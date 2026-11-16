from services.ats_scorer import ATSScorer
from services.nlp_service import compute_match_score, lexical_similarity
from services.resume_parser import ResumeParser
from utils.text_utils import parse_skills_list, clean_text

from tests.conftest import SAMPLE_RESUME


def test_parse_skills_list():
    assert parse_skills_list("Python, React; SQL | Docker") == ["python", "react", "sql", "docker"]
    assert parse_skills_list("") == []


def test_clean_text_collapses_whitespace():
    assert clean_text("  a \n\n b\t c ") == "a b c"


def test_keyword_match_reports_missing():
    score, missing = ATSScorer.keyword_match_score("Python, Kubernetes", SAMPLE_RESUME, "")
    assert score == 50.0
    assert missing == ["kubernetes"]


def test_ats_score_in_range():
    result = ATSScorer.compute_ats_score(
        "Python, FastAPI, Docker", SAMPLE_RESUME, "python", "B.S. Computer Science",
        "Senior Software Engineer at Acme Corp building APIs", "resume.pdf",
    )
    assert 0 <= result["ats_score"] <= 100
    assert result["missing_skills"] == ""


def test_parser_extracts_fields():
    assert ResumeParser.extract_email(SAMPLE_RESUME) == "jane.doe@example.com"
    assert "555" in ResumeParser.extract_phone(SAMPLE_RESUME)
    assert ResumeParser.extract_name(SAMPLE_RESUME) == "Jane Doe"
    skills = ResumeParser.extract_skills(SAMPLE_RESUME).lower()
    assert "python" in skills and "docker" in skills
    assert "computer science" in ResumeParser.extract_education(SAMPLE_RESUME).lower()


def test_match_score_prefers_relevant_resume():
    job = "Python backend engineer with FastAPI, Docker and AWS"
    relevant = compute_match_score(job, SAMPLE_RESUME)
    irrelevant = compute_match_score(job, "Pastry chef skilled in baking bread and cakes")
    assert 0 <= irrelevant < relevant <= 100
    assert lexical_similarity("", "x") == 0.0


def test_skill_extraction_uses_word_boundaries():
    skills = [s.strip() for s in ResumeParser.extract_skills("Worked at Google using JavaScript and PostgreSQL.\n").split(",")]
    assert "javascript" in skills and "postgresql" in skills
    assert "java" not in skills and "sql" not in skills and "go" not in skills
    cpp = ResumeParser.extract_skills("Proficient in C++ and C#.\n")
    assert "c++" in cpp and "c#" in cpp
