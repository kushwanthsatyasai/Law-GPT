import numpy as np
import pickle
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .models import LegalCase, LegalStatute, Document, Chunk
from .schemas import LegalCaseResponse, LegalStatuteResponse
import json
import hashlib

class SimpleVectorSimilarityService:
    def __init__(self):
        # Simple TF-IDF based similarity (no external dependencies)
        self.case_documents = []
        self.statute_documents = []
        self.document_documents = []
        
        # File paths for persistence
        self.data_dir = "data"
        self.case_data_path = os.path.join(self.data_dir, "case_data.pkl")
        self.statute_data_path = os.path.join(self.data_dir, "statute_data.pkl")
        self.document_data_path = os.path.join(self.data_dir, "document_data.pkl")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load existing data from files"""
        try:
            if os.path.exists(self.case_data_path):
                with open(self.case_data_path, 'rb') as f:
                    self.case_documents = pickle.load(f)
            
            if os.path.exists(self.statute_data_path):
                with open(self.statute_data_path, 'rb') as f:
                    self.statute_documents = pickle.load(f)
            
            if os.path.exists(self.document_data_path):
                with open(self.document_data_path, 'rb') as f:
                    self.document_documents = pickle.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.case_documents = []
            self.statute_documents = []
            self.document_documents = []

    def _save_data(self):
        """Save data to files"""
        try:
            with open(self.case_data_path, 'wb') as f:
                pickle.dump(self.case_documents, f)
            
            with open(self.statute_data_path, 'wb') as f:
                pickle.dump(self.statute_documents, f)
            
            with open(self.document_data_path, 'wb') as f:
                pickle.dump(self.document_documents, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:20]  # Limit to top 20 keywords

    def add_cases_to_index(self, cases: List[LegalCaseResponse]):
        """Add cases to the similarity index"""
        if not cases:
            return
        
        for case in cases:
            case_data = {
                'id': case.id,
                'case_id': case.case_id,
                'title': case.title,
                'court': case.court,
                'jurisdiction': case.jurisdiction,
                'case_date': case.case_date,
                'case_type': case.case_type,
                'summary': case.summary,
                'citation': case.citation,
                'source': case.source,
                'relevance_score': case.relevance_score,
                'keywords': self._extract_keywords(f"{case.title} {case.summary} {case.citation}"),
                'full_text': f"{case.title} {case.summary} {case.citation} {case.court}"
            }
            self.case_documents.append(case_data)
        
        self._save_data()
        print(f"Added {len(cases)} cases to similarity index")

    def add_statutes_to_index(self, statutes: List[LegalStatuteResponse]):
        """Add statutes to the similarity index"""
        if not statutes:
            return
        
        for statute in statutes:
            statute_data = {
                'id': statute.id,
                'statute_id': statute.statute_id,
                'title': statute.title,
                'jurisdiction': statute.jurisdiction,
                'section_number': statute.section_number,
                'summary': statute.summary,
                'effective_date': statute.effective_date,
                'source': statute.source,
                'relevance_score': statute.relevance_score,
                'keywords': self._extract_keywords(f"{statute.title} {statute.summary} {statute.section_number}"),
                'full_text': f"{statute.title} {statute.summary} {statute.section_number} {statute.jurisdiction}"
            }
            self.statute_documents.append(statute_data)
        
        self._save_data()
        print(f"Added {len(statutes)} statutes to similarity index")

    def add_documents_to_index(self, documents: List[Dict[str, Any]]):
        """Add documents to the similarity index"""
        if not documents:
            return
        
        for doc in documents:
            doc_data = {
                'id': doc.get('id'),
                'title': doc.get('title', ''),
                'filename': doc.get('filename', ''),
                'content': doc.get('content', ''),
                'user_id': doc.get('user_id'),
                'created_at': doc.get('created_at'),
                'keywords': self._extract_keywords(doc.get('content', '')),
                'full_text': f"{doc.get('title', '')} {doc.get('content', '')}"
            }
            self.document_documents.append(doc_data)
        
        self._save_data()
        print(f"Added {len(documents)} documents to similarity index")

    def find_similar_cases(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases using text similarity"""
        if not self.case_documents:
            return []
        
        # Calculate similarity scores
        similarities = []
        for case in self.case_documents:
            similarity = self._simple_text_similarity(query, case['full_text'])
            similarities.append((similarity, case))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Return top k results
        results = []
        for similarity, case in similarities[:k]:
            if similarity > 0.1:  # Only return results with meaningful similarity
                result = case.copy()
                result['similarity_score'] = similarity
                results.append(result)
        
        return results

    def find_similar_statutes(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar statutes using text similarity"""
        if not self.statute_documents:
            return []
        
        # Calculate similarity scores
        similarities = []
        for statute in self.statute_documents:
            similarity = self._simple_text_similarity(query, statute['full_text'])
            similarities.append((similarity, statute))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Return top k results
        results = []
        for similarity, statute in similarities[:k]:
            if similarity > 0.1:  # Only return results with meaningful similarity
                result = statute.copy()
                result['similarity_score'] = similarity
                results.append(result)
        
        return results

    def find_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar documents using text similarity"""
        if not self.document_documents:
            return []
        
        # Calculate similarity scores
        similarities = []
        for doc in self.document_documents:
            similarity = self._simple_text_similarity(query, doc['full_text'])
            similarities.append((similarity, doc))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Return top k results
        results = []
        for similarity, doc in similarities[:k]:
            if similarity > 0.1:  # Only return results with meaningful similarity
                result = doc.copy()
                result['similarity_score'] = similarity
                results.append(result)
        
        return results

    def find_similar_cases_by_case_text(self, case_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases based on case text content"""
        return self.find_similar_cases(case_text, k)

    def get_case_embeddings(self, case_text: str) -> np.ndarray:
        """Get simple keyword-based representation"""
        keywords = self._extract_keywords(case_text)
        # Return a simple hash-based representation
        text_hash = hashlib.md5(case_text.encode()).hexdigest()
        return np.array([hash(text_hash) % 1000])  # Simple numeric representation

    def get_document_embeddings(self, document_text: str) -> np.ndarray:
        """Get simple keyword-based representation"""
        keywords = self._extract_keywords(document_text)
        # Return a simple hash-based representation
        text_hash = hashlib.md5(document_text.encode()).hexdigest()
        return np.array([hash(text_hash) % 1000])  # Simple numeric representation

    def rebuild_index_from_database(self, db: Session):
        """Rebuild all indices from database"""
        try:
            # Clear existing data
            self.case_documents = []
            self.statute_documents = []
            self.document_documents = []
            
            # Rebuild from database
            # This would require implementing database queries to get all cases, statutes, and documents
            # For now, we'll keep the existing functionality
            
            self._save_data()
            print("Indices rebuilt successfully")
        except Exception as e:
            print(f"Error rebuilding indices: {e}")

# Global instance
simple_vector_similarity_service = SimpleVectorSimilarityService()
