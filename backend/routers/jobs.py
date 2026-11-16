"""Job description routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.recruiter import Recruiter
from models.job import Job
from schemas.schemas import JobCreate, JobResponse, MessageResponse
from auth.jwt_handler import require_recruiter, get_current_user

router = APIRouter(tags=["Jobs"])


@router.post("/create-job", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Create a new job description."""
    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")

    job = Job(
        recruiter_id=recruiter.id,
        title=job_data.title,
        description=job_data.description,
        required_skills=job_data.required_skills,
        experience=job_data.experience,
        location=job_data.location,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all job descriptions."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return jobs


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single job description."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/jobs/{job_id}", response_model=MessageResponse)
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Delete a job description."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
    if not recruiter or job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=403, detail="You can only delete your own jobs")

    db.delete(job)
    db.commit()
    return MessageResponse(message="Job deleted successfully")
