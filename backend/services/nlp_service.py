"""NLP service using sentence-transformers for semantic similarity.

If sentence-transformers (or the model download) is unavailable, the service
falls back to a lightweight bag-of-words TF cosine similarity so the API keeps
working offline. Set NLP_BACKEND=lexical to force the fallback.
"""

import logging
import math
import os
import re
from collections import Counter
from functools import lru_cache

import numpy as np

from utils.text_utils import clean_text

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("NLP_MODEL", "all-MiniLM-L6-v2")

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "of", "on", "or", "our", "that", "the", "to", "was", "we",
    "will", "with", "you", "your", "this", "their", "they", "who", "can", "all",
}


@lru_cache(maxsize=1)
def get_model():
    """Load and cache the sentence-transformer model (None if unavailable)."""
    if os.getenv("NLP_BACKEND", "").lower() == "lexical":
        return None
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(MODEL_NAME)
    except Exception as exc:  # ImportError, network errors, etc.
        logger.warning("Semantic model unavailable (%s); using lexical fallback.", exc)
        return None


@lru_cache(maxsize=1024)
def _encode_cached(cleaned: str) -> np.ndarray:
    return get_model().encode(cleaned, convert_to_numpy=True)


def encode_text(text: str) -> np.ndarray:
    """Encode text into an embedding vector (cached per unique text)."""
    cleaned = clean_text(text) or "empty"
    return _encode_cached(cleaned)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def _tokens(text: str) -> Counter:
    words = re.findall(r"[a-z0-9+#.]{2,}", (text or "").lower())
    return Counter(w.strip(".") for w in words if w not in _STOPWORDS)


def lexical_similarity(text_a: str, text_b: str) -> float:
    """Cosine similarity between term-frequency vectors (0..1)."""
    a, b = _tokens(text_a), _tokens(text_b)
    if not a or not b:
        return 0.0
    dot = sum(a[t] * b[t] for t in a.keys() & b.keys())
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def compute_match_score(job_text: str, resume_text: str) -> float:
    """
    Compute semantic match score (0-100) between job description and resume.
    Uses sentence-transformers embeddings and cosine similarity.
    """
    if get_model() is None:
        # TF cosine is typically 0..0.6 for related docs; stretch to a 0-100 scale
        similarity = lexical_similarity(job_text, resume_text)
        return round(max(0.0, min(100.0, math.sqrt(similarity) * 100)), 2)

    job_embedding = encode_text(job_text)
    resume_embedding = encode_text(resume_text)
    similarity = cosine_similarity(job_embedding, resume_embedding)
    # Map cosine similarity (-1 to 1) to 0-100 scale
    score = max(0.0, min(100.0, (similarity + 0.2) / 1.2 * 100))
    return round(score, 2)


def build_job_text(title: str, description: str, required_skills: str, experience: str) -> str:
    """Combine job fields into a single text for encoding."""
    return clean_text(f"{title}. {description}. Skills: {required_skills}. Experience: {experience}")


def build_resume_text(
    skills: str, education: str, experience: str, parsed_text: str
) -> str:
    """Combine resume fields into a single text for encoding."""
    skills, education, experience = skills or "", education or "", experience or ""
    parsed_text = parsed_text or ""
    structured = f"Skills: {skills}. Education: {education}. Experience: {experience}."
    # Use parsed text if structured fields are sparse
    if len(structured) < 100 and parsed_text:
        return clean_text(parsed_text[:3000])
    return clean_text(f"{structured} {parsed_text[:2000]}")
