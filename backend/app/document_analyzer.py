import re
import time
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from .config import settings
from .models import Document
from .schemas import ClauseAnalysis, DocumentAnalysisResponse
from .ingest import extract_text_from_pdf, extract_text_from_image


class DocumentAnalyzer:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Common legal clause patterns
        self.clause_patterns = {
            "termination": [
                r"terminat(?:ion|e|ing)",
                r"end\s+of\s+agreement",
                r"breach\s+of\s+contract",
                r"default\s+under\s+this\s+agreement"
            ],
            "payment": [
                r"payment\s+terms?",
                r"due\s+date",
                r"invoice",
                r"compensation",
                r"fee\s+structure",
                r"billing"
            ],
            "liability": [
                r"liability",
                r"indemnif(?:y|ication)",
                r"damages",
                r"limitation\s+of\s+liability",
                r"hold\s+harmless"
            ],
            "confidentiality": [
                r"confidential",
                r"non-disclosure",
                r"proprietary",
                r"trade\s+secret",
                r"privacy"
            ],
            "intellectual_property": [
                r"intellectual\s+property",
                r"copyright",
                r"patent",
                r"trademark",
                r"work\s+for\s+hire"
            ],
            "governing_law": [
                r"governing\s+law",
                r"jurisdiction",
                r"venue",
                r"dispute\s+resolution",
                r"arbitration"
            ],
            "force_majeure": [
                r"force\s+majeure",
                r"act\s+of\s+god",
                r"unforeseeable",
                r"beyond\s+control"
            ],
            "warranty": [
                r"warrant(?:y|ies)",
                r"guarantee",
                r"representation",
                r"as\s+is"
            ]
        }

    def analyze_document(self, document: Document, analysis_type: str = "comprehensive", 
                        focus_areas: Optional[List[str]] = None) -> DocumentAnalysisResponse:
        """Analyze a document for legal clauses and safety assessment"""
        start_time = time.time()
        
        try:
            # Extract text from document
            text = self._extract_document_text(document)
            if not text.strip():
                return DocumentAnalysisResponse(
                    document_id=document.id,
                    document_title=document.title,
                    analysis_status="failed",
                    total_clauses=0,
                    safe_clauses=0,
                    warning_clauses=0,
                    dangerous_clauses=0,
                    clauses=[],
                    summary="Failed to extract text from document",
                    overall_risk_level="unknown",
                    error_message="No text could be extracted from the document"
                )

            # Identify clauses
            clauses = self._identify_clauses(text, focus_areas)
            
            # Analyze each clause for safety
            analyzed_clauses = []
            for clause in clauses:
                analysis = self._analyze_clause_safety(clause, text)
                analyzed_clauses.append(analysis)

            # Calculate statistics
            safe_count = sum(1 for c in analyzed_clauses if c.safety_level == "safe")
            warning_count = sum(1 for c in analyzed_clauses if c.safety_level == "warning")
            dangerous_count = sum(1 for c in analyzed_clauses if c.safety_level == "dangerous")
            
            # Determine overall risk level
            total_clauses = len(analyzed_clauses)
            if total_clauses == 0:
                overall_risk = "unknown"
            elif dangerous_count > total_clauses * 0.3:
                overall_risk = "high"
            elif dangerous_count > total_clauses * 0.1 or warning_count > total_clauses * 0.4:
                overall_risk = "medium"
            else:
                overall_risk = "low"

            # Generate summary
            summary = self._generate_summary(analyzed_clauses, overall_risk)
            
            processing_time = time.time() - start_time

            return DocumentAnalysisResponse(
                document_id=document.id,
                document_title=document.title,
                analysis_status="completed",
                total_clauses=total_clauses,
                safe_clauses=safe_count,
                warning_clauses=warning_count,
                dangerous_clauses=dangerous_count,
                clauses=analyzed_clauses,
                summary=summary,
                overall_risk_level=overall_risk,
                processing_time=processing_time
            )

        except Exception as e:
            return DocumentAnalysisResponse(
                document_id=document.id,
                document_title=document.title,
                analysis_status="failed",
                total_clauses=0,
                safe_clauses=0,
                warning_clauses=0,
                dangerous_clauses=0,
                clauses=[],
                summary=f"Analysis failed: {str(e)}",
                overall_risk_level="unknown",
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

    def _extract_document_text(self, document: Document) -> str:
        """Extract text from document based on file type"""
        if document.path.lower().endswith('.pdf'):
            return extract_text_from_pdf(document.path)
        elif document.path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return extract_text_from_image(document.path)
        else:
            try:
                with open(document.path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception:
                return ""

    def _identify_clauses(self, text: str, focus_areas: Optional[List[str]] = None) -> List[Dict]:
        """Identify legal clauses in the document text"""
        clauses = []
        
        # Use focus areas or all clause types
        areas_to_check = focus_areas if focus_areas else list(self.clause_patterns.keys())
        
        for clause_type in areas_to_check:
            if clause_type not in self.clause_patterns:
                continue
                
            patterns = self.clause_patterns[clause_type]
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 200)
                    end = min(len(text), match.end() + 500)
                    clause_text = text[start:end].strip()
                    
                    # Clean up the clause text
                    clause_text = re.sub(r'\s+', ' ', clause_text)
                    
                    if len(clause_text) > 50:  # Only include substantial clauses
                        clauses.append({
                            'type': clause_type,
                            'text': clause_text,
                            'start_pos': match.start(),
                            'end_pos': match.end()
                        })
        
        # Remove duplicates and sort by position
        unique_clauses = []
        seen_texts = set()
        for clause in sorted(clauses, key=lambda x: x['start_pos']):
            if clause['text'] not in seen_texts:
                unique_clauses.append(clause)
                seen_texts.add(clause['text'])
        
        return unique_clauses

    def _analyze_clause_safety(self, clause: Dict, full_text: str) -> ClauseAnalysis:
        """Analyze a specific clause for safety using AI"""
        clause_text = clause['text']
        clause_type = clause['type']
        
        # Create a comprehensive prompt for clause analysis
        prompt = f"""
        Analyze this legal clause for safety and potential risks. Consider the following aspects:
        1. Fairness to both parties
        2. Legal enforceability
        3. Potential hidden risks
        4. Industry best practices
        5. Common problematic terms

        Clause Type: {clause_type}
        Clause Text: {clause_text}

        Provide your analysis in the following format:
        SAFETY_LEVEL: [safe/warning/dangerous]
        EXPLANATION: [Detailed explanation of why this clause is safe, concerning, or dangerous]
        RECOMMENDATIONS: [Specific recommendations for improvement if needed]

        Focus on:
        - Unfair terms that heavily favor one party
        - Vague or ambiguous language
        - Excessive liability or penalty clauses
        - Unreasonable termination conditions
        - Hidden fees or costs
        - Unfair dispute resolution terms
        """

        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse the response
            safety_level = "warning"  # default
            explanation = "Unable to analyze this clause properly."
            recommendations = None
            
            lines = analysis_text.split('\n')
            for line in lines:
                if line.startswith('SAFETY_LEVEL:'):
                    level = line.replace('SAFETY_LEVEL:', '').strip().lower()
                    if level in ['safe', 'warning', 'dangerous']:
                        safety_level = level
                elif line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
                elif line.startswith('RECOMMENDATIONS:'):
                    rec = line.replace('RECOMMENDATIONS:', '').strip()
                    if rec and rec != 'None':
                        recommendations = rec
            
            return ClauseAnalysis(
                clause_text=clause_text[:500] + "..." if len(clause_text) > 500 else clause_text,
                clause_type=clause_type,
                safety_level=safety_level,
                explanation=explanation,
                recommendations=recommendations
            )
            
        except Exception as e:
            return ClauseAnalysis(
                clause_text=clause_text[:500] + "..." if len(clause_text) > 500 else clause_text,
                clause_type=clause_type,
                safety_level="warning",
                explanation=f"Error analyzing clause: {str(e)}",
                recommendations="Please review this clause manually."
            )

    def _generate_summary(self, clauses: List[ClauseAnalysis], overall_risk: str) -> str:
        """Generate a summary of the document analysis"""
        if not clauses:
            return "No significant legal clauses were identified in this document."
        
        safe_count = sum(1 for c in clauses if c.safety_level == "safe")
        warning_count = sum(1 for c in clauses if c.safety_level == "warning")
        dangerous_count = sum(1 for c in clauses if c.safety_level == "dangerous")
        
        summary_parts = [
            f"Document Analysis Summary:",
            f"• Total clauses analyzed: {len(clauses)}",
            f"• Safe clauses: {safe_count}",
            f"• Warning clauses: {warning_count}",
            f"• Dangerous clauses: {dangerous_count}",
            f"• Overall risk level: {overall_risk.upper()}"
        ]
        
        if dangerous_count > 0:
            dangerous_clauses = [c for c in clauses if c.safety_level == "dangerous"]
            summary_parts.append(f"\n⚠️  HIGH PRIORITY: {dangerous_count} dangerous clause(s) require immediate attention:")
            for clause in dangerous_clauses[:3]:  # Show top 3 dangerous clauses
                summary_parts.append(f"   • {clause.clause_type}: {clause.explanation[:100]}...")
        
        if warning_count > 0:
            summary_parts.append(f"\n⚠️  {warning_count} clause(s) need review for potential improvements.")
        
        if safe_count > 0:
            summary_parts.append(f"\n✅ {safe_count} clause(s) appear to be fair and reasonable.")
        
        return "\n".join(summary_parts)
