"""
Celery configuration for async task execution
"""
from celery import Celery
import os

# Initialize Celery app
app = Celery(
    'job_platform',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)


# Define async tasks
@app.task
def fetch_jobs_task(source: str, query: str, location: str):
    """Async job fetching"""
    from services.job_fetcher.main import JobFetcher
    fetcher = JobFetcher()
    return fetcher.fetch_jobs(source, query, location)


@app.task
def match_job_task(job: dict, resume: str, skills: list):
    """Async job matching"""
    from services.matching_engine.main import MatchingEngine
    matcher = MatchingEngine()
    result = matcher.match_job_to_candidate(job, resume, skills)
    return {
        "job_id": result.job_id,
        "combined_score": result.combined_score,
        "matched_skills": result.matched_skills
    }


@app.task
def apply_job_task(job_url: str, resume: str, cover_letter: str, user_data: dict):
    """Async job application"""
    from services.apply_engine.main import ApplicationExecutor
    executor = ApplicationExecutor()
    return executor.submit_application(job_url, resume, cover_letter, user_data)
