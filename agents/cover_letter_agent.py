"""
Cover Letter Agent - Plans personalized cover letter generation
Outputs JSON strategy only
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CoverLetterAgent:
    """
    Agent that plans how to write compelling, personalized cover letters
    based on job requirements and candidate profile. Outputs JSON strategy only.
    """
    
    def __init__(self):
        self.name = "Cover Letter Agent"
    
    def plan_cover_letter(
        self,
        job: Dict[str, Any],
        candidate_profile: Dict[str, Any]
    ) -> str:
        """
        Plan cover letter strategy for specific job
        
        Args:
            job: Job listing data
            candidate_profile: Candidate information
        
        Returns:
            JSON string with cover letter strategy
        """
        strategy = {
            "agent": self.name,
            "job_id": job.get("id"),
            "strategy": {
                "tone": "professional but personable",
                "key_stories": [
                    "Relevant project experience",
                    "Problem-solving example",
                    "Team collaboration success"
                ],
                "company_alignment": [
                    "Company mission relevance",
                    "Tech stack interest",
                    "Growth opportunity"
                ]
            },
            "structure": {
                "opening": "Hook with specific interest in company",
                "body": "2-3 paragraphs showing fit",
                "closing": "Clear call to action"
            },
            "personalization_level": "HIGH",
            "action": "GENERATE_COVER_LETTER"
        }
        
        return json.dumps(strategy, indent=2)


# Example usage
if __name__ == "__main__":
    agent = CoverLetterAgent()
    job = {"id": "job_001", "title": "Python Developer", "company": "TechCorp"}
    candidate = {"name": "John Doe", "experience_years": 5}
    result = agent.plan_cover_letter(job, candidate)
    print(result)
