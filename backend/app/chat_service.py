import json
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text as sqltext
from .models import ChatSession, ChatMessage, User, Document, Chunk
from .schemas import (
    ChatSessionResponse, ChatMessageResponse, ChatSessionDetailResponse,
    CreateChatSessionRequest, SendMessageRequest, SendMessageResponse
)
from .rag import embed_query, pgvector_search, answer_with_citations
from .legal_database import LegalDatabaseService
from .indian_legal_database import IndianLegalDatabaseService
from .document_analyzer import DocumentAnalyzer
import google.generativeai as genai
from .config import settings

# Configure Google Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)


class ChatService:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.legal_db_service = LegalDatabaseService()
        self.indian_legal_db_service = IndianLegalDatabaseService()
        self.document_analyzer = DocumentAnalyzer()

    def create_chat_session(self, db: Session, user_id: int, title: str) -> ChatSessionResponse:
        """Create a new chat session"""
        try:
            session = ChatSession(
                user_id=user_id,
                title=title,
                is_active=True
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return ChatSessionResponse(
                id=session.id,
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                is_active=session.is_active,
                message_count=0
            )
        except Exception as e:
            print(f"Error creating chat session: {e}")
            db.rollback()
            raise

    def get_user_chat_sessions(self, db: Session, user_id: int) -> List[ChatSessionResponse]:
        """Get all chat sessions for a user"""
        try:
            sessions = db.query(ChatSession).filter(
                ChatSession.user_id == user_id,
                ChatSession.is_active == True
            ).order_by(ChatSession.updated_at.desc()).all()
            
            return [
                ChatSessionResponse(
                    id=session.id,
                    title=session.title,
                    created_at=session.created_at.isoformat(),
                    updated_at=session.updated_at.isoformat(),
                    is_active=session.is_active,
                    message_count=len(session.messages)
                )
                for session in sessions
            ]
        except Exception as e:
            print(f"Error getting chat sessions: {e}")
            return []

    def get_chat_session_detail(self, db: Session, session_id: int, user_id: int) -> Optional[ChatSessionDetailResponse]:
        """Get detailed chat session with messages"""
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
                ChatSession.is_active == True
            ).first()
            
            if not session:
                return None
            
            messages = [
                ChatMessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    message_type=msg.message_type,
                    message_metadata=msg.message_metadata,
                    created_at=msg.created_at.isoformat()
                )
                for msg in sorted(session.messages, key=lambda x: x.created_at)
            ]
            
            return ChatSessionDetailResponse(
                id=session.id,
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                is_active=session.is_active,
                messages=messages
            )
        except Exception as e:
            print(f"Error getting chat session detail: {e}")
            return None

    def send_message(self, db: Session, user_id: int, request: SendMessageRequest) -> Optional[SendMessageResponse]:
        """Send a message and get AI response"""
        try:
            # Get the chat session
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == user_id,
                ChatSession.is_active == True
            ).first()
            
            if not session:
                return None
            
            # Save user message
            user_message = ChatMessage(
                session_id=session.id,
                role="user",
                content=request.message,
                message_type=request.message_type
            )
            db.add(user_message)
            db.commit()
            
            # Generate AI response
            ai_response = self._generate_ai_response(db, user_id, request.message, session.id)
            
            # Save AI response
            ai_message = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=ai_response["content"],
                message_type=ai_response["message_type"],
                message_metadata=json.dumps(ai_response.get("metadata", {}))
            )
            db.add(ai_message)
            
            # Update session timestamp
            session.updated_at = time.time()
            
            db.commit()
            db.refresh(ai_message)
            db.refresh(session)
            
            return SendMessageResponse(
                message=ChatMessageResponse(
                    id=ai_message.id,
                    role=ai_message.role,
                    content=ai_message.content,
                    message_type=ai_message.message_type,
                    message_metadata=ai_message.message_metadata,
                    created_at=ai_message.created_at.isoformat()
                ),
                session=ChatSessionResponse(
                    id=session.id,
                    title=session.title,
                    created_at=session.created_at.isoformat(),
                    updated_at=session.updated_at.isoformat(),
                    is_active=session.is_active,
                    message_count=len(session.messages) + 1
                )
            )
        except Exception as e:
            print(f"Error sending message: {e}")
            db.rollback()
            return None

    def _generate_ai_response(self, db: Session, user_id: int, message: str, session_id: int) -> Dict[str, Any]:
        """Generate AI response based on message type and context"""
        try:
            # Determine if this is a legal research query
            legal_keywords = [
                "case law", "precedent", "statute", "legislation", "court decision",
                "legal precedent", "jurisdiction", "ruling", "judgment", "legal case"
            ]
            
            is_legal_research = any(keyword in message.lower() for keyword in legal_keywords)
            
            if is_legal_research:
                return self._generate_legal_research_response(db, user_id, message)
            else:
                return self._generate_hybrid_response(db, user_id, message, session_id)
        
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return {
                "content": "I apologize, but I encountered an error while processing your request. Please try again.",
                "message_type": "text",
                "metadata": {"error": str(e)}
            }

    def _generate_legal_research_response(self, db: Session, user_id: int, message: str) -> Dict[str, Any]:
        """Generate response for legal research queries"""
        try:
            # Check if this is a specific case search query
            case_search_patterns = [
                'case name', 'case of', 'vs', 'v.', 'versus', 'judgment of', 'ruling in',
                'find case', 'search case', 'look up case', 'case details', 'case information'
            ]
            
            is_case_search = any(pattern in message.lower() for pattern in case_search_patterns)
            
            if is_case_search:
                return self._handle_case_search_query(db, user_id, message)
            
            # Determine if this is an Indian law query
            indian_keywords = [
                "india", "indian", "supreme court of india", "high court", "district court",
                "indian penal code", "indian contract act", "constitution of india",
                "crpc", "cpc", "evidence act", "companies act", "consumer protection"
            ]
            
            is_indian_law_query = any(keyword in message.lower() for keyword in indian_keywords)
            
            if is_indian_law_query:
                # Search Indian legal databases
                cases = self.indian_legal_db_service.search_indian_cases(message, max_results=5)
                statutes = self.indian_legal_db_service.search_indian_statutes(message, max_results=5)
                
                # Search local Indian database
                local_cases = self.indian_legal_db_service.search_database_indian_cases(db, message, max_results=3)
                local_statutes = self.indian_legal_db_service.search_database_indian_statutes(db, message, max_results=3)
            else:
                # Search international legal databases
                cases = self.legal_db_service.search_legal_cases(message, max_results=5)
                statutes = self.legal_db_service.search_legal_statutes(message, max_results=5)
                
                # Search local database
                local_cases = self.legal_db_service.search_database_cases(db, message, max_results=3)
                local_statutes = self.legal_db_service.search_database_statutes(db, message, max_results=3)
            
            # Combine results
            all_cases = cases + local_cases
            all_statutes = statutes + local_statutes
            
            # Generate response using AI
            context = self._build_legal_context(all_cases, all_statutes)
            
            if is_indian_law_query:
                prompt = f"""
                You are a specialized Indian legal research assistant. Based on the following Indian legal information, provide a comprehensive response to the user's query: "{message}"
                
                Indian Legal Context:
                {context}
                
                Please provide:
                1. A direct answer to the query under Indian law
                2. Relevant Indian case law and precedents
                3. Applicable Indian statutes and legislation
                4. Key legal principles under Indian law
                5. Practical implications in the Indian legal system
                6. References to relevant sections of Indian laws
                
                Format your response in a clear, professional manner suitable for Indian legal research.
                Include proper citations to Indian cases and statutes.
                """
            else:
                prompt = f"""
                You are a legal research assistant. Based on the following legal information, provide a comprehensive response to the user's query: "{message}"
                
                Legal Context:
                {context}
                
                Please provide:
                1. A direct answer to the query
                2. Relevant case law and precedents
                3. Applicable statutes and legislation
                4. Key legal principles
                5. Practical implications
                
                Format your response in a clear, professional manner suitable for legal research.
                """
            
            response = self.model.generate_content(prompt)
            content = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "content": content,
                "message_type": "legal_research",
                "metadata": {
                    "cases_found": len(all_cases),
                    "statutes_found": len(all_statutes),
                    "sources": list(set([case.source for case in all_cases] + [statute.source for statute in all_statutes])),
                    "is_indian_law": is_indian_law_query,
                    "jurisdiction": "India" if is_indian_law_query else "International"
                }
            }
        
        except Exception as e:
            print(f"Error in legal research response: {e}")
            return {
                "content": f"I encountered an error while researching legal information: {str(e)}",
                "message_type": "legal_research",
                "metadata": {"error": str(e)}
            }

    def _generate_hybrid_response(self, db: Session, user_id: int, message: str, session_id: int) -> Dict[str, Any]:
        """Generate hybrid response using both documents and legal databases"""
        try:
            # Search user's documents
            doc_results = []
            try:
                qvec = embed_query(message)
                hits = pgvector_search(db, qvec, top_k=3)
                doc_results = [(chunk.text, score) for chunk, score in hits]
            except Exception as e:
                print(f"Error searching documents: {e}")
            
            # Search legal databases
            legal_cases = self.legal_db_service.search_legal_cases(message, max_results=3)
            legal_statutes = self.legal_db_service.search_legal_statutes(message, max_results=3)
            
            # Build context
            context_parts = []
            
            if doc_results:
                context_parts.append("User Documents:")
                for text, score in doc_results:
                    context_parts.append(f"- {text[:200]}... (relevance: {score:.2f})")
            
            if legal_cases:
                context_parts.append("\nRelevant Case Law:")
                for case in legal_cases:
                    context_parts.append(f"- {case.title} ({case.citation})")
                    context_parts.append(f"  {case.summary[:150]}...")
            
            if legal_statutes:
                context_parts.append("\nRelevant Legislation:")
                for statute in legal_statutes:
                    context_parts.append(f"- {statute.title}")
                    context_parts.append(f"  {statute.summary[:150]}...")
            
            context = "\n".join(context_parts)
            
            # Generate response
            prompt = f"""
            You are LawGPT, a specialized legal assistant. Answer the following question using the provided context from both user documents and legal databases.
            
            Question: {message}
            
            Context:
            {context}
            
            Provide a comprehensive answer that:
            1. Directly addresses the user's question
            2. References relevant information from their documents
            3. Cites applicable case law and legislation when relevant
            4. Offers practical legal guidance
            5. Indicates when you're uncertain or when professional legal advice is needed
            
            Be thorough but concise, and always remind the user that this is not a substitute for professional legal advice.
            """
            
            response = self.model.generate_content(prompt)
            content = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "content": content,
                "message_type": "hybrid",
                "metadata": {
                    "documents_searched": len(doc_results),
                    "cases_found": len(legal_cases),
                    "statutes_found": len(legal_statutes),
                    "sources": list(set([case.source for case in legal_cases] + [statute.source for statute in legal_statutes]))
                }
            }
        
        except Exception as e:
            print(f"Error in hybrid response: {e}")
            return {
                "content": f"I encountered an error while processing your request: {str(e)}",
                "message_type": "hybrid",
                "metadata": {"error": str(e)}
            }

    def _build_legal_context(self, cases: List, statutes: List) -> str:
        """Build context string from legal cases and statutes"""
        context_parts = []
        
        if cases:
            context_parts.append("RELEVANT CASE LAW:")
            for case in cases:
                context_parts.append(f"• {case.title} ({case.citation})")
                context_parts.append(f"  Court: {case.court}, {case.jurisdiction}")
                context_parts.append(f"  Summary: {case.summary}")
                context_parts.append("")
        
        if statutes:
            context_parts.append("RELEVANT LEGISLATION:")
            for statute in statutes:
                context_parts.append(f"• {statute.title}")
                if statute.section_number:
                    context_parts.append(f"  Section: {statute.section_number}")
                context_parts.append(f"  Jurisdiction: {statute.jurisdiction}")
                context_parts.append(f"  Summary: {statute.summary}")
                context_parts.append("")
        
        return "\n".join(context_parts)

    def delete_chat_session(self, db: Session, session_id: int, user_id: int) -> bool:
        """Delete a chat session (soft delete)"""
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                return False
            
            session.is_active = False
            db.commit()
            return True
        
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            db.rollback()
            return False

    def rename_chat_session(self, db: Session, session_id: int, user_id: int, new_title: str) -> bool:
        """Rename a chat session"""
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                return False
            
            session.title = new_title
            db.commit()
            return True
        
        except Exception as e:
            print(f"Error renaming chat session: {e}")
            db.rollback()
            return False

    def _handle_case_search_query(self, db: Session, user_id: int, message: str) -> Dict[str, Any]:
        """Handle specific case search queries"""
        try:
            # Extract case name from query using AI
            prompt = f"""
            Extract the case name from this legal query: "{message}"
            
            Look for patterns like:
            - "case of [Name]"
            - "[Name] vs [Name]"
            - "[Name] v. [Name]"
            - "find case [Name]"
            - "search for [Name]"
            
            Return only the case name or names, separated by comma if multiple.
            If no clear case name is found, return "NO_CASE_NAME_FOUND"
            """
            
            response = self.model.generate_content(prompt)
            case_name = response.text.strip()
            
            if case_name == "NO_CASE_NAME_FOUND":
                return {
                    "content": "I couldn't identify a specific case name in your query. Please provide the case name more clearly, for example: 'Find case of Kesavananda Bharati' or 'Search for Kesavananda Bharati vs State of Kerala'.",
                    "message_type": "text",
                    "metadata": {"is_case_search": True, "case_found": False}
                }
            
            # Search for the specific case
            cases = self.indian_legal_db_service.search_specific_case(case_name, message)
            
            if not cases:
                return {
                    "content": f"I couldn't find any information about the case '{case_name}'. This could be because:\n1. The case name might be misspelled\n2. The case might not be available in our database\n3. The case might be from a different jurisdiction\n\nPlease try with the exact case name or citation.",
                    "message_type": "text",
                    "metadata": {"is_case_search": True, "case_found": False, "searched_case": case_name}
                }
            
            # Generate detailed response about the case
            case = cases[0]  # Take the first result
            response_text = f"""**Case Found: {case.title}**

**Court:** {case.court}
**Citation:** {case.citation}
**Date:** {case.case_date}
**Type:** {case.case_type}

**Summary:**
{case.summary}

**Key Details:**
- **Jurisdiction:** {case.jurisdiction}
- **Source:** {case.source}
- **Relevance Score:** {case.relevance_score * 100:.0f}%

This case appears to be highly relevant to your query. Would you like me to find similar cases or provide more detailed analysis of this case?"""
            
            return {
                "content": response_text.strip(),
                "message_type": "text",
                "metadata": {
                    "is_case_search": True,
                    "case_found": True,
                    "searched_case": case_name,
                    "case_details": {
                        "title": case.title,
                        "court": case.court,
                        "citation": case.citation,
                        "date": case.case_date,
                        "type": case.case_type,
                        "jurisdiction": case.jurisdiction,
                        "source": case.source,
                        "relevance_score": case.relevance_score
                    }
                }
            }
            
        except Exception as e:
            print(f"Error in case search: {e}")
            return {
                "content": f"I encountered an error while searching for the case: {str(e)}",
                "message_type": "text",
                "metadata": {"is_case_search": True, "error": str(e)}
            }
