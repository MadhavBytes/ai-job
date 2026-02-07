"""
Job Fetcher Service - Fetches and normalizes job listings
Coordinates job source adapters to retrieve jobs from various platforms.
"""
from fastapi import FastAPI, HTTPException
import logging
from typing import List, Dict, Any

from .sources import FoorillaJobSource

app = FastAPI(title="Job Fetcher Service")
logger = logging.getLogger(__name__)


class JobFetcher:
    """
    Coordinates fetching jobs from multiple sources
    
    Architecture:
    - Each job source has its own adapter (sources/adapter_name.py)
    - Adapters handle all source-specific logic (API, scraping, normalization)
    - JobFetcher orchestrates adapter selection and response formatting
    - All job data is normalized to common schema before returning
    """
    
    def __init__(self):
        """Initialize job fetcher with available sources"""
        self.sources = {
            "foorilla": FoorillaJobSource()
        }
        logger.info(f"Initialized JobFetcher with sources: {list(self.sources.keys())}")
    
    def get_available_sources(self) -> List[str]:
        """Get list of available job sources"""
        return list(self.sources.keys())
    
    def fetch_jobs(self, source: str, query: str, location: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch jobs from specified source
        
        Args:
            source: Job source name (e.g., "foorilla")
            query: Job search keyword
            location: Job location filter
            limit: Maximum number of results
        
        Returns:
            List of normalized job dictionaries
        
        Raises:
            ValueError: If source is not available
        """
        if source not in self.sources:
            available = ", ".join(self.sources.keys())
            raise ValueError(f"Source '{source}' not available. Available: {available}")
        
        logger.info(f"Fetching {limit} jobs from '{source}': query='{query}', location='{location}'")
        
        try:
            adapter = self.sources[source]
            jobs = adapter.search_jobs(query, location, limit)
            logger.info(f"Fetched {len(jobs)} jobs from '{source}'")
            return jobs
        
        except Exception as e:
            logger.error(f"Error fetching from '{source}': {e}", exc_info=True)
            raise


job_fetcher = JobFetcher()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "job-fetcher"}


@app.get("/sources")
async def list_sources():
    """
    List available job sources
    
    Returns:
        {
            "available_sources": ["foorilla", ...],
            "count": 1
        }
    """
    sources = job_fetcher.get_available_sources()
    return {
        "available_sources": sources,
        "count": len(sources)
    }


@app.post("/search")
async def search_jobs(
    source: str,
    query: str,
    location: str,
    limit: int = 50
):
    """
    Search for jobs on specified source
    
    Args:
        source: Job source name (e.g., "foorilla")
        query: Job search keyword
        location: Job location filter
        limit: Maximum results (default: 50, max: 200)
    
    Returns:
        {
            "success": true,
            "source": "foorilla",
            "query": "Python Developer",
            "location": "Remote",
            "count": 25,
            "jobs": [...]
        }
    """
    try:
        # Validate limit
        limit = min(int(limit), 200)
        limit = max(limit, 1)
        
        # Search using job fetcher
        jobs = job_fetcher.fetch_jobs(source, query, location, limit)
        
        return {
            "success": True,
            "source": source,
            "query": query,
            "location": location,
            "count": len(jobs),
            "jobs": jobs
        }
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching from '{source}': {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
