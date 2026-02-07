"""Base adapter for job sources"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class JobSourceAdapter(ABC):
    """Abstract base class for job source adapters"""
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of the job source
        
        Returns:
            str: Source identifier (e.g., "foorilla", "linkedin")
        """
        pass
    
    @abstractmethod
    def search_jobs(self, query: str, location: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs on this source
        
        Args:
            query: Job search keyword/title
            location: Job location filter
            limit: Maximum number of results to return
        
        Returns:
            List of normalized job dictionaries
            Empty list if search fails or no results found
        """
        pass
    
    def normalize_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw job data to common JobListing schema
        
        Common schema:
        {
            "id": str,
            "title": str,
            "company": str,
            "description": str,
            "location": str,
            "job_url": str,
            "source": str,
            "posted_date": str (ISO format),
            "salary_min": Optional[float],
            "salary_max": Optional[float],
            "requirements": List[str]
        }
        
        Args:
            job: Raw job data from source
        
        Returns:
            Normalized job dictionary
        """
        return {
            "id": job.get("id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "description": job.get("description", ""),
            "location": job.get("location", ""),
            "job_url": job.get("job_url", ""),
            "source": self.get_source_name(),
            "posted_date": job.get("posted_date", ""),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "requirements": job.get("requirements", [])
        }
