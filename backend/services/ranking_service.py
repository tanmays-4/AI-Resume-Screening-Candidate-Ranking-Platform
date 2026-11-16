"""Candidate ranking service combining NLP and ATS scoring."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from models.candidate import Candidate
from models.job import Job
from models.resume import Resume
from models.score import Score
from services.nlp_service import compute_match_score, build_job_text, build_resume_text
from services.ats_scorer import ATSScorer
from schemas.schemas import RankedCandidate, RankResponse


class RankingService:
    """Rank candidates against a job description."""

    @staticmethod
    def get_latest_resume(db: Session, candidate_id: int) -> Optional[Resume]:
        """Get the most recently uploaded resume for a candidate."""
        return (
            db.query(Resume)
            .filter(Resume.candidate_id == candidate_id)
            .order_by(Resume.created_at.desc(), Resume.id.desc())
            .first()
        )

    @classmethod
    def score_candidate(
        cls, db: Session, job: Job, candidate: Candidate, commit: bool = True
    ) -> Score:
        """Compute and persist match + ATS scores for a candidate against a job."""
        resume = cls.get_latest_resume(db, candidate.id)
        resume_text = resume.parsed_text if resume else ""
        file_name = resume.file_name if resume else ""

        job_text = build_job_text(
            job.title, job.description, job.required_skills, job.experience
        )
        candidate_text = build_resume_text(
            candidate.skills, candidate.education, candidate.experience, resume_text
        )

        match_score = compute_match_score(job_text, candidate_text)
        ats_result = ATSScorer.compute_ats_score(
            job.required_skills,
            resume_text,
            candidate.skills or "",
            candidate.education or "",
            candidate.experience or "",
            file_name,
        )

        # Upsert score record
        existing = (
            db.query(Score)
            .filter(Score.job_id == job.id, Score.candidate_id == candidate.id)
            .first()
        )
        if existing:
            existing.match_score = match_score
            existing.ats_score = ats_result["ats_score"]
            existing.missing_skills = ats_result["missing_skills"]
            score = existing
        else:
            score = Score(
                job_id=job.id,
                candidate_id=candidate.id,
                match_score=match_score,
                ats_score=ats_result["ats_score"],
                missing_skills=ats_result["missing_skills"],
            )
            db.add(score)

        if commit:
            db.commit()
            db.refresh(score)
        return score

    @classmethod
    def rank_candidates(
        cls,
        db: Session,
        job: Job,
        skills_filter: Optional[str] = None,
        experience_filter: Optional[str] = None,
        education_filter: Optional[str] = None,
        min_match_score: Optional[float] = None,
        min_ats_score: Optional[float] = None,
        sort_by: str = "match_score",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> RankResponse:
        """Score all candidates and return ranked, filtered, paginated results."""
        # Only candidates who have uploaded at least one resume can be scored
        candidates = (
            db.query(Candidate)
            .options(joinedload(Candidate.user))
            .filter(Candidate.resumes.any())
            .all()
        )

        # Score each candidate, then persist in a single transaction
        for candidate in candidates:
            cls.score_candidate(db, job, candidate, commit=False)
        db.commit()

        # Build query with scores
        query = (
            db.query(Candidate, Score)
            .join(Score, Score.candidate_id == Candidate.id)
            .filter(Score.job_id == job.id)
        )

        # Apply filters
        if skills_filter:
            query = query.filter(Candidate.skills.ilike(f"%{skills_filter}%"))
        if experience_filter:
            query = query.filter(Candidate.experience.ilike(f"%{experience_filter}%"))
        if education_filter:
            query = query.filter(Candidate.education.ilike(f"%{education_filter}%"))
        if min_match_score is not None:
            query = query.filter(Score.match_score >= min_match_score)
        if min_ats_score is not None:
            query = query.filter(Score.ats_score >= min_ats_score)

        results = query.all()

        # Sort
        reverse = sort_order == "desc"
        if sort_by == "ats_score":
            results.sort(key=lambda x: x[1].ats_score, reverse=reverse)
        elif sort_by == "name":
            results.sort(key=lambda x: (x[0].name or "").lower(), reverse=reverse)
        else:
            results.sort(key=lambda x: x[1].match_score, reverse=reverse)

        page = max(page, 1)
        page_size = max(1, page_size)
        total = len(results)
        start = (page - 1) * page_size
        page_results = results[start : start + page_size]

        ranked = []
        for idx, (candidate, score) in enumerate(page_results, start=start + 1):
            email = candidate.user.email if candidate.user else ""
            ranked.append(
                RankedCandidate(
                    rank=idx,
                    candidate_id=candidate.id,
                    candidate_name=candidate.name or "Unknown",
                    email=email,
                    skills=candidate.skills or "",
                    education=candidate.education or "",
                    experience=candidate.experience or "",
                    match_score=score.match_score,
                    ats_score=score.ats_score,
                    missing_skills=score.missing_skills or "",
                )
            )

        return RankResponse(
            job_id=job.id,
            job_title=job.title,
            total=total,
            page=page,
            page_size=page_size,
            results=ranked,
        )
