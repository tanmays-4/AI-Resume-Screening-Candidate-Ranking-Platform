"""Resume parsing service using pdfplumber and python-docx."""

import re
from pathlib import Path
from typing import Dict

import pdfplumber
from docx import Document

from utils.text_utils import clean_text


# Common technical skills for extraction
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "node.js", "nodejs",
    "sql", "postgresql", "mysql", "mongodb", "redis", "docker", "kubernetes",
    "aws", "azure", "gcp", "fastapi", "django", "flask", "spring", "c++",
    "c#", "go", "rust", "html", "css", "tailwind", "git", "linux", "agile",
    "scrum", "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "data analysis", "rest api", "graphql",
    "microservices", "ci/cd", "jenkins", "terraform", "ansible", "kafka",
    "spark", "hadoop", "tableau", "power bi", "excel", "communication",
    "leadership", "project management", "problem solving", "teamwork",
]


class ResumeParser:
    """Extract structured data from PDF and DOCX resume files."""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract raw text from a PDF file."""
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract raw text from a DOCX file."""
        doc = Document(file_path)
        lines = [p.text for p in doc.paragraphs if p.text.strip()]
        # Many resume templates put content inside tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip() and cell.text not in lines:
                        lines.append(cell.text)
        return "\n".join(lines)

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """Extract text based on file extension."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return cls.extract_text_from_pdf(file_path)
        if ext == ".docx":
            return cls.extract_text_from_docx(file_path)
        raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def extract_email(text: str) -> str:
        """Find email address in resume text."""
        match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_phone(text: str) -> str:
        """Find phone number in resume text."""
        patterns = [
            r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
            r"\d{10}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""

    @staticmethod
    def extract_name(text: str) -> str:
        """Heuristic name extraction from first lines of resume."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:5]:
            # Skip lines that look like contact info
            if "@" in line or re.search(r"\d{3}.*\d{3}", line):
                continue
            if 2 <= len(line.split()) <= 4 and len(line) < 50:
                if line[0].isupper():
                    return line
        return lines[0][:50] if lines else "Unknown"

    @staticmethod
    def extract_skills(text: str) -> str:
        """Extract known skills from resume text."""
        text_lower = text.lower()
        # Word-boundary match so "java" doesn't hit "javascript", "go" doesn't hit "google", etc.
        found = [
            skill for skill in COMMON_SKILLS
            if re.search(rf"(?<![\w+#.]){re.escape(skill)}(?![\w+#])", text_lower)
        ]
        if "nodejs" in found and "node.js" in found:
            found.remove("nodejs")
        found_lower = set(found)
        # Also look for a Skills section
        skills_section = re.search(
            r"(?:skills|technical skills|core competencies)[:\s]*(.+?)(?:\n\n|\n[A-Z])",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if skills_section:
            section_skills = re.split(r"[,;|•\n]", skills_section.group(1))
            for s in section_skills:
                s = s.strip()
                if s and len(s) < 40 and s.lower() not in found_lower:
                    found.append(s)
                    found_lower.add(s.lower())
        return ", ".join(found[:30])

    @staticmethod
    def extract_education(text: str) -> str:
        """Extract education section from resume."""
        patterns = [
            r"(?:education|academic background)[:\s]*(.+?)(?:\n\n|experience|skills|projects|$)",
            r"(?:b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?|bachelor|master|degree).+",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                edu = match.group(0) if match.lastindex is None else match.group(1)
                return clean_text(edu)[:500]
        return ""

    @staticmethod
    def extract_experience(text: str) -> str:
        """Extract work experience section from resume."""
        patterns = [
            r"(?:experience|work experience|employment history|professional experience)[:\s]*(.+?)(?:\n\n(?:education|skills|projects|certifications)|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return clean_text(match.group(1))[:1000]
        return ""

    @classmethod
    def parse_resume(cls, file_path: str) -> Dict[str, str]:
        """Full resume parse pipeline returning structured fields."""
        raw_text = cls.extract_text(file_path)
        cleaned = clean_text(raw_text)

        return {
            "parsed_text": cleaned,
            "name": cls.extract_name(raw_text),
            "email": cls.extract_email(raw_text),
            "phone": cls.extract_phone(raw_text),
            "skills": cls.extract_skills(raw_text),
            "education": cls.extract_education(raw_text),
            "experience": cls.extract_experience(raw_text),
        }
