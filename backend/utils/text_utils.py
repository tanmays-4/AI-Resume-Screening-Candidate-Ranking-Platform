"""Text cleaning utilities for resume and job description processing."""

import re


def clean_text(text: str) -> str:
    """Normalize whitespace and remove special characters from text."""
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    return text.strip()


def extract_keywords(text: str) -> set:
    """Extract lowercase keyword tokens from text."""
    if not text:
        return set()
    tokens = re.findall(r"[a-zA-Z+#.]{2,}", text.lower())
    return set(tokens)


def parse_skills_list(skills_str: str) -> list:
    """Parse comma/semicolon separated skills into a list."""
    if not skills_str:
        return []
    parts = re.split(r"[,;|\n]", skills_str)
    return [s.strip().lower() for s in parts if s.strip()]
