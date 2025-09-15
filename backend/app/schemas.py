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


class ClauseAnalysis(BaseModel):
    clause_text: str
    clause_type: str  # e.g., "termination", "payment", "liability", "confidentiality"
    safety_level: str  # "safe", "warning", "dangerous"
    explanation: str
    recommendations: Optional[str] = None
    page_number: Optional[int] = None
    line_number: Optional[int] = None


class DocumentAnalysisResponse(BaseModel):
    document_id: int
    document_title: str
    analysis_status: str  # "completed", "processing", "failed"
    total_clauses: int
    safe_clauses: int
    warning_clauses: int
    dangerous_clauses: int
    clauses: List[ClauseAnalysis]
    summary: str
    overall_risk_level: str  # "low", "medium", "high"
    processing_time: Optional[float] = None
    error_message: Optional[str] = None


class DocumentAnalysisRequest(BaseModel):
    document_id: int
    analysis_type: str = "comprehensive"  # "comprehensive", "quick", "specific"
    focus_areas: Optional[List[str]] = None  # e.g., ["payment", "termination", "liability"]


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    is_active: bool
    message_count: int


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    message_type: str
    message_metadata: Optional[str] = None
    created_at: str


class ChatSessionDetailResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    is_active: bool
    messages: List[ChatMessageResponse]


class CreateChatSessionRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    message: str
    message_type: str = "text"


class SendMessageResponse(BaseModel):
    message: ChatMessageResponse
    session: ChatSessionResponse


class LegalCaseResponse(BaseModel):
    id: int
    case_id: str
    title: str
    court: str
    jurisdiction: str
    case_date: Optional[str] = None
    case_type: str
    summary: str
    citation: str
    source: str
    relevance_score: Optional[float] = None


class LegalStatuteResponse(BaseModel):
    id: int
    statute_id: str
    title: str
    jurisdiction: str
    section_number: Optional[str] = None
    summary: str
    effective_date: Optional[str] = None
    source: str
    relevance_score: Optional[float] = None


class LegalResearchResponse(BaseModel):
    query: str
    cases: List[LegalCaseResponse]
    statutes: List[LegalStatuteResponse]
    total_results: int
    search_time: float


class HybridQueryRequest(BaseModel):
    session_id: int
    query: str
    include_documents: bool = True
    include_legal_db: bool = True
    max_results: int = 10


class DocumentAnalysisRequest(BaseModel):
    document_id: int
    analysis_type: str = "comprehensive"
    focus_areas: Optional[List[str]] = None


class ClauseAnalysis(BaseModel):
    clause_text: str
    clause_type: str
    safety_level: str  # 'safe', 'warning', 'dangerous'
    explanation: str
    recommendations: Optional[str] = None
    page_number: Optional[int] = None
    line_number: Optional[int] = None


class DocumentAnalysisResponse(BaseModel):
    document_id: int
    document_title: str
    analysis_status: str  # 'completed', 'processing', 'failed'
    total_clauses: int
    safe_clauses: int
    warning_clauses: int
    dangerous_clauses: int
    clauses: List[ClauseAnalysis]
    summary: str
    overall_risk_level: str  # 'low', 'medium', 'high'
    processing_time: Optional[float] = None
    error_message: Optional[str] = None


class SavedDocumentAnalysis(BaseModel):
    id: int
    document_id: int
    analysis_type: str
    analysis_status: str
    total_clauses: int
    safe_clauses: int
    warning_clauses: int
    dangerous_clauses: int
    overall_risk_level: str
    summary: str
    created_at: str
    updated_at: str