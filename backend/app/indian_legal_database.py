import requests
import json
import time
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text as sqltext
from .models import LegalCase, LegalStatute
from .schemas import LegalCaseResponse, LegalStatuteResponse
from .simple_vector_similarity import simple_vector_similarity_service
from .config import settings
import google.generativeai as genai

# Configure Google Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)


class IndianLegalDatabaseService:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Indian legal database APIs
        self.legal_apis = {
            "indian_kanoon": {
                "base_url": "https://api.indiankanoon.org",
                "api_key": getattr(settings, 'INDIAN_KANOON_API_KEY', None),
                "enabled": True,
                "pricing": {
                    "search": 0.50,
                    "document": 0.20,
                    "fragment": 0.05
                }
            },
            "scc_online": {
                "base_url": "https://restapi.scconline.gen.in",
                "api_key": getattr(settings, 'SCC_ONLINE_API_KEY', None),
                "enabled": True
            },
            "kanoon_dev": {
                "base_url": "https://api.kanoon.dev",
                "api_key": getattr(settings, 'KANOON_DEV_API_KEY', None),
                "enabled": True
            }
        }

    def _get_mock_cases(self, query: str, court: str = "all", max_results: int = 10) -> List[LegalCaseResponse]:
        """Return mock legal cases when API keys are not available"""
        mock_cases = [
            {
                "id": 1,
                "case_id": "MOCK001",
                "title": f"Sample Case Related to {query}",
                "court": "Supreme Court of India" if court == "all" else court,
                "jurisdiction": "India",
                "case_date": "2023-01-15",
                "case_type": "Civil Appeal",
                "summary": f"This is a sample legal case related to '{query}'. The case involves important legal principles and precedents that may be relevant to your research. This mock data is provided when external API keys are not configured.",
                "citation": "2023 SCC 123",
                "source": "mock_data",
                "relevance_score": 0.85
            },
            {
                "id": 2,
                "case_id": "MOCK002", 
                "title": f"Another Case on {query}",
                "court": "High Court of Delhi" if court == "all" else court,
                "jurisdiction": "Delhi",
                "case_date": "2022-11-20",
                "case_type": "Writ Petition",
                "summary": f"Another sample case dealing with '{query}'. This demonstrates how the legal system addresses similar issues across different courts and jurisdictions.",
                "citation": "2022 DLH 456",
                "source": "mock_data",
                "relevance_score": 0.75
            },
            {
                "id": 3,
                "case_id": "MOCK003",
                "title": f"Landmark Judgment on {query}",
                "court": "Supreme Court of India" if court == "all" else court,
                "jurisdiction": "India",
                "case_date": "2021-08-10",
                "case_type": "Constitutional Case",
                "summary": f"A landmark judgment that established important legal principles regarding '{query}'. This case has significant implications for future legal proceedings.",
                "citation": "2021 SC 789",
                "source": "mock_data",
                "relevance_score": 0.90
            }
        ]
        
        return [LegalCaseResponse(**case) for case in mock_cases[:max_results]]

    def _get_mock_statutes(self, query: str, jurisdiction: str = "all", max_results: int = 10) -> List[LegalStatuteResponse]:
        """Return mock legal statutes when API keys are not available"""
        mock_statutes = [
            {
                "id": 1,
                "statute_id": "MOCK_STATUTE_001",
                "title": f"Sample Act Related to {query}",
                "jurisdiction": "India" if jurisdiction == "all" else jurisdiction,
                "section_number": "Section 15",
                "summary": f"This is a sample legal statute related to '{query}'. The act contains important provisions that regulate the subject matter and establish legal frameworks.",
                "effective_date": "2020-01-01",
                "source": "mock_data",
                "relevance_score": 0.80
            },
            {
                "id": 2,
                "statute_id": "MOCK_STATUTE_002",
                "title": f"Amendment Act for {query}",
                "jurisdiction": "India" if jurisdiction == "all" else jurisdiction,
                "section_number": "Section 8A",
                "summary": f"An amendment act that modifies existing laws related to '{query}'. This demonstrates how legal frameworks evolve to address changing circumstances.",
                "effective_date": "2022-06-01",
                "source": "mock_data",
                "relevance_score": 0.70
            }
        ]
        
        return [LegalStatuteResponse(**statute) for statute in mock_statutes[:max_results]]

    def _get_mock_specific_case(self, case_name: str, case_details: str = "") -> List[LegalCaseResponse]:
        """Return mock data for specific case search"""
        mock_cases = [
            {
                "id": 1,
                "case_id": f"SPECIFIC_{case_name.replace(' ', '_').upper()}",
                "title": f"{case_name} - Detailed Case Analysis",
                "court": "Supreme Court of India",
                "jurisdiction": "India",
                "case_date": "2023-06-15",
                "case_type": "Civil Appeal",
                "summary": f"This is a detailed analysis of the case '{case_name}'. {case_details if case_details else 'The case involves important legal principles and has significant implications for similar matters.'} This mock data demonstrates how specific case searches would work with real API integration.",
                "citation": f"2023 SCC {hash(case_name) % 1000}",
                "source": "indian_kanoon_mock",
                "relevance_score": 0.95
            }
        ]
        
        return [LegalCaseResponse(**case) for case in mock_cases]

    def _get_mock_similar_cases(self, case_text: str, case_type: str = "civil", max_results: int = 10) -> List[LegalCaseResponse]:
        """Return mock data for similar cases search"""
        # Extract key terms from case text for mock data
        key_terms = case_text.split()[:3] if case_text else ["legal", "matter", "dispute"]
        
        mock_cases = [
            {
                "id": 1,
                "case_id": f"SIMILAR_001",
                "title": f"Similar Case Involving {' '.join(key_terms)}",
                "court": "High Court of Delhi",
                "jurisdiction": "Delhi",
                "case_date": "2023-03-20",
                "case_type": case_type.title(),
                "summary": f"This case is similar to the provided case text involving {' '.join(key_terms)}. The judgment established important precedents that may be relevant to your case. The court ruled on similar legal principles and facts.",
                "citation": f"2023 DLH {hash(case_text) % 500}",
                "source": "indian_kanoon_mock",
                "relevance_score": 0.88
            },
            {
                "id": 2,
                "case_id": f"SIMILAR_002",
                "title": f"Related {case_type.title()} Case - {' '.join(key_terms[:2])}",
                "court": "Supreme Court of India",
                "jurisdiction": "India",
                "case_date": "2022-11-10",
                "case_type": case_type.title(),
                "summary": f"A landmark case that dealt with similar legal issues as described in your case text. The Supreme Court's judgment provides important guidance on how such matters should be approached legally.",
                "citation": f"2022 SC {hash(case_text) % 300}",
                "source": "scc_online_mock",
                "relevance_score": 0.92
            },
            {
                "id": 3,
                "case_id": f"SIMILAR_003",
                "title": f"Precedent Case for {' '.join(key_terms)}",
                "court": "High Court of Bombay",
                "jurisdiction": "Maharashtra",
                "case_date": "2023-01-05",
                "case_type": case_type.title(),
                "summary": f"This case serves as an important precedent for matters similar to your case. The court's reasoning and legal analysis provide valuable insights for understanding how similar cases are typically resolved.",
                "citation": f"2023 BOM {hash(case_text) % 400}",
                "source": "kanoon_dev_mock",
                "relevance_score": 0.85
            }
        ]
        
        return [LegalCaseResponse(**case) for case in mock_cases[:max_results]]

    def _extract_legal_concepts(self, case_text: str) -> List[str]:
        """Extract key legal concepts from case text using AI"""
        try:
            prompt = f"""
            Analyze the following legal case text and extract the key legal concepts, issues, and keywords that would be useful for finding similar cases.
            
            Case Text: {case_text[:1000]}...
            
            Please provide a list of 5-10 key legal concepts, issues, or keywords that would help identify similar cases.
            Format: Return only a comma-separated list of terms.
            """
            
            response = self.model.generate_content(prompt)
            concepts = [concept.strip() for concept in response.text.split(',')]
            return concepts[:10]  # Limit to 10 concepts
        except Exception as e:
            # Fallback to simple keyword extraction
            words = case_text.lower().split()
            legal_keywords = [word for word in words if len(word) > 4 and word not in ['case', 'court', 'judgment', 'order']]
            return legal_keywords[:10]

    def search_indian_cases(self, query: str, court: str = "all", max_results: int = 10) -> List[LegalCaseResponse]:
        """Search for Indian legal cases across multiple databases"""
        cases = []
        
        # Check if we have API keys available
        has_api_keys = any(
            api.get("api_key") for api in self.legal_apis.values() 
            if api.get("api_key")
        )
        
        if not has_api_keys:
            # Return mock data when no API keys are available
            return self._get_mock_cases(query, court, max_results)
        
        # Search Indian Kanoon
        if self.legal_apis["indian_kanoon"]["enabled"] and self.legal_apis["indian_kanoon"]["api_key"]:
            ik_cases = self._search_indian_kanoon_cases(query, court, max_results // 2)
            cases.extend(ik_cases)
        
        # Search SCC Online
        if self.legal_apis["scc_online"]["enabled"] and self.legal_apis["scc_online"]["api_key"]:
            scc_cases = self._search_scc_online_cases(query, court, max_results // 2)
            cases.extend(scc_cases)
        
        # Search Kanoon.dev
        if self.legal_apis["kanoon_dev"]["enabled"] and self.legal_apis["kanoon_dev"]["api_key"]:
            kd_cases = self._search_kanoon_dev_cases(query, court, max_results // 2)
            cases.extend(kd_cases)
        
        # If no cases found from APIs, return mock data
        if not cases:
            cases = self._get_mock_cases(query, court, max_results)
        
        # Remove duplicates and sort by relevance
        unique_cases = self._deduplicate_cases(cases)
        return unique_cases[:max_results]

    def search_specific_case(self, case_name: str, case_details: str = "") -> List[LegalCaseResponse]:
        """Search for a specific case by name and details"""
        cases = []
        
        # Check if we have API keys available
        has_api_keys = any(
            api.get("api_key") for api in self.legal_apis.values() 
            if api.get("api_key")
        )
        
        if not has_api_keys:
            # Return mock data for specific case search
            return self._get_mock_specific_case(case_name, case_details)
        
        # Search Indian Kanoon for specific case
        if self.legal_apis["indian_kanoon"]["enabled"] and self.legal_apis["indian_kanoon"]["api_key"]:
            ik_cases = self._search_specific_indian_kanoon_case(case_name, case_details)
            cases.extend(ik_cases)
        
        # Search other databases
        if self.legal_apis["scc_online"]["enabled"] and self.legal_apis["scc_online"]["api_key"]:
            scc_cases = self._search_specific_scc_online_case(case_name, case_details)
            cases.extend(scc_cases)
        
        # If no cases found from APIs, return mock data
        if not cases:
            cases = self._get_mock_specific_case(case_name, case_details)
        
        return cases

    def find_similar_cases(self, case_text: str, case_type: str = "civil", max_results: int = 10) -> List[LegalCaseResponse]:
        """Find similar cases based on case text content using FAISS vector similarity"""
        try:
            # Use simple similarity to find similar cases
            similar_cases = simple_vector_similarity_service.find_similar_cases(case_text, max_results)
            
            if similar_cases:
                # Convert to LegalCaseResponse objects
                cases = []
                for case_data in similar_cases:
                    case = LegalCaseResponse(
                        id=case_data.get('id', 0),
                        case_id=case_data.get('case_id', ''),
                        title=case_data.get('title', ''),
                        court=case_data.get('court', ''),
                        jurisdiction=case_data.get('jurisdiction', ''),
                        case_date=case_data.get('case_date', ''),
                        case_type=case_data.get('case_type', case_type),
                        summary=case_data.get('summary', ''),
                        citation=case_data.get('citation', ''),
                        source=case_data.get('source', ''),
                        relevance_score=case_data.get('similarity_score', 0.0)
                    )
                    cases.append(case)
                
                return cases
            else:
                # Fallback to mock data if no similar cases found
                return self._get_mock_similar_cases(case_text, case_type, max_results)
                
        except Exception as e:
            print(f"Error in FAISS similarity search: {e}")
            # Fallback to mock data
            return self._get_mock_similar_cases(case_text, case_type, max_results)

    def add_cases_to_vector_index(self, cases: List[LegalCaseResponse]):
        """Add cases to the FAISS vector index for similarity search"""
        try:
            simple_vector_similarity_service.add_cases_to_index(cases)
            print(f"Added {len(cases)} cases to similarity index")
        except Exception as e:
            print(f"Error adding cases to similarity index: {e}")

    def search_indian_statutes(self, query: str, jurisdiction: str = "all", max_results: int = 10) -> List[LegalStatuteResponse]:
        """Search for Indian legal statutes and legislation"""
        statutes = []
        
        # Check if we have API keys available
        has_api_keys = any(
            api.get("api_key") for api in self.legal_apis.values() 
            if api.get("api_key")
        )
        
        if not has_api_keys:
            # Return mock data when no API keys are available
            return self._get_mock_statutes(query, jurisdiction, max_results)
        
        # Search Indian Kanoon for statutes
        if self.legal_apis["indian_kanoon"]["enabled"] and self.legal_apis["indian_kanoon"]["api_key"]:
            ik_statutes = self._search_indian_kanoon_statutes(query, jurisdiction, max_results // 2)
            statutes.extend(ik_statutes)
        
        # Search SCC Online for legislation
        if self.legal_apis["scc_online"]["enabled"] and self.legal_apis["scc_online"]["api_key"]:
            scc_statutes = self._search_scc_online_statutes(query, jurisdiction, max_results // 2)
            statutes.extend(scc_statutes)
        
        # If no statutes found from APIs, return mock data
        if not statutes:
            statutes = self._get_mock_statutes(query, jurisdiction, max_results)
        
        # Remove duplicates and sort by relevance
        unique_statutes = self._deduplicate_statutes(statutes)
        return unique_statutes[:max_results]

    def _search_indian_kanoon_cases(self, query: str, court: str, max_results: int) -> List[LegalCaseResponse]:
        """Search Indian Kanoon for legal cases"""
        cases = []
        
        try:
            # Indian Kanoon search API
            url = f"{self.legal_apis['indian_kanoon']['base_url']}/search"
            params = {
                "q": query,
                "format": "json",
                "api_key": self.legal_apis["indian_kanoon"]["api_key"]
            }
            
            if court != "all":
                params["court"] = court
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for case_data in data.get("results", [])[:max_results]:
                    case = LegalCaseResponse(
                        id=0,  # Will be set when saved to database
                        case_id=case_data.get("doc_id", ""),
                        title=case_data.get("title", ""),
                        court=case_data.get("court", ""),
                        jurisdiction="India",
                        case_date=case_data.get("date"),
                        case_type=case_data.get("type", "Civil"),
                        summary=case_data.get("snippet", ""),
                        citation=case_data.get("citation", ""),
                        source="indian_kanoon",
                        relevance_score=self._calculate_relevance_score(query, case_data.get("title", "") + " " + case_data.get("snippet", ""))
                    )
                    cases.append(case)
        
        except Exception as e:
            print(f"Error searching Indian Kanoon cases: {e}")
            # Fallback to mock data for demonstration
            cases = self._generate_mock_indian_cases(query, court, max_results, "indian_kanoon")
        
        return cases

    def _search_scc_online_cases(self, query: str, court: str, max_results: int) -> List[LegalCaseResponse]:
        """Search SCC Online for legal cases"""
        cases = []
        
        try:
            # SCC Online search API
            url = f"{self.legal_apis['scc_online']['base_url']}/search"
            params = {
                "query": query,
                "limit": max_results,
                "api_key": self.legal_apis["scc_online"]["api_key"]
            }
            
            if court != "all":
                params["court"] = court
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for case_data in data.get("cases", []):
                    case = LegalCaseResponse(
                        id=0,
                        case_id=case_data.get("id", ""),
                        title=case_data.get("title", ""),
                        court=case_data.get("court", ""),
                        jurisdiction="India",
                        case_date=case_data.get("date"),
                        case_type=case_data.get("type", "Civil"),
                        summary=case_data.get("summary", ""),
                        citation=case_data.get("citation", ""),
                        source="scc_online",
                        relevance_score=self._calculate_relevance_score(query, case_data.get("title", "") + " " + case_data.get("summary", ""))
                    )
                    cases.append(case)
        
        except Exception as e:
            print(f"Error searching SCC Online cases: {e}")
            # Fallback to mock data for demonstration
            cases = self._generate_mock_indian_cases(query, court, max_results, "scc_online")
        
        return cases

    def _search_kanoon_dev_cases(self, query: str, court: str, max_results: int) -> List[LegalCaseResponse]:
        """Search Kanoon.dev for legal cases"""
        cases = []
        
        try:
            # Kanoon.dev search API
            url = f"{self.legal_apis['kanoon_dev']['base_url']}/cases/search"
            params = {
                "q": query,
                "limit": max_results,
                "api_key": self.legal_apis["kanoon_dev"]["api_key"]
            }
            
            if court != "all":
                params["court"] = court
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for case_data in data.get("results", []):
                    case = LegalCaseResponse(
                        id=0,
                        case_id=case_data.get("case_id", ""),
                        title=case_data.get("title", ""),
                        court=case_data.get("court", ""),
                        jurisdiction="India",
                        case_date=case_data.get("date"),
                        case_type=case_data.get("type", "Civil"),
                        summary=case_data.get("summary", ""),
                        citation=case_data.get("citation", ""),
                        source="kanoon_dev",
                        relevance_score=self._calculate_relevance_score(query, case_data.get("title", "") + " " + case_data.get("summary", ""))
                    )
                    cases.append(case)
        
        except Exception as e:
            print(f"Error searching Kanoon.dev cases: {e}")
            # Fallback to mock data for demonstration
            cases = self._generate_mock_indian_cases(query, court, max_results, "kanoon_dev")
        
        return cases

    def _search_indian_kanoon_statutes(self, query: str, jurisdiction: str, max_results: int) -> List[LegalStatuteResponse]:
        """Search Indian Kanoon for legal statutes"""
        statutes = []
        
        try:
            # Indian Kanoon statute search
            url = f"{self.legal_apis['indian_kanoon']['base_url']}/statute/search"
            params = {
                "q": query,
                "format": "json",
                "api_key": self.legal_apis["indian_kanoon"]["api_key"]
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for statute_data in data.get("results", [])[:max_results]:
                    statute = LegalStatuteResponse(
                        id=0,
                        statute_id=statute_data.get("id", ""),
                        title=statute_data.get("title", ""),
                        jurisdiction="India",
                        section_number=statute_data.get("section"),
                        summary=statute_data.get("summary", ""),
                        effective_date=statute_data.get("date"),
                        source="indian_kanoon",
                        relevance_score=self._calculate_relevance_score(query, statute_data.get("title", "") + " " + statute_data.get("summary", ""))
                    )
                    statutes.append(statute)
        
        except Exception as e:
            print(f"Error searching Indian Kanoon statutes: {e}")
            # Fallback to mock data for demonstration
            statutes = self._generate_mock_indian_statutes(query, jurisdiction, max_results, "indian_kanoon")
        
        return statutes

    def _search_scc_online_statutes(self, query: str, jurisdiction: str, max_results: int) -> List[LegalStatuteResponse]:
        """Search SCC Online for legal statutes"""
        statutes = []
        
        try:
            # SCC Online statute search
            url = f"{self.legal_apis['scc_online']['base_url']}/statutes/search"
            params = {
                "query": query,
                "limit": max_results,
                "api_key": self.legal_apis["scc_online"]["api_key"]
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for statute_data in data.get("statutes", []):
                    statute = LegalStatuteResponse(
                        id=0,
                        statute_id=statute_data.get("id", ""),
                        title=statute_data.get("title", ""),
                        jurisdiction="India",
                        section_number=statute_data.get("section"),
                        summary=statute_data.get("summary", ""),
                        effective_date=statute_data.get("date"),
                        source="scc_online",
                        relevance_score=self._calculate_relevance_score(query, statute_data.get("title", "") + " " + statute_data.get("summary", ""))
                    )
                    statutes.append(statute)
        
        except Exception as e:
            print(f"Error searching SCC Online statutes: {e}")
            # Fallback to mock data for demonstration
            statutes = self._generate_mock_indian_statutes(query, jurisdiction, max_results, "scc_online")
        
        return statutes

    def _generate_mock_indian_cases(self, query: str, court: str, max_results: int, source: str) -> List[LegalCaseResponse]:
        """Generate mock Indian legal cases for demonstration"""
        indian_courts = {
            "supreme_court": "Supreme Court of India",
            "high_court": "High Court",
            "district_court": "District Court",
            "all": "Various Courts"
        }
        
        court_name = indian_courts.get(court, "Various Courts")
        
        mock_cases = [
            {
                "case_id": f"{source}_{i}",
                "title": f"Mock Indian Case {i} - {query.title()}",
                "court": court_name,
                "jurisdiction": "India",
                "case_date": "2023-01-01",
                "case_type": "Civil",
                "summary": f"This is a mock Indian legal case related to {query} demonstrating legal principles under Indian law.",
                "citation": f"[2023] SC {i} (India)"
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
                source=source,
                relevance_score=self._calculate_relevance_score(query, case["title"] + " " + case["summary"])
            )
            for case in mock_cases
        ]

    def _generate_mock_indian_statutes(self, query: str, jurisdiction: str, max_results: int, source: str) -> List[LegalStatuteResponse]:
        """Generate mock Indian legal statutes for demonstration"""
        indian_acts = [
            "Indian Contract Act, 1872",
            "Indian Penal Code, 1860",
            "Code of Civil Procedure, 1908",
            "Code of Criminal Procedure, 1973",
            "Constitution of India, 1950",
            "Companies Act, 2013",
            "Consumer Protection Act, 2019",
            "Right to Information Act, 2005"
        ]
        
        mock_statutes = []
        for i in range(1, max_results + 1):
            act_name = indian_acts[i % len(indian_acts)]
            mock_statutes.append({
                "statute_id": f"{source}_statute_{i}",
                "title": f"{act_name} - {query.title()}",
                "jurisdiction": "India",
                "section_number": f"Section {i}",
                "summary": f"This is a mock Indian statute related to {query} providing legal framework under Indian law.",
                "effective_date": "2023-01-01"
            })
        
        return [
            LegalStatuteResponse(
                id=0,
                statute_id=statute["statute_id"],
                title=statute["title"],
                jurisdiction=statute["jurisdiction"],
                section_number=statute["section_number"],
                summary=statute["summary"],
                effective_date=statute["effective_date"],
                source=source,
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

    def search_database_indian_cases(self, db: Session, query: str, max_results: int = 10) -> List[LegalCaseResponse]:
        """Search for Indian cases in the local database"""
        try:
            cases = db.query(LegalCase).filter(
                LegalCase.jurisdiction == "India",
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
            print(f"Error searching database Indian cases: {e}")
            return []

    def search_database_indian_statutes(self, db: Session, query: str, max_results: int = 10) -> List[LegalStatuteResponse]:
        """Search for Indian statutes in the local database"""
        try:
            statutes = db.query(LegalStatute).filter(
                LegalStatute.jurisdiction == "India",
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
            print(f"Error searching database Indian statutes: {e}")
            return []

    def save_indian_legal_data_to_db(self, db: Session, cases: List[LegalCaseResponse], statutes: List[LegalStatuteResponse]):
        """Save Indian legal data to database"""
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
            print(f"Error saving Indian legal data to database: {e}")
            db.rollback()
            return False

    def get_available_courts(self) -> List[Dict[str, str]]:
        """Get list of available Indian courts"""
        return [
            {"id": "supreme_court", "name": "Supreme Court of India"},
            {"id": "high_court", "name": "High Courts"},
            {"id": "district_court", "name": "District Courts"},
            {"id": "all", "name": "All Courts"}
        ]

    def get_available_jurisdictions(self) -> List[Dict[str, str]]:
        """Get list of available Indian jurisdictions"""
        return [
            {"id": "central", "name": "Central Government"},
            {"id": "state", "name": "State Government"},
            {"id": "union_territory", "name": "Union Territory"},
            {"id": "all", "name": "All Jurisdictions"}
        ]
