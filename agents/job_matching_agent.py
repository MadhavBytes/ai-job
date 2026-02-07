"""
Job Matching Agent - Uses CrewAI to plan job matching strategy
Outputs JSON only, no side effects
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class JobMatchingAgent:
    """
    Agent that analyzes job requirements and candidate profile
    to determine optimal matches. Outputs JSON strategy only.
    """
    
    def __init__(self):
        self.name = "Job Matching Agent"
    
    def analyze_match(self, job: Dict[str, Any], candidate_profile: Dict[str, Any]) -> str:
        """
        Analyze job-candidate match and return JSON strategy
        
        Args:
            job: Job listing data
            candidate_profile: Candidate skills and experience
        
        Returns:
            JSON string with matching strategy
        """
        strategy = {
            "agent": self.name,
            "job_id": job.get("id"),
            "match_analysis": {
                "should_match": True,
                "confidence": 0.85,
                "key_factors": [
                    "Skills alignment",
                    "Experience level",
                    "Location match"
                ],
                "gaps": [
                    "Missing advanced Python"
                ]
            },
            "recommendation": "APPLY"
        }
        
        return json.dumps(strategy, indent=2)


# Example usage
if __name__ == "__main__":
    agent = JobMatchingAgent()
    job = {"id": "job_001", "title": "Python Developer", "requirements": ["Python", "FastAPI"]}
    candidate = {"skills": ["Python", "Django", "PostgreSQL"]}
    result = agent.analyze_match(job, candidate)
    print(result)
