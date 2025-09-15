from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import google.generativeai as genai
from .config import settings
from .database import Base, engine, get_db
from .models import User, Document, QueryLog, DocumentAnalysis
from .schemas import *
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .ingest import extract_text_from_pdf, extract_text_from_image
from .rag import upsert_document_chunks, embed_query, pgvector_search, answer_with_citations
from .document_analyzer import DocumentAnalyzer
from .chat_service import ChatService
from .legal_database import LegalDatabaseService
from .indian_legal_database import IndianLegalDatabaseService
from .document_risk_analyzer import document_risk_analyzer
from .simple_vector_similarity import simple_vector_similarity_service

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
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong password. Please try again")
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


@app.post("/analyze-document", response_model=DocumentAnalysisResponse)
def analyze_document(
    req: DocumentAnalysisRequest, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Analyze a document for legal clauses and safety assessment"""
    try:
        # Get the document
        document = db.query(Document).filter(
            Document.id == req.document_id,
            Document.user_id == user.id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if analysis already exists
        existing_analysis = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == req.document_id,
            DocumentAnalysis.user_id == user.id,
            DocumentAnalysis.analysis_type == req.analysis_type
        ).first()
        
        if existing_analysis:
            # Return existing analysis
            analysis_data = json.loads(existing_analysis.analysis_data)
            return DocumentAnalysisResponse(
                document_id=document.id,
                document_title=document.title,
                analysis_status=existing_analysis.analysis_status,
                total_clauses=existing_analysis.total_clauses,
                safe_clauses=existing_analysis.safe_clauses,
                warning_clauses=existing_analysis.warning_clauses,
                dangerous_clauses=existing_analysis.dangerous_clauses,
                clauses=analysis_data.get('clauses', []),
                summary=existing_analysis.summary,
                overall_risk_level=existing_analysis.overall_risk_level,
                processing_time=existing_analysis.processing_time,
                error_message=existing_analysis.error_message
            )
        
        # Initialize analyzer and perform analysis
        analyzer = DocumentAnalyzer()
        analysis = analyzer.analyze_document(
            document, 
            analysis_type=req.analysis_type,
            focus_areas=req.focus_areas
        )
        
        # Save analysis to database
        import json
        analysis_record = DocumentAnalysis(
            document_id=document.id,
            user_id=user.id,
            analysis_type=req.analysis_type,
            analysis_status=analysis.analysis_status,
            total_clauses=analysis.total_clauses,
            safe_clauses=analysis.safe_clauses,
            warning_clauses=analysis.warning_clauses,
            dangerous_clauses=analysis.dangerous_clauses,
            overall_risk_level=analysis.overall_risk_level,
            summary=analysis.summary,
            analysis_data=json.dumps({
                'clauses': [clause.dict() for clause in analysis.clauses]
            }),
            processing_time=analysis.processing_time,
            error_message=analysis.error_message
        )
        
        db.add(analysis_record)
        db.commit()
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")


@app.get("/documents", response_model=List[dict])
def get_user_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all documents for the current user"""
    documents = db.query(Document).filter(Document.user_id == user.id).all()
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "content_type": doc.content_type,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        }
        for doc in documents
    ]


@app.get("/document-analyses", response_model=List[SavedDocumentAnalysis])
def get_user_document_analyses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all document analyses for the current user"""
    analyses = db.query(DocumentAnalysis).filter(DocumentAnalysis.user_id == user.id).order_by(DocumentAnalysis.created_at.desc()).all()
    return [
        SavedDocumentAnalysis(
            id=analysis.id,
            document_id=analysis.document_id,
            analysis_type=analysis.analysis_type,
            analysis_status=analysis.analysis_status,
            total_clauses=analysis.total_clauses,
            safe_clauses=analysis.safe_clauses,
            warning_clauses=analysis.warning_clauses,
            dangerous_clauses=analysis.dangerous_clauses,
            overall_risk_level=analysis.overall_risk_level,
            summary=analysis.summary,
            created_at=analysis.created_at.isoformat() if analysis.created_at else None,
            updated_at=analysis.updated_at.isoformat() if analysis.updated_at else None
        )
        for analysis in analyses
    ]


@app.get("/document-analyses/{analysis_id}", response_model=DocumentAnalysisResponse)
def get_document_analysis(
    analysis_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document analysis by ID"""
    analysis = db.query(DocumentAnalysis).filter(
        DocumentAnalysis.id == analysis_id,
        DocumentAnalysis.user_id == user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get document title
    document = db.query(Document).filter(Document.id == analysis.document_id).first()
    document_title = document.title if document else "Unknown Document"
    
    # Parse analysis data
    import json
    analysis_data = json.loads(analysis.analysis_data)
    
    return DocumentAnalysisResponse(
        document_id=analysis.document_id,
        document_title=document_title,
        analysis_status=analysis.analysis_status,
        total_clauses=analysis.total_clauses,
        safe_clauses=analysis.safe_clauses,
        warning_clauses=analysis.warning_clauses,
        dangerous_clauses=analysis.dangerous_clauses,
        clauses=[ClauseAnalysis(**clause) for clause in analysis_data.get('clauses', [])],
        summary=analysis.summary,
        overall_risk_level=analysis.overall_risk_level,
        processing_time=analysis.processing_time,
        error_message=analysis.error_message
    )


@app.get("/me", response_model=dict)
def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "name": getattr(user, 'name', user.email.split('@')[0].title())  # Use email prefix as name if no name field
    }


# Chat Session Endpoints
@app.post("/chat/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    req: CreateChatSessionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    chat_service = ChatService()
    return chat_service.create_chat_session(db, user.id, req.title)


@app.get("/chat/sessions", response_model=List[ChatSessionResponse])
def get_chat_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all chat sessions for the current user"""
    chat_service = ChatService()
    return chat_service.get_user_chat_sessions(db, user.id)


@app.get("/chat/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_chat_session_detail(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed chat session with messages"""
    chat_service = ChatService()
    session = chat_service.get_chat_session_detail(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@app.post("/chat/sessions/{session_id}/messages", response_model=SendMessageResponse)
def send_message(
    session_id: int,
    req: SendMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a chat session"""
    chat_service = ChatService()
    req.session_id = session_id  # Ensure session_id matches the URL parameter
    response = chat_service.send_message(db, user.id, req)
    if not response:
        raise HTTPException(status_code=404, detail="Chat session not found or error processing message")
    return response


@app.delete("/chat/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    chat_service = ChatService()
    success = chat_service.delete_chat_session(db, session_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"message": "Chat session deleted successfully"}


@app.put("/chat/sessions/{session_id}/rename")
def rename_chat_session(
    session_id: int,
    req: CreateChatSessionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rename a chat session"""
    chat_service = ChatService()
    success = chat_service.rename_chat_session(db, session_id, user.id, req.title)
    if not success:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"message": "Chat session renamed successfully"}


# Legal Database Endpoints
@app.post("/legal-research", response_model=LegalResearchResponse)
def legal_research(
    req: QueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search legal databases for cases and statutes"""
    try:
        legal_service = LegalDatabaseService()
        
        # Search for cases and statutes
        cases = legal_service.search_legal_cases(req.question, max_results=5)
        statutes = legal_service.search_legal_statutes(req.question, max_results=5)
        
        # Save to database for future reference
        legal_service.save_legal_data_to_db(db, cases, statutes)
        
        return LegalResearchResponse(
            query=req.question,
            cases=cases,
            statutes=statutes,
            total_results=len(cases) + len(statutes),
            search_time=0.0  # Would be calculated in real implementation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in legal research: {str(e)}")


@app.post("/hybrid-query", response_model=QueryResponse)
def hybrid_query(
    req: HybridQueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hybrid query combining document search and legal database search"""
    try:
        chat_service = ChatService()
        
        # Create a temporary message request
        message_req = SendMessageRequest(
            session_id=req.session_id,
            message=req.query,
            message_type="hybrid"
        )
        
        # Get response using chat service
        response = chat_service.send_message(db, user.id, message_req)
        
        if not response:
            raise HTTPException(status_code=500, detail="Error processing hybrid query")
        
        # Convert to QueryResponse format
        return QueryResponse(
            answer=response.message.content,
            sources=[],  # Sources would be extracted from metadata
            confidence="medium"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in hybrid query: {str(e)}")


# Indian Legal Database Endpoints
@app.post("/indian-legal-research", response_model=LegalResearchResponse)
def indian_legal_research(
    req: QueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search Indian legal databases for cases and statutes"""
    try:
        indian_legal_service = IndianLegalDatabaseService()
        
        # Search for Indian cases and statutes
        cases = indian_legal_service.search_indian_cases(req.question, max_results=5)
        statutes = indian_legal_service.search_indian_statutes(req.question, max_results=5)
        
        # Save to database for future reference
        indian_legal_service.save_indian_legal_data_to_db(db, cases, statutes)
        
        return LegalResearchResponse(
            query=req.question,
            cases=cases,
            statutes=statutes,
            total_results=len(cases) + len(statutes),
            search_time=0.0  # Would be calculated in real implementation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Indian legal research: {str(e)}")


@app.get("/indian-legal/courts")
def get_indian_courts():
    """Get list of available Indian courts"""
    indian_legal_service = IndianLegalDatabaseService()
    return indian_legal_service.get_available_courts()


@app.get("/indian-legal/jurisdictions")
def get_indian_jurisdictions():
    """Get list of available Indian jurisdictions"""
    indian_legal_service = IndianLegalDatabaseService()
    return indian_legal_service.get_available_jurisdictions()


@app.post("/indian-legal/cases/search")
def search_indian_cases(
    query: str = Form(...),
    court: str = Form("all"),
    max_results: int = Form(10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search specifically for Indian legal cases"""
    try:
        indian_legal_service = IndianLegalDatabaseService()
        cases = indian_legal_service.search_indian_cases(query, court, max_results)
        
        # Save to database
        indian_legal_service.save_indian_legal_data_to_db(db, cases, [])
        
        return {
            "query": query,
            "court": court,
            "cases": cases,
            "total_results": len(cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching Indian cases: {str(e)}")


@app.post("/indian-legal/statutes/search")
def search_indian_statutes(
    query: str = Form(...),
    jurisdiction: str = Form("all"),
    max_results: int = Form(10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search specifically for Indian legal statutes"""
    try:
        indian_legal_service = IndianLegalDatabaseService()
        statutes = indian_legal_service.search_indian_statutes(query, jurisdiction, max_results)
        
        # Save to database
        indian_legal_service.save_indian_legal_data_to_db(db, [], statutes)
        
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "statutes": statutes,
            "total_results": len(statutes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching Indian statutes: {str(e)}")


@app.post("/indian-legal/cases/search-specific")
def search_specific_case(
    case_name: str = Form(...),
    case_details: str = Form(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for a specific case by name and details"""
    try:
        indian_legal_service = IndianLegalDatabaseService()
        cases = indian_legal_service.search_specific_case(case_name, case_details)
        
        return {
            "case_name": case_name,
            "case_details": case_details,
            "cases": cases,
            "total_results": len(cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching specific case: {str(e)}")


@app.post("/indian-legal/cases/find-similar")
def find_similar_cases(
    case_text: str = Form(...),
    case_type: str = Form("civil"),
    max_results: int = Form(10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find similar cases based on case text content"""
    try:
        indian_legal_service = IndianLegalDatabaseService()
        cases = indian_legal_service.find_similar_cases(case_text, case_type, max_results)
        
        return {
            "case_type": case_type,
            "search_text": case_text[:100] + "..." if len(case_text) > 100 else case_text,
            "cases": cases,
            "total_results": len(cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cases: {str(e)}")


@app.post("/indian-legal/cases/analyze-document")
def analyze_case_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze uploaded case document and find similar cases"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Read file content
        content = file.file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            from .ingest import extract_text_from_pdf
            case_text = extract_text_from_pdf(content)
        elif file.filename.lower().endswith(('.txt', '.doc', '.docx')):
            case_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, TXT, DOC, or DOCX files.")
        
        if not case_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file")
        
        # Find similar cases
        indian_legal_service = IndianLegalDatabaseService()
        similar_cases = indian_legal_service.find_similar_cases(case_text, "civil", 10)
        
        # Extract key legal concepts
        legal_concepts = indian_legal_service._extract_legal_concepts(case_text)
        
        return {
            "similar_cases": similar_cases,
            "total_results": len(similar_cases),
            "legal_concepts": legal_concepts,
            "document_analysis": {
                "filename": file.filename,
                "text_length": len(case_text),
                "extracted_text_preview": case_text[:500] + "..." if len(case_text) > 500 else case_text
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing case document: {str(e)}")


@app.post("/analyze-document-risks")
def analyze_document_risks(
    file: UploadFile = File(...),
    document_type: str = Form("general"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze document for risky clauses and provide detailed risk assessment for common citizens"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Read file content
        content = file.file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            from .ingest import extract_text_from_pdf
            document_text = extract_text_from_pdf(content)
        elif file.filename.lower().endswith(('.txt', '.doc', '.docx')):
            document_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, TXT, DOC, or DOCX files.")
        
        if not document_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file")
        
        # Analyze document risks
        risk_analysis = document_risk_analyzer.analyze_specific_document_type(document_text, document_type)
        
        # Add document metadata
        risk_analysis["document_metadata"] = {
            "filename": file.filename,
            "file_size": len(content),
            "text_length": len(document_text),
            "document_type": document_type,
            "analyzed_at": "2024-01-01T00:00:00Z"  # You can use datetime.now().isoformat()
        }
        
        return risk_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing document risks: {str(e)}")


@app.post("/find-similar-cases-vector")
def find_similar_cases_vector(
    case_text: str = Form(...),
    max_results: int = Form(10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find similar cases using FAISS vector similarity"""
    try:
        # Use simple similarity to find similar cases
        similar_cases = simple_vector_similarity_service.find_similar_cases(case_text, max_results)
        
        return {
            "similar_cases": similar_cases,
            "total_results": len(similar_cases),
            "search_text": case_text[:100] + "..." if len(case_text) > 100 else case_text,
            "method": "FAISS_VECTOR_SIMILARITY"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cases: {str(e)}")


@app.post("/add-cases-to-vector-index")
def add_cases_to_vector_index(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add existing cases to FAISS vector index for similarity search"""
    try:
        # Get all cases from database
        cases = db.query(LegalCase).all()
        
        if not cases:
            return {"message": "No cases found in database", "added_count": 0}
        
        # Convert to LegalCaseResponse format
        case_responses = []
        for case in cases:
            case_response = LegalCaseResponse(
                id=case.id,
                case_id=case.case_id,
                title=case.title,
                court=case.court,
                jurisdiction=case.jurisdiction,
                case_date=case.case_date,
                case_type=case.case_type,
                summary=case.summary,
                citation=case.citation,
                source=case.source,
                relevance_score=case.relevance_score
            )
            case_responses.append(case_response)
        
        # Add to similarity index
        simple_vector_similarity_service.add_cases_to_index(case_responses)
        
        return {
            "message": f"Successfully added {len(case_responses)} cases to vector index",
            "added_count": len(case_responses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding cases to vector index: {str(e)}")