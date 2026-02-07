"""
Shared data models for the job application platform.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class JobListing(BaseModel):
    """Job listing model"""
    id: str
    title: str
    company: str
    description: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    location: str
    job_url: str
    source: str  # linkedin, indeed, etc.
    posted_date: datetime
    requirements: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Resume(BaseModel):
    """Resume model"""
    id: str
    user_id: str
    original_content: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MatchScore(BaseModel):
    """Match score between job and candidate"""
    job_id: str
    user_id: str
    eligibility_score: float  # 0-100
    similarity_score: float  # 0-100
    combined_score: float  # 0-100
    matched_skills: List[str]
    missing_skills: List[str]
    reasoning: str


class ApplicationRecord(BaseModel):
    """Job application record"""
    id: str
    job_id: str
    user_id: str
    status: str  # pending, applied, rejected, interview
    resume_version: int
    cover_letter: Optional[str] = None
    applied_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
