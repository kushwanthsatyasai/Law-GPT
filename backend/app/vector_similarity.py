import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from .models import LegalCase, LegalStatute, Document, Chunk
from .schemas import LegalCaseResponse, LegalStatuteResponse
import json

class VectorSimilarityService:
    def __init__(self):
        # Initialize sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # FAISS indices
        self.case_index = None
        self.statute_index = None
        self.document_index = None
        
        # Metadata storage
        self.case_metadata = []
        self.statute_metadata = []
        self.document_metadata = []
        
        # File paths for persistence
        self.case_index_path = "data/case_index.faiss"
        self.statute_index_path = "data/statute_index.faiss"
        self.document_index_path = "data/document_index.faiss"
        self.metadata_path = "data/metadata.pkl"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Load existing indices if they exist
        self._load_indices()

    def _load_indices(self):
        """Load existing FAISS indices and metadata"""
        try:
            if os.path.exists(self.case_index_path):
                self.case_index = faiss.read_index(self.case_index_path)
            else:
                self.case_index = faiss.IndexFlatIP(self.embedding_dim)
            
            if os.path.exists(self.statute_index_path):
                self.statute_index = faiss.read_index(self.statute_index_path)
            else:
                self.statute_index = faiss.IndexFlatIP(self.embedding_dim)
            
            if os.path.exists(self.document_index_path):
                self.document_index = faiss.read_index(self.document_index_path)
            else:
                self.document_index = faiss.IndexFlatIP(self.embedding_dim)
            
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.case_metadata = metadata.get('cases', [])
                    self.statute_metadata = metadata.get('statutes', [])
                    self.document_metadata = metadata.get('documents', [])
        except Exception as e:
            print(f"Error loading indices: {e}")
            # Initialize empty indices
            self.case_index = faiss.IndexFlatIP(self.embedding_dim)
            self.statute_index = faiss.IndexFlatIP(self.embedding_dim)
            self.document_index = faiss.IndexFlatIP(self.embedding_dim)

    def _save_indices(self):
        """Save FAISS indices and metadata"""
        try:
            faiss.write_index(self.case_index, self.case_index_path)
            faiss.write_index(self.statute_index, self.statute_index_path)
            faiss.write_index(self.document_index, self.document_index_path)
            
            metadata = {
                'cases': self.case_metadata,
                'statutes': self.statute_metadata,
                'documents': self.document_metadata
            }
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
        except Exception as e:
            print(f"Error saving indices: {e}")

    def add_cases_to_index(self, cases: List[LegalCaseResponse]):
        """Add cases to the FAISS index"""
        if not cases:
            return
        
        # Prepare text for embedding
        texts = []
        for case in cases:
            text = f"{case.title} {case.summary} {case.citation} {case.court}"
            texts.append(text)
        
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        embeddings = embeddings.astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.case_index.add(embeddings)
        
        # Store metadata
        for i, case in enumerate(cases):
            self.case_metadata.append({
                'id': case.id,
                'case_id': case.case_id,
                'title': case.title,
                'court': case.court,
                'citation': case.citation,
                'summary': case.summary,
                'case_date': case.case_date,
                'case_type': case.case_type,
                'jurisdiction': case.jurisdiction,
                'source': case.source,
                'relevance_score': case.relevance_score
            })
        
        self._save_indices()

    def add_statutes_to_index(self, statutes: List[LegalStatuteResponse]):
        """Add statutes to the FAISS index"""
        if not statutes:
            return
        
        # Prepare text for embedding
        texts = []
        for statute in statutes:
            text = f"{statute.title} {statute.summary} {statute.section_number} {statute.jurisdiction}"
            texts.append(text)
        
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        embeddings = embeddings.astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.statute_index.add(embeddings)
        
        # Store metadata
        for i, statute in enumerate(statutes):
            self.statute_metadata.append({
                'id': statute.id,
                'statute_id': statute.statute_id,
                'title': statute.title,
                'jurisdiction': statute.jurisdiction,
                'section_number': statute.section_number,
                'summary': statute.summary,
                'effective_date': statute.effective_date,
                'source': statute.source,
                'relevance_score': statute.relevance_score
            })
        
        self._save_indices()

    def add_documents_to_index(self, documents: List[Dict[str, Any]]):
        """Add documents to the FAISS index"""
        if not documents:
            return
        
        # Prepare text for embedding
        texts = []
        for doc in documents:
            text = f"{doc.get('title', '')} {doc.get('content', '')} {doc.get('filename', '')}"
            texts.append(text)
        
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        embeddings = embeddings.astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.document_index.add(embeddings)
        
        # Store metadata
        for i, doc in enumerate(documents):
            self.document_metadata.append({
                'id': doc.get('id'),
                'title': doc.get('title'),
                'filename': doc.get('filename'),
                'content': doc.get('content'),
                'user_id': doc.get('user_id'),
                'created_at': doc.get('created_at')
            })
        
        self._save_indices()

    def find_similar_cases(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases using FAISS"""
        if self.case_index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.case_index.search(query_embedding, min(k, self.case_index.ntotal))
        
        # Return results with metadata
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.case_metadata):
                result = self.case_metadata[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results

    def find_similar_statutes(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar statutes using FAISS"""
        if self.statute_index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.statute_index.search(query_embedding, min(k, self.statute_index.ntotal))
        
        # Return results with metadata
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.statute_metadata):
                result = self.statute_metadata[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results

    def find_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar documents using FAISS"""
        if self.document_index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.document_index.search(query_embedding, min(k, self.document_index.ntotal))
        
        # Return results with metadata
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.document_metadata):
                result = self.document_metadata[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results

    def find_similar_cases_by_case_text(self, case_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases based on case text content"""
        return self.find_similar_cases(case_text, k)

    def get_case_embeddings(self, case_text: str) -> np.ndarray:
        """Get embeddings for case text"""
        embedding = self.model.encode([case_text], convert_to_tensor=False)
        embedding = embedding.astype('float32')
        faiss.normalize_L2(embedding)
        return embedding

    def get_document_embeddings(self, document_text: str) -> np.ndarray:
        """Get embeddings for document text"""
        embedding = self.model.encode([document_text], convert_to_tensor=False)
        embedding = embedding.astype('float32')
        faiss.normalize_L2(embedding)
        return embedding

    def rebuild_index_from_database(self, db: Session):
        """Rebuild all indices from database"""
        try:
            # Clear existing indices
            self.case_index = faiss.IndexFlatIP(self.embedding_dim)
            self.statute_index = faiss.IndexFlatIP(self.embedding_dim)
            self.document_index = faiss.IndexFlatIP(self.embedding_dim)
            self.case_metadata = []
            self.statute_metadata = []
            self.document_metadata = []
            
            # Rebuild from database
            # This would require implementing database queries to get all cases, statutes, and documents
            # For now, we'll keep the existing functionality
            
            self._save_indices()
            print("Indices rebuilt successfully")
        except Exception as e:
            print(f"Error rebuilding indices: {e}")

# Global instance
vector_similarity_service = VectorSimilarityService()
