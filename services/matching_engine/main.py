"""
Matching Engine Service - Eligibility and Similarity Scoring
"""
from fastapi import FastAPI
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

app = FastAPI(title="Matching Engine Service")
logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Match result between job and candidate"""
    job_id: str
    user_id: str
    eligibility_score: float
    similarity_score: float
    combined_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    reasoning: str


class MatchingEngine:
    """Scores job-candidate matches"""
    
    def calculate_eligibility(self, requirements: List[str], candidate_skills: List[str]) -> float:
        """Calculate eligibility score (0-100)"""
        if not requirements:
            return 100.0
        
        matched = sum(1 for req in requirements if any(req.lower() in skill.lower() for skill in candidate_skills))
        return (matched / len(requirements)) * 100
    
    def calculate_similarity(self, job_desc: str, resume: str) -> float:
        """Calculate semantic similarity (0-100)"""
        # Placeholder: would use sentence-transformers/FAISS in production
        return 75.0
    
    def match_job_to_candidate(self, job: Dict[str, Any], resume: str, skills: List[str]) -> MatchResult:
        """Match a job to candidate"""
        eligibility = self.calculate_eligibility(job.get("requirements", []), skills)
        similarity = self.calculate_similarity(job.get("description", ""), resume)
        combined = (eligibility * 0.6) + (similarity * 0.4)
        
        matched_skills = [s for s in skills if any(s.lower() in req.lower() for req in job.get("requirements", []))]
        missing_skills = [r for r in job.get("requirements", []) if r not in matched_skills]
        
        return MatchResult(
            job_id=job.get("id", ""),
            user_id="user_001",  # Placeholder
            eligibility_score=eligibility,
            similarity_score=similarity,
            combined_score=combined,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            reasoning=f"Eligibility: {eligibility:.1f}%, Similarity: {similarity:.1f}%"
        )


matcher = MatchingEngine()


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/match")
async def match_job(job: Dict[str, Any], resume: str, skills: List[str]):
    """Match job to candidate"""
    try:
        result = matcher.match_job_to_candidate(job, resume, skills)
        return {
            "job_id": result.job_id,
            "eligibility_score": result.eligibility_score,
            "similarity_score": result.similarity_score,
            "combined_score": result.combined_score,
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills,
            "reasoning": result.reasoning
        }
    except Exception as e:
        logger.error(f"Error matching job: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
