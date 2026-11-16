"""Analytics dashboard routes."""

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from models.user import User
from models.candidate import Candidate
from models.job import Job
from models.score import Score
from schemas.schemas import AnalyticsResponse
from auth.jwt_handler import require_recruiter

router = APIRouter(tags=["Analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Return analytics data for recruiter dashboard."""
    total_candidates = db.query(Candidate).count()
    total_jobs = db.query(Job).count()

    avg_ats = db.query(func.avg(Score.ats_score)).scalar() or 0.0
    avg_match = db.query(func.avg(Score.match_score)).scalar() or 0.0

    # Skills distribution
    candidates = db.query(Candidate).all()
    skill_counter = Counter()
    for c in candidates:
        if c.skills:
            for skill in c.skills.split(","):
                skill = skill.strip()
                if skill:
                    skill_counter[skill] += 1

    skills_distribution = [
        {"name": skill, "value": count}
        for skill, count in skill_counter.most_common(10)
    ]

    # Score distribution buckets
    scores = db.query(Score).all()
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for s in scores:
        score_val = s.match_score
        if score_val <= 20:
            buckets["0-20"] += 1
        elif score_val <= 40:
            buckets["21-40"] += 1
        elif score_val <= 60:
            buckets["41-60"] += 1
        elif score_val <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1

    score_distribution = [{"name": k, "value": v} for k, v in buckets.items()]

    # Top candidates by match score
    top_scores = (
        db.query(Score, Candidate)
        .join(Candidate, Candidate.id == Score.candidate_id)
        .order_by(Score.match_score.desc())
        .limit(5)
        .all()
    )
    top_candidates = [
        {
            "name": c.name,
            "match_score": s.match_score,
            "ats_score": s.ats_score,
        }
        for s, c in top_scores
    ]

    return AnalyticsResponse(
        total_candidates=total_candidates,
        total_jobs=total_jobs,
        avg_ats_score=round(float(avg_ats), 2),
        avg_match_score=round(float(avg_match), 2),
        skills_distribution=skills_distribution,
        score_distribution=score_distribution,
        top_candidates=top_candidates,
    )
