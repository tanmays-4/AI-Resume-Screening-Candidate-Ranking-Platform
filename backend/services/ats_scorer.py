"""ATS (Applicant Tracking System) compatibility scoring service."""

import re
from typing import Dict, List

from utils.text_utils import parse_skills_list, clean_text


class ATSScorer:
    """
    Compute ATS compatibility score (0-100) based on:
    - Keyword matching
    - Missing skills
    - Formatting checks
    - Resume length
    - Education presence
    - Experience presence
    """

    @staticmethod
    def keyword_match_score(required_skills: str, resume_text: str, candidate_skills: str) -> tuple:
        """Score keyword overlap between job requirements and resume."""
        required = parse_skills_list(required_skills)
        if not required:
            return 100.0, []

        combined = f"{resume_text} {candidate_skills}".lower()
        matched = []
        missing = []

        for skill in required:
            # Flexible matching: allow partial matches for multi-word skills
            skill_pattern = re.escape(skill).replace(r"\ ", r"[\s-]?")
            if re.search(skill_pattern, combined, re.IGNORECASE):
                matched.append(skill)
            else:
                missing.append(skill)

        score = (len(matched) / len(required)) * 100
        return round(score, 2), missing

    @staticmethod
    def formatting_score(resume_text: str, file_name: str) -> float:
        """Check resume formatting quality for ATS parsing."""
        score = 100.0
        text = resume_text or ""

        # Penalize very short resumes
        if len(text) < 200:
            score -= 30
        elif len(text) < 500:
            score -= 15

        # Penalize excessive special characters (bad for ATS)
        special_ratio = len(re.findall(r"[^\w\s.,;:@#\-+/()]", text)) / max(len(text), 1)
        if special_ratio > 0.05:
            score -= 20

        # Reward standard file formats
        if file_name.lower().endswith((".pdf", ".docx")):
            pass  # Good format
        else:
            score -= 10

        # Check for section headers (good structure)
        headers = ["experience", "education", "skills", "summary", "objective"]
        found_headers = sum(1 for h in headers if h in text.lower())
        if found_headers >= 2:
            score += 5
        elif found_headers == 0:
            score -= 15

        return max(0.0, min(100.0, score))

    @staticmethod
    def content_score(education: str, experience: str, resume_text: str) -> float:
        """Score based on presence of education and experience sections."""
        score = 0.0
        text_lower = (resume_text or "").lower()

        # Education presence (25 points)
        if education and len(education.strip()) > 10:
            score += 25
        elif any(kw in text_lower for kw in ["bachelor", "master", "degree", "university", "college", "b.s", "m.s"]):
            score += 20

        # Experience presence (25 points)
        if experience and len(experience.strip()) > 20:
            score += 25
        elif any(kw in text_lower for kw in ["experience", "worked", "employed", "intern", "developer", "engineer"]):
            score += 20

        # Skills presence (20 points)
        if any(kw in text_lower for kw in ["skills", "proficient", "expertise", "technologies"]):
            score += 20

        # Contact info presence (10 points)
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", resume_text or ""):
            score += 10

        # Length appropriateness (20 points)
        length = len(resume_text or "")
        if 500 <= length <= 5000:
            score += 20
        elif 200 <= length < 500:
            score += 10

        return min(100.0, score)

    @classmethod
    def compute_ats_score(
        cls,
        required_skills: str,
        resume_text: str,
        candidate_skills: str,
        education: str,
        experience: str,
        file_name: str = "",
    ) -> Dict:
        """
        Compute overall ATS score as weighted average of sub-scores.
        Returns score and missing skills list.
        """
        keyword_score, missing = cls.keyword_match_score(
            required_skills, resume_text, candidate_skills
        )
        format_score = cls.formatting_score(resume_text, file_name)
        content_score = cls.content_score(education, experience, resume_text)

        # Weighted average
        ats_score = keyword_score * 0.45 + format_score * 0.25 + content_score * 0.30
        ats_score = round(max(0.0, min(100.0, ats_score)), 2)

        return {
            "ats_score": ats_score,
            "missing_skills": ", ".join(missing),
            "keyword_score": keyword_score,
            "format_score": round(format_score, 2),
            "content_score": round(content_score, 2),
        }
