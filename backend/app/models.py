from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="lawyer")  # lawyer | admin
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1024))
    content_type: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Vector] = mapped_column(Vector(3072))
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    document = relationship("Document")


class QueryLog(Base):
    __tablename__ = "query_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    question: Mapped[str] = mapped_column(Text)
    doc_ids: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id"))
    role: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(String(50), default="text")  # 'text', 'document_analysis', 'legal_research'
    message_metadata: Mapped[Optional[str]] = mapped_column(Text)  # JSON string for additional data
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    session = relationship("ChatSession", back_populates="messages")


class LegalCase(Base):
    __tablename__ = "legal_cases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    court: Mapped[str] = mapped_column(String(200))
    jurisdiction: Mapped[str] = mapped_column(String(100))
    case_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    case_type: Mapped[str] = mapped_column(String(100))
    summary: Mapped[str] = mapped_column(Text)
    full_text: Mapped[str] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text)  # comma-separated keywords
    citation: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(100))  # e.g., 'canlii', 'bailii', 'pacer'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LegalStatute(Base):
    __tablename__ = "legal_statutes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    statute_id: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    jurisdiction: Mapped[str] = mapped_column(String(100))
    section_number: Mapped[Optional[str]] = mapped_column(String(50))
    statute_text: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text)
    effective_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    analysis_type: Mapped[str] = mapped_column(String(50), default="comprehensive")
    analysis_status: Mapped[str] = mapped_column(String(20), default="completed")  # 'completed', 'processing', 'failed'
    total_clauses: Mapped[int] = mapped_column(Integer, default=0)
    safe_clauses: Mapped[int] = mapped_column(Integer, default=0)
    warning_clauses: Mapped[int] = mapped_column(Integer, default=0)
    dangerous_clauses: Mapped[int] = mapped_column(Integer, default=0)
    overall_risk_level: Mapped[str] = mapped_column(String(20), default="low")  # 'low', 'medium', 'high'
    summary: Mapped[str] = mapped_column(Text)
    analysis_data: Mapped[str] = mapped_column(Text)  # JSON string containing full analysis results
    processing_time: Mapped[Optional[float]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    document = relationship("Document")
    user = relationship("User")