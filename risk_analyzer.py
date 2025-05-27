import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class RiskAnalyzer:
    def __init__(self):
        # Configure Gemini 2.0 Flash
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.system_prompt = """You are a legal document risk analyzer. Your task is to:
1. Identify potentially risky clauses in legal documents
2. Compare them with similar clauses from reference documents
3. Provide a risk score (0-100) and detailed explanation
4. Suggest mitigation strategies if applicable

Focus on:
- Unusual or one-sided terms
- Hidden liabilities
- Ambiguous language
- Non-standard clauses
- Potential legal conflicts"""

    def analyze_document(self, document_chunks: List[Dict], similar_docs: List[Dict]) -> Dict:
        """
        Analyze document chunks and provide risk assessment.
        
        Args:
            document_chunks (List[Dict]): List of document chunks to analyze
            similar_docs (List[Dict]): List of similar reference documents
            
        Returns:
            Dict: Risk analysis results
        """
        # Combine document chunks
        document_text = "\n\n".join([chunk['text'] for chunk in document_chunks])
        
        # Combine similar documents for context
        context = "\n\nReference Documents:\n" + "\n---\n".join([
            f"Document: {doc['metadata']['file_name']}\n{doc['text']}"
            for doc in similar_docs
        ])
        
        # Create analysis prompt
        prompt = f"""System: {self.system_prompt}

Document to analyze:
{document_text}

{context}

Please analyze the document and provide:
1. A list of identified risky clauses
2. Risk score (0-100) with explanation
3. Comparison with similar clauses from reference documents
4. Mitigation suggestions if applicable"""

        # Get analysis from Gemini 2.0 Flash
        response = self.model.generate_content(prompt)
        analysis = response.text
        
        # Extract risk score from analysis
        risk_score = self._extract_risk_score(analysis)
        
        return {
            'analysis': analysis,
            'risk_score': risk_score,
            'document_chunks': document_chunks,
            'similar_docs': similar_docs
        }

    def _extract_risk_score(self, analysis: str) -> int:
        """Extract risk score from analysis text."""
        try:
            # Look for risk score in the format "Risk score: XX"
            score_text = analysis.split("Risk score:")[1].split("\n")[0].strip()
            return int(score_text)
        except:
            return 0  # Default score if extraction fails 