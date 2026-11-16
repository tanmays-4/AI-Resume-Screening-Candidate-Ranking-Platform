"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# --- Auth ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(recruiter|candidate)$")
    name: Optional[str] = ""
    company: Optional[str] = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


# --- Job ---

class JobCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10)
    required_skills: str = Field(..., min_length=1)
    experience: str = ""
    location: str = ""


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    required_skills: str
    experience: str
    location: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Candidate ---

class CandidateResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: Optional[str] = ""
    phone: str
    skills: str
    education: str
    experience: str
    created_at: datetime
    resume_count: int = 0
    latest_resume_id: Optional[int] = None

    model_config = {"from_attributes": True}


class CandidateDetail(CandidateResponse):
    resumes: List["ResumeResponse"] = []
    scores: List["ScoreResponse"] = []


# --- Resume ---

class ResumeResponse(BaseModel):
    id: int
    candidate_id: int
    file_path: str
    file_name: str
    parsed_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Score / Ranking ---

class RankRequest(BaseModel):
    job_id: int
    skills_filter: Optional[str] = None
    experience_filter: Optional[str] = None
    education_filter: Optional[str] = None
    min_match_score: Optional[float] = None
    min_ats_score: Optional[float] = None
    sort_by: str = "match_score"  # match_score | ats_score | name
    sort_order: str = "desc"  # asc | desc
    page: int = 1
    page_size: int = 20


class ScoreResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    match_score: float
    ats_score: float
    missing_skills: str
    created_at: datetime
    job_title: Optional[str] = None

    model_config = {"from_attributes": True}


class RankedCandidate(BaseModel):
    rank: int
    candidate_id: int
    candidate_name: str
    email: str
    skills: str
    education: str
    experience: str
    match_score: float
    ats_score: float
    missing_skills: str


class RankResponse(BaseModel):
    job_id: int
    job_title: str
    total: int
    page: int
    page_size: int
    results: List[RankedCandidate]


# --- Analytics ---

class AnalyticsResponse(BaseModel):
    total_candidates: int
    total_jobs: int
    avg_ats_score: float
    avg_match_score: float
    skills_distribution: List[dict]
    score_distribution: List[dict]
    top_candidates: List[dict]


class MessageResponse(BaseModel):
    message: str
