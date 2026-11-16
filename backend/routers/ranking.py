"""Candidate ranking and CSV export routes."""

import csv
import io
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.job import Job
from schemas.schemas import RankRequest, RankResponse
from auth.jwt_handler import require_recruiter
from services.ranking_service import RankingService

router = APIRouter(tags=["Ranking"])


@router.post("/rank", response_model=RankResponse)
async def rank_candidates(
    request: RankRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """
    Rank all candidates against a selected job description.
    Computes semantic similarity and ATS scores, returns sorted results.
    """
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return RankingService.rank_candidates(
        db=db,
        job=job,
        skills_filter=request.skills_filter,
        experience_filter=request.experience_filter,
        education_filter=request.education_filter,
        min_match_score=request.min_match_score,
        min_ats_score=request.min_ats_score,
        sort_by=request.sort_by,
        sort_order=request.sort_order,
        page=request.page,
        page_size=request.page_size,
    )


@router.post("/rank/export")
async def export_ranked_csv(
    request: RankRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Export ranked candidates as CSV download."""
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get all results without pagination for export
    result = RankingService.rank_candidates(
        db=db,
        job=job,
        skills_filter=request.skills_filter,
        experience_filter=request.experience_filter,
        education_filter=request.education_filter,
        min_match_score=request.min_match_score,
        min_ats_score=request.min_ats_score,
        sort_by=request.sort_by,
        sort_order=request.sort_order,
        page=1,
        page_size=10000,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Name", "Email", "Match Score", "ATS Score",
        "Skills", "Missing Skills", "Education", "Experience",
    ])
    for r in result.results:
        writer.writerow([
            r.rank, r.candidate_name, r.email, r.match_score, r.ats_score,
            r.skills, r.missing_skills, r.education, r.experience,
        ])

    output.seek(0)
    safe_title = re.sub(r"[^A-Za-z0-9_-]+", "_", job.title).strip("_") or "job"
    filename = f"ranked_candidates_{safe_title}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
