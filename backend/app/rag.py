from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text as sqltext
from .models import Document, Chunk
from .config import settings
import google.generativeai as genai

EMBED_DIM = 3072  # Gemini text-embedding-004

genai.configure(api_key=settings.GOOGLE_API_KEY)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _embed(content: str) -> List[float]:
    resp = genai.embed_content(model="text-embedding-004", content=content)
    return resp["embedding"]


def upsert_document_chunks(db: Session, doc: Document, text: str):
    chunks = chunk_text(text)
    if not chunks:
        return 0
    vectors = [_embed(ch) for ch in chunks]
    for idx, (ch, vec) in enumerate(zip(chunks, vectors)):
        c = Chunk(document_id=doc.id, text=ch, page=None, offset=idx * 800)
        db.add(c)
        db.flush()
        db.execute(sqltext("UPDATE chunks SET embedding = :vec WHERE id = :id"), {"vec": vec, "id": c.id})
    db.commit()
    return len(chunks)


def pgvector_search(db: Session, query_vec: List[float], top_k: int = 3) -> List[Tuple[Chunk, float]]:
    sql = """
    SELECT id, 1 - (embedding <=> :q) AS score
    FROM chunks
    ORDER BY embedding <=> :q
    LIMIT :k
    """
    rows = db.execute(sqltext(sql), {"q": query_vec, "k": top_k}).fetchall()
    if not rows:
        return []
    results: List[Tuple[Chunk, float]] = []
    for row in rows:
        chunk = db.query(Chunk).filter(Chunk.id == row[0]).first()
        if chunk is not None:
            results.append((chunk, float(row[1])))
    return results


def embed_query(question: str) -> List[float]:
    return _embed(question)


def answer_with_citations(question: str, hits: List[Tuple[Chunk, float]]) -> Tuple[str, str]:
    context = "\n\n".join([h[0].text for h in hits]) or "No context"
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = (
        "Answer the legal question using the context.\n\n"
        f"Question:\n{question}\n\nContext:\n{context}\n\n"
        "Include brief citations from the snippets."
    )
    out = model.generate_content(prompt)
    answer = getattr(out, "text", None) or "No answer."
    avg = sum([h[1] for h in hits]) / max(1, len(hits))
    confidence = "high" if avg > 0.8 else "medium" if avg > 0.6 else "low"
    return answer, confidence