"""Candidate and resume routes."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from database.connection import get_db
from models.user import User, UserRole
from models.candidate import Candidate
from models.resume import Resume
from schemas.schemas import (
    CandidateResponse,
    CandidateDetail,
    ResumeResponse,
    MessageResponse,
    ScoreResponse,
)
from auth.jwt_handler import get_current_user, require_candidate, require_recruiter
from services.resume_parser import ResumeParser

router = APIRouter(tags=["Candidates"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/resumes")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _candidate_to_response(candidate: Candidate) -> CandidateResponse:
    """Convert Candidate ORM object to response schema."""
    return CandidateResponse(
        id=candidate.id,
        user_id=candidate.user_id,
        name=candidate.name or "",
        email=candidate.user.email if candidate.user else "",
        phone=candidate.phone or "",
        skills=candidate.skills or "",
        education=candidate.education or "",
        experience=candidate.experience or "",
        created_at=candidate.created_at,
        resume_count=len(candidate.resumes),
        latest_resume_id=candidate.resumes[-1].id if candidate.resumes else None,
    )


def _candidate_to_detail(candidate: Candidate) -> CandidateDetail:
    """Convert Candidate ORM object to detailed response with resumes and scores."""
    base = _candidate_to_response(candidate).model_dump()
    scores = []
    for s in candidate.scores:
        score = ScoreResponse.model_validate(s)
        score.job_title = s.job.title if s.job else None
        scores.append(score)
    scores.sort(key=lambda s: s.match_score, reverse=True)
    return CandidateDetail(
        **base,
        resumes=[ResumeResponse.model_validate(r) for r in candidate.resumes],
        scores=scores,
    )


def _load_candidate(db: Session, **filters) -> Candidate | None:
    query = db.query(Candidate).options(
        joinedload(Candidate.user),
        joinedload(Candidate.resumes),
        joinedload(Candidate.scores),
    )
    for key, value in filters.items():
        query = query.filter(getattr(Candidate, key) == value)
    return query.first()


@router.post("/upload-resume", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    """Upload and parse a resume (PDF or DOCX)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Upload a PDF or DOCX file.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )

    candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    # Save file locally under a random name (never trust the client filename)
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse resume
    try:
        parsed = ResumeParser.parse_resume(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")

    if not parsed["parsed_text"].strip():
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted. Scanned/image-only resumes are not supported.",
        )

    # Update candidate profile with extracted data
    if parsed["name"] and parsed["name"] != "Unknown" and not candidate.name:
        candidate.name = parsed["name"]
    for field in ("phone", "skills", "education", "experience"):
        if parsed[field]:
            setattr(candidate, field, parsed[field])

    resume = Resume(
        candidate_id=candidate.id,
        file_path=file_path,
        file_name=Path(file.filename).name,
        parsed_text=parsed["parsed_text"],
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


@router.get("/candidates", response_model=list[CandidateResponse])
async def list_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
    search: str = "",
    page: int = 1,
    page_size: int = 50,
):
    """List all candidates (recruiter only)."""
    page = max(page, 1)
    page_size = max(1, min(page_size, 200))
    query = db.query(Candidate).options(joinedload(Candidate.user), joinedload(Candidate.resumes))
    if search:
        query = query.filter(
            (Candidate.name.ilike(f"%{search}%"))
            | (Candidate.skills.ilike(f"%{search}%"))
            | (Candidate.education.ilike(f"%{search}%"))
        )
    candidates = (
        query.order_by(Candidate.created_at.desc(), Candidate.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    # joinedload on a collection can duplicate parent rows; dedupe while keeping order
    seen, unique = set(), []
    for c in candidates:
        if c.id not in seen:
            seen.add(c.id)
            unique.append(c)
    return [_candidate_to_response(c) for c in unique]


# NOTE: this static route must be declared before /candidate/{candidate_id},
# otherwise "me" is matched as a candidate_id and fails int validation.
@router.get("/candidate/me/profile", response_model=CandidateDetail)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate),
):
    """Get current candidate's own profile."""
    candidate = _load_candidate(db, user_id=current_user.id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return _candidate_to_detail(candidate)


@router.get("/candidate/{candidate_id}", response_model=CandidateDetail)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed candidate profile (recruiters, or the candidate themselves)."""
    candidate = _load_candidate(db, id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if current_user.role != UserRole.RECRUITER and candidate.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to view this profile")

    return _candidate_to_detail(candidate)


@router.delete("/candidate/{candidate_id}", response_model=MessageResponse)
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Delete a candidate, their account and their resumes (recruiter only)."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Remove resume files from disk
    for resume in candidate.resumes:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)

    user = candidate.user
    if user is not None:
        db.delete(user)  # cascades to candidate -> resumes, scores
    else:
        db.delete(candidate)
    db.commit()
    return MessageResponse(message="Candidate deleted successfully")


@router.get("/resume/{resume_id}/preview")
async def preview_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download/preview an uploaded resume file."""
    resume = (
        db.query(Resume)
        .options(joinedload(Resume.candidate))
        .filter(Resume.id == resume_id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if current_user.role != UserRole.RECRUITER and resume.candidate.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this resume")

    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on disk")

    ext = Path(resume.file_path).suffix.lower()
    return FileResponse(
        path=resume.file_path,
        filename=resume.file_name,
        media_type=MEDIA_TYPES.get(ext, "application/octet-stream"),
    )
