from pydantic import BaseModel, EmailStr
from typing import List, Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "lawyer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class IngestResponse(BaseModel):
    ingested_chunks: int


class SourceItem(BaseModel):
    document_id: int
    title: str
    snippet: str
    page: Optional[int] = None
    offset: Optional[int] = None


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    confidence: str