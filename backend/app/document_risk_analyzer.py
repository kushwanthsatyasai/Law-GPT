import re
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import google.generativeai as genai
from .config import settings

# Configure Google Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

@dataclass
class RiskClause:
    clause_text: str
    page_number: int
    line_number: int
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    risk_description: str
    recommendation: str
    section_name: str = ""

class DocumentRiskAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Common risky clauses patterns
        self.risky_patterns = {
            "arbitration_clauses": [
                r"arbitration",
                r"dispute resolution",
                r"binding arbitration",
                r"final and binding"
            ],
            "liability_limitations": [
                r"not liable",
                r"no liability",
                r"limitation of liability",
                r"exclusion of liability",
                r"maximum liability"
            ],
            "termination_clauses": [
                r"terminate",
                r"termination",
                r"breach",
                r"default",
                r"immediate termination"
            ],
            "payment_terms": [
                r"late fees",
                r"penalty",
                r"interest rate",
                r"payment terms",
                r"due date"
            ],
            "warranty_disclaimers": [
                r"as is",
                r"no warranty",
                r"disclaimer",
                r"warranty excluded",
                r"without warranty"
            ],
            "confidentiality": [
                r"confidential",
                r"non-disclosure",
                r"proprietary",
                r"trade secret"
            ],
            "force_majeure": [
                r"force majeure",
                r"act of god",
                r"unforeseen circumstances",
                r"beyond control"
            ],
            "governing_law": [
                r"governing law",
                r"jurisdiction",
                r"venue",
                r"applicable law"
            ]
        }

    def analyze_document_risks(self, document_text: str, document_type: str = "general") -> Dict[str, Any]:
        """Analyze document for risky clauses and provide detailed analysis"""
        try:
            # Split document into pages and lines
            pages = self._split_into_pages(document_text)
            
            # Find risky clauses using pattern matching
            risky_clauses = self._find_risky_clauses(pages)
            
            # Use AI to analyze and provide detailed risk assessment
            ai_analysis = self._get_ai_risk_analysis(document_text, document_type, risky_clauses)
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_risk_score(risky_clauses)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risky_clauses, document_type)
            
            return {
                "overall_risk_score": overall_risk_score,
                "risk_level": self._get_risk_level(overall_risk_score),
                "risky_clauses": [clause.__dict__ for clause in risky_clauses],
                "ai_analysis": ai_analysis,
                "recommendations": recommendations,
                "document_type": document_type,
                "total_pages": len(pages),
                "total_risky_clauses": len(risky_clauses)
            }
            
        except Exception as e:
            return {
                "error": f"Error analyzing document risks: {str(e)}",
                "overall_risk_score": 0,
                "risk_level": "UNKNOWN",
                "risky_clauses": [],
                "ai_analysis": "",
                "recommendations": []
            }

    def _split_into_pages(self, text: str) -> List[List[str]]:
        """Split document text into pages and lines"""
        # Simple page splitting - in real implementation, this would be more sophisticated
        lines = text.split('\n')
        pages = []
        lines_per_page = 50  # Approximate lines per page
        
        for i in range(0, len(lines), lines_per_page):
            page_lines = lines[i:i + lines_per_page]
            pages.append(page_lines)
        
        return pages

    def _find_risky_clauses(self, pages: List[List[str]]) -> List[RiskClause]:
        """Find risky clauses using pattern matching"""
        risky_clauses = []
        
        for page_num, page_lines in enumerate(pages, 1):
            for line_num, line in enumerate(page_lines, 1):
                line_lower = line.lower()
                
                for category, patterns in self.risky_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line_lower, re.IGNORECASE):
                            # Extract the full sentence or paragraph
                            clause_text = self._extract_clause_text(line, page_lines, line_num)
                            
                            # Determine risk level
                            risk_level = self._determine_risk_level(category, clause_text)
                            
                            # Get risk description and recommendation
                            risk_description = self._get_risk_description(category, clause_text)
                            recommendation = self._get_recommendation(category, clause_text)
                            
                            risky_clause = RiskClause(
                                clause_text=clause_text,
                                page_number=page_num,
                                line_number=line_num,
                                risk_level=risk_level,
                                risk_description=risk_description,
                                recommendation=recommendation,
                                section_name=category.replace('_', ' ').title()
                            )
                            
                            risky_clauses.append(risky_clause)
        
        return risky_clauses

    def _extract_clause_text(self, line: str, page_lines: List[str], line_num: int) -> str:
        """Extract the full clause text around the matched line"""
        # Get context around the line (2 lines before and after)
        start_line = max(0, line_num - 3)
        end_line = min(len(page_lines), line_num + 2)
        
        context_lines = page_lines[start_line:end_line]
        return ' '.join(context_lines).strip()

    def _determine_risk_level(self, category: str, clause_text: str) -> str:
        """Determine the risk level of a clause"""
        high_risk_keywords = [
            "immediate termination", "no liability", "binding arbitration",
            "as is", "no warranty", "penalty", "late fees", "exclusive jurisdiction"
        ]
        
        medium_risk_keywords = [
            "termination", "arbitration", "confidential", "governing law",
            "force majeure", "limitation of liability"
        ]
        
        clause_lower = clause_text.lower()
        
        if any(keyword in clause_lower for keyword in high_risk_keywords):
            return "HIGH"
        elif any(keyword in clause_lower for keyword in medium_risk_keywords):
            return "MEDIUM"
        else:
            return "LOW"

    def _get_risk_description(self, category: str, clause_text: str) -> str:
        """Get risk description for a clause category"""
        descriptions = {
            "arbitration_clauses": "This clause may limit your right to go to court and could be expensive.",
            "liability_limitations": "This clause limits the other party's responsibility for damages.",
            "termination_clauses": "This clause defines when and how the agreement can be ended.",
            "payment_terms": "This clause defines payment obligations and potential penalties.",
            "warranty_disclaimers": "This clause limits or excludes warranties and guarantees.",
            "confidentiality": "This clause requires you to keep certain information secret.",
            "force_majeure": "This clause excuses performance due to unforeseen events.",
            "governing_law": "This clause determines which laws apply to disputes."
        }
        
        return descriptions.get(category, "This clause may have legal implications that require careful review.")

    def _get_recommendation(self, category: str, clause_text: str) -> str:
        """Get recommendation for a clause category"""
        recommendations = {
            "arbitration_clauses": "Consider negotiating for court jurisdiction or mutual arbitration terms.",
            "liability_limitations": "Review if liability limitations are reasonable and fair.",
            "termination_clauses": "Ensure termination terms are fair and provide adequate notice.",
            "payment_terms": "Verify payment terms are clear and penalties are reasonable.",
            "warranty_disclaimers": "Consider requesting specific warranties for important aspects.",
            "confidentiality": "Ensure confidentiality terms are mutual and reasonable.",
            "force_majeure": "Review if force majeure events are clearly defined.",
            "governing_law": "Consider if the chosen jurisdiction is convenient for you."
        }
        
        return recommendations.get(category, "Consult with a legal professional before signing.")

    def _get_ai_risk_analysis(self, document_text: str, document_type: str, risky_clauses: List[RiskClause]) -> str:
        """Get AI-powered risk analysis"""
        try:
            prompt = f"""
            Analyze this {document_type} document for legal risks and provide a comprehensive assessment for a common citizen.
            
            Document Text (first 2000 characters):
            {document_text[:2000]}...
            
            Found Risky Clauses: {len(risky_clauses)}
            
            Please provide:
            1. Overall risk assessment
            2. Key areas of concern
            3. Potential legal implications
            4. Advice for the document signer
            5. Whether this document is generally safe to sign
            
            Keep the language simple and practical for a non-lawyer.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI analysis unavailable: {str(e)}"

    def _calculate_risk_score(self, risky_clauses: List[RiskClause]) -> float:
        """Calculate overall risk score (0-100)"""
        if not risky_clauses:
            return 0.0
        
        high_risk_count = sum(1 for clause in risky_clauses if clause.risk_level == "HIGH")
        medium_risk_count = sum(1 for clause in risky_clauses if clause.risk_level == "MEDIUM")
        low_risk_count = sum(1 for clause in risky_clauses if clause.risk_level == "LOW")
        
        # Weighted scoring
        score = (high_risk_count * 10) + (medium_risk_count * 5) + (low_risk_count * 2)
        
        # Normalize to 0-100 scale
        max_possible_score = len(risky_clauses) * 10
        normalized_score = min(100, (score / max_possible_score) * 100) if max_possible_score > 0 else 0
        
        return round(normalized_score, 2)

    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score"""
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_recommendations(self, risky_clauses: List[RiskClause], document_type: str) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        if not risky_clauses:
            recommendations.append("This document appears to have minimal legal risks.")
            return recommendations
        
        high_risk_clauses = [c for c in risky_clauses if c.risk_level == "HIGH"]
        medium_risk_clauses = [c for c in risky_clauses if c.risk_level == "MEDIUM"]
        
        if high_risk_clauses:
            recommendations.append(f"⚠️ HIGH RISK: {len(high_risk_clauses)} high-risk clauses found. Consider consulting a lawyer before signing.")
        
        if medium_risk_clauses:
            recommendations.append(f"⚠️ MEDIUM RISK: {len(medium_risk_clauses)} medium-risk clauses found. Review carefully before signing.")
        
        recommendations.append("📋 Read all terms carefully and ask questions about anything unclear.")
        recommendations.append("⚖️ Consider having a legal professional review the document.")
        recommendations.append("📝 Keep a copy of the signed document for your records.")
        
        if document_type.lower() in ["rental", "lease", "agreement"]:
            recommendations.append("🏠 For rental agreements, ensure all terms are clearly stated and fair.")
        elif document_type.lower() in ["employment", "job", "contract"]:
            recommendations.append("💼 For employment contracts, verify all terms match your understanding.")
        elif document_type.lower() in ["shares", "stock", "investment"]:
            recommendations.append("📈 For investment documents, understand all risks and obligations.")
        
        return recommendations

    def analyze_specific_document_type(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """Analyze specific document types with specialized rules"""
        # Add document-type specific analysis
        base_analysis = self.analyze_document_risks(document_text, document_type)
        
        # Add specific recommendations based on document type
        if document_type.lower() == "rental_agreement":
            base_analysis["specific_risks"] = self._analyze_rental_agreement_risks(document_text)
        elif document_type.lower() == "employment_contract":
            base_analysis["specific_risks"] = self._analyze_employment_contract_risks(document_text)
        elif document_type.lower() == "shares_document":
            base_analysis["specific_risks"] = self._analyze_shares_document_risks(document_text)
        
        return base_analysis

    def _analyze_rental_agreement_risks(self, text: str) -> List[str]:
        """Analyze rental agreement specific risks"""
        risks = []
        
        if "security deposit" in text.lower():
            risks.append("Review security deposit terms and refund conditions")
        
        if "maintenance" in text.lower():
            risks.append("Verify maintenance responsibilities")
        
        if "subletting" in text.lower():
            risks.append("Check subletting restrictions")
        
        return risks

    def _analyze_employment_contract_risks(self, text: str) -> List[str]:
        """Analyze employment contract specific risks"""
        risks = []
        
        if "non-compete" in text.lower():
            risks.append("Review non-compete clause restrictions")
        
        if "confidentiality" in text.lower():
            risks.append("Understand confidentiality obligations")
        
        if "termination" in text.lower():
            risks.append("Verify termination conditions")
        
        return risks

    def _analyze_shares_document_risks(self, text: str) -> List[str]:
        """Analyze shares document specific risks"""
        risks = []
        
        if "risk" in text.lower():
            risks.append("Understand all investment risks")
        
        if "volatility" in text.lower():
            risks.append("Consider market volatility impact")
        
        if "liquidity" in text.lower():
            risks.append("Check liquidity restrictions")
        
        return risks

# Global instance
document_risk_analyzer = DocumentRiskAnalyzer()
