from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
import os
import google.generativeai as genai
from .config import settings
from .database import Base, engine, get_db
from .models import User, Document, QueryLog
from .schemas import *
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .ingest import extract_text_from_pdf, extract_text_from_image
from .rag import upsert_document_chunks, embed_query, pgvector_search, answer_with_citations

# Configure Google Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

app = FastAPI(title="Law GPT Backend", version="0.1.0")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

# Create tables and storage dir
Base.metadata.create_all(bind=engine)
os.makedirs(settings.STORAGE_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=req.email, password_hash=hash_password(req.password), role=req.role)
    db.add(user)
    db.commit()
    token = create_access_token(sub=user.email, role=user.role)
    return TokenResponse(access_token=token)


@app.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=user.email, role=user.role)
    return TokenResponse(access_token=token)


@app.post("/upload")
def upload_document(
    background: BackgroundTasks,
    title: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dest_dir = os.path.join(settings.STORAGE_DIR, str(user.id))
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)
    with open(dest_path, "wb") as f:
        f.write(file.file.read())
    doc = Document(user_id=user.id, title=title, path=dest_path, content_type=file.content_type or "application/octet-stream")
    db.add(doc)
    db.commit()
    return {"document_id": doc.id, "title": doc.title}


@app.post("/ingest", response_model=IngestResponse)
def ingest(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == user.id).all()
    total = 0
    for doc in docs:
        text = ""
        if (doc.content_type or "").lower().startswith("application/pdf") or doc.path.lower().endswith(".pdf"):
            text = extract_text_from_pdf(doc.path)
        elif doc.path.lower().endswith((".png", ".jpg", ".jpeg")):
            text = extract_text_from_image(doc.path)
        else:
            try:
                with open(doc.path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                text = ""
        total += upsert_document_chunks(db, doc, text)
    return IngestResponse(ingested_chunks=total)


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    qvec = embed_query(req.question)
    hits = pgvector_search(db, qvec, top_k=req.top_k)
    answer, confidence = answer_with_citations(req.question, hits)
    sources = []
    doc_ids = []
    for chunk, score in hits:
        doc = chunk.document
        doc_ids.append(str(doc.id))
        snippet = (chunk.text[:240] + "...") if len(chunk.text) > 240 else chunk.text
        sources.append(SourceItem(document_id=doc.id, title=doc.title, snippet=snippet, page=chunk.page, offset=chunk.offset))
    log = QueryLog(user_id=user.id, question=req.question, doc_ids=",".join(doc_ids))
    db.add(log)
    db.commit()
    return QueryResponse(answer=answer, sources=sources, confidence=confidence)


@app.post("/fine-tune")
def fine_tune_endpoint():
    return {"status": "scheduled", "note": "Use scripts in app/fine_tune to prepare/train/serve LoRA models."}


@app.post("/gemini-query", response_model=QueryResponse)
def gemini_query(req: QueryRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Direct query to Google Gemini API for legal questions without RAG"""
    try:
        # Log the query
        log = QueryLog(user_id=user.id, question=req.question, doc_ids="")
        db.add(log)
        db.commit()
        
        # Create the prompt for legal questions
        prompt = (
            "You are LawGPT, a specialized legal assistant. Answer the following legal question "
            "with accurate information. If you're unsure, indicate the limitations of your knowledge. "
            f"Question: {req.question}"
        )
        
        # Call Gemini API
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        answer = getattr(response, "text", None) or "Sorry, I couldn't generate a response."
        
        return QueryResponse(
            answer=answer,
            sources=[],  # No sources for direct Gemini queries
            confidence="medium"  # Default confidence level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Gemini API: {str(e)}")