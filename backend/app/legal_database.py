import requests
import json
import time
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text as sqltext
from .models import LegalCase, LegalStatute
from .schemas import LegalCaseResponse, LegalStatuteResponse
from .config import settings
import google.generativeai as genai

# Configure Google Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)


class LegalDatabaseService:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Legal database APIs (free/public)
        self.legal_apis = {
            "canlii": {
                "base_url": "https://api.canlii.org/v1",
                "api_key": getattr(settings, 'CANLII_API_KEY', None),
                "enabled": True
            },
            "bailii": {
                "base_url": "https://www.bailii.org",
                "api_key": None,
                "enabled": True
            },
            "open_law": {
                "base_url": "https://api.openlaw.io",
                "api_key": getattr(settings, 'OPEN_LAW_API_KEY', None),
                "enabled": False  # Requires API key
            }
        }

    def search_legal_cases(self, query: str, jurisdiction: str = "all", max_results: int = 10) -> List[LegalCaseResponse]:
        """Search for legal cases across multiple databases"""
        cases = []
        
        # Search CanLII (Canadian Legal Information Institute)
        if self.legal_apis["canlii"]["enabled"]:
            canlii_cases = self._search_canlii_cases(query, max_results // 2)
            cases.extend(canlii_cases)
        
        # Search BAILII (British and Irish Legal Information Institute)
        if self.legal_apis["bailii"]["enabled"]:
            bailii_cases = self._search_bailii_cases(query, max_results // 2)
            cases.extend(bailii_cases)
        
        # Remove duplicates and sort by relevance
        unique_cases = self._deduplicate_cases(cases)
        return unique_cases[:max_results]

    def search_legal_statutes(self, query: str, jurisdiction: str = "all", max_results: int = 10) -> List[LegalStatuteResponse]:
        """Search for legal statutes and legislation"""
        statutes = []
        
        # Search CanLII statutes
        if self.legal_apis["canlii"]["enabled"]:
            canlii_statutes = self._search_canlii_statutes(query, max_results // 2)
            statutes.extend(canlii_statutes)
        
        # Search BAILII legislation
        if self.legal_apis["bailii"]["enabled"]:
            bailii_statutes = self._search_bailii_statutes(query, max_results // 2)
            statutes.extend(bailii_statutes)
        
        # Remove duplicates and sort by relevance
        unique_statutes = self._deduplicate_statutes(statutes)
        return unique_statutes[:max_results]

    def _search_canlii_cases(self, query: str, max_results: int) -> List[LegalCaseResponse]:
        """Search CanLII for legal cases"""
        cases = []
        
        try:
            # CanLII API search
            url = f"{self.legal_apis['canlii']['base_url']}/caseBrowse/en"
            params = {
                "q": query,
                "resultCount": max_results,
                "api_key": self.legal_apis["canlii"]["api_key"]
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for case_data in data.get("cases", []):
                    case = LegalCaseResponse(
                        id=0,  # Will be set when saved to database
                        case_id=case_data.get("caseId", ""),
                        title=case_data.get("title", ""),
                        court=case_data.get("court", ""),
                        jurisdiction=case_data.get("jurisdiction", ""),
                        case_date=case_data.get("decisionDate"),
                        case_type=case_data.get("type", ""),
                        summary=case_data.get("summary", ""),
                        citation=case_data.get("citation", ""),
                        source="canlii",
                        relevance_score=self._calculate_relevance_score(query, case_data.get("title", "") + " " + case_data.get("summary", ""))
                    )
                    cases.append(case)
        
        except Exception as e:
            print(f"Error searching CanLII cases: {e}")
        
        return cases

    def _search_bailii_cases(self, query: str, max_results: int) -> List[LegalCaseResponse]:
        """Search BAILII for legal cases (web scraping approach)"""
        cases = []
        
        try:
            # BAILII search URL
            search_url = f"https://www.bailii.org/cgi-bin/markup.cgi?doc=/cgi-bin/search.cgi&query={query}&method=boolean&rank=score&rank=date&rank=relevance&sort=score&sort=date&sort=relevance&results=50&start=1"
            
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                # Parse HTML response (simplified)
                # In a real implementation, you'd use BeautifulSoup or similar
                # For now, we'll create mock data based on the query
                mock_cases = self._generate_mock_bailii_cases(query, max_results)
                cases.extend(mock_cases)
        
        except Exception as e:
            print(f"Error searching BAILII cases: {e}")
        
        return cases

    def _search_canlii_statutes(self, query: str, max_results: int) -> List[LegalStatuteResponse]:
        """Search CanLII for legal statutes"""
        statutes = []
        
        try:
            # CanLII legislation search
            url = f"{self.legal_apis['canlii']['base_url']}/legislationBrowse/en"
            params = {
                "q": query,
                "resultCount": max_results,
                "api_key": self.legal_apis["canlii"]["api_key"]
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for statute_data in data.get("legislations", []):
                    statute = LegalStatuteResponse(
                        id=0,  # Will be set when saved to database
                        statute_id=statute_data.get("legislationId", ""),
                        title=statute_data.get("title", ""),
                        jurisdiction=statute_data.get("jurisdiction", ""),
                        section_number=statute_data.get("sectionNumber"),
                        summary=statute_data.get("summary", ""),
                        effective_date=statute_data.get("effectiveDate"),
                        source="canlii",
                        relevance_score=self._calculate_relevance_score(query, statute_data.get("title", "") + " " + statute_data.get("summary", ""))
                    )
                    statutes.append(statute)
        
        except Exception as e:
            print(f"Error searching CanLII statutes: {e}")
        
        return statutes

    def _search_bailii_statutes(self, query: str, max_results: int) -> List[LegalStatuteResponse]:
        """Search BAILII for legal statutes"""
        statutes = []
        
        try:
            # BAILII legislation search
            search_url = f"https://www.bailii.org/cgi-bin/markup.cgi?doc=/cgi-bin/search.cgi&query={query}&method=boolean&rank=score&rank=date&rank=relevance&sort=score&sort=date&sort=relevance&results=50&start=1"
            
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                # Parse HTML response (simplified)
                # In a real implementation, you'd use BeautifulSoup or similar
                # For now, we'll create mock data based on the query
                mock_statutes = self._generate_mock_bailii_statutes(query, max_results)
                statutes.extend(mock_statutes)
        
        except Exception as e:
            print(f"Error searching BAILII statutes: {e}")
        
        return statutes

    def _generate_mock_bailii_cases(self, query: str, max_results: int) -> List[LegalCaseResponse]:
        """Generate mock BAILII cases for demonstration"""
        mock_cases = [
            {
                "case_id": f"bailii_{i}",
                "title": f"Mock Case {i} - {query.title()}",
                "court": "High Court of Justice",
                "jurisdiction": "England and Wales",
                "case_date": "2023-01-01",
                "case_type": "Civil",
                "summary": f"This is a mock case related to {query} demonstrating legal principles and precedents.",
                "citation": f"[2023] EWHC {i} (Ch)"
            }
            for i in range(1, max_results + 1)
        ]
        
        return [
            LegalCaseResponse(
                id=0,
                case_id=case["case_id"],
                title=case["title"],
                court=case["court"],
                jurisdiction=case["jurisdiction"],
                case_date=case["case_date"],
                case_type=case["case_type"],
                summary=case["summary"],
                citation=case["citation"],
                source="bailii",
                relevance_score=self._calculate_relevance_score(query, case["title"] + " " + case["summary"])
            )
            for case in mock_cases
        ]

    def _generate_mock_bailii_statutes(self, query: str, max_results: int) -> List[LegalStatuteResponse]:
        """Generate mock BAILII statutes for demonstration"""
        mock_statutes = [
            {
                "statute_id": f"bailii_statute_{i}",
                "title": f"Mock Statute {i} - {query.title()}",
                "jurisdiction": "England and Wales",
                "section_number": f"Section {i}",
                "summary": f"This is a mock statute related to {query} providing legal framework and regulations.",
                "effective_date": "2023-01-01"
            }
            for i in range(1, max_results + 1)
        ]
        
        return [
            LegalStatuteResponse(
                id=0,
                statute_id=statute["statute_id"],
                title=statute["title"],
                jurisdiction=statute["jurisdiction"],
                section_number=statute["section_number"],
                summary=statute["summary"],
                effective_date=statute["effective_date"],
                source="bailii",
                relevance_score=self._calculate_relevance_score(query, statute["title"] + " " + statute["summary"])
            )
            for statute in mock_statutes
        ]

    def _calculate_relevance_score(self, query: str, text: str) -> float:
        """Calculate relevance score based on query-text similarity"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(query_words.intersection(text_words))
        union = len(query_words.union(text_words))
        
        return intersection / union if union > 0 else 0.0

    def _deduplicate_cases(self, cases: List[LegalCaseResponse]) -> List[LegalCaseResponse]:
        """Remove duplicate cases based on case_id"""
        seen = set()
        unique_cases = []
        
        for case in cases:
            if case.case_id not in seen:
                seen.add(case.case_id)
                unique_cases.append(case)
        
        # Sort by relevance score
        unique_cases.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        return unique_cases

    def _deduplicate_statutes(self, statutes: List[LegalStatuteResponse]) -> List[LegalStatuteResponse]:
        """Remove duplicate statutes based on statute_id"""
        seen = set()
        unique_statutes = []
        
        for statute in statutes:
            if statute.statute_id not in seen:
                seen.add(statute.statute_id)
                unique_statutes.append(statute)
        
        # Sort by relevance score
        unique_statutes.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        return unique_statutes

    def save_legal_data_to_db(self, db: Session, cases: List[LegalCaseResponse], statutes: List[LegalStatuteResponse]):
        """Save legal data to database"""
        try:
            # Save cases
            for case_data in cases:
                existing_case = db.query(LegalCase).filter(LegalCase.case_id == case_data.case_id).first()
                if not existing_case:
                    case = LegalCase(
                        case_id=case_data.case_id,
                        title=case_data.title,
                        court=case_data.court,
                        jurisdiction=case_data.jurisdiction,
                        case_date=case_data.case_date,
                        case_type=case_data.case_type,
                        summary=case_data.summary,
                        full_text=case_data.summary,  # In real implementation, fetch full text
                        citation=case_data.citation,
                        source=case_data.source
                    )
                    db.add(case)
            
            # Save statutes
            for statute_data in statutes:
                existing_statute = db.query(LegalStatute).filter(LegalStatute.statute_id == statute_data.statute_id).first()
                if not existing_statute:
                    statute = LegalStatute(
                        statute_id=statute_data.statute_id,
                        title=statute_data.title,
                        jurisdiction=statute_data.jurisdiction,
                        section_number=statute_data.section_number,
                        statute_text=statute_data.summary,  # In real implementation, fetch full text
                        summary=statute_data.summary,
                        effective_date=statute_data.effective_date,
                        source=statute_data.source
                    )
                    db.add(statute)
            
            db.commit()
            return True
        
        except Exception as e:
            print(f"Error saving legal data to database: {e}")
            db.rollback()
            return False

    def search_database_cases(self, db: Session, query: str, max_results: int = 10) -> List[LegalCaseResponse]:
        """Search for cases in the local database"""
        try:
            # Use full-text search if available, otherwise use LIKE
            cases = db.query(LegalCase).filter(
                LegalCase.title.ilike(f"%{query}%") |
                LegalCase.summary.ilike(f"%{query}%") |
                LegalCase.keywords.ilike(f"%{query}%")
            ).limit(max_results).all()
            
            return [
                LegalCaseResponse(
                    id=case.id,
                    case_id=case.case_id,
                    title=case.title,
                    court=case.court,
                    jurisdiction=case.jurisdiction,
                    case_date=case.case_date.isoformat() if case.case_date else None,
                    case_type=case.case_type,
                    summary=case.summary,
                    citation=case.citation,
                    source=case.source,
                    relevance_score=self._calculate_relevance_score(query, case.title + " " + case.summary)
                )
                for case in cases
            ]
        
        except Exception as e:
            print(f"Error searching database cases: {e}")
            return []

    def search_database_statutes(self, db: Session, query: str, max_results: int = 10) -> List[LegalStatuteResponse]:
        """Search for statutes in the local database"""
        try:
            statutes = db.query(LegalStatute).filter(
                LegalStatute.title.ilike(f"%{query}%") |
                LegalStatute.summary.ilike(f"%{query}%") |
                LegalStatute.keywords.ilike(f"%{query}%")
            ).limit(max_results).all()
            
            return [
                LegalStatuteResponse(
                    id=statute.id,
                    statute_id=statute.statute_id,
                    title=statute.title,
                    jurisdiction=statute.jurisdiction,
                    section_number=statute.section_number,
                    summary=statute.summary,
                    effective_date=statute.effective_date.isoformat() if statute.effective_date else None,
                    source=statute.source,
                    relevance_score=self._calculate_relevance_score(query, statute.title + " " + statute.summary)
                )
                for statute in statutes
            ]
        
        except Exception as e:
            print(f"Error searching database statutes: {e}")
            return []
