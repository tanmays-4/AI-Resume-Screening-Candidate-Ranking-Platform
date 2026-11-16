"""Shared fixtures: isolated SQLite DB, temp upload dir, lexical NLP backend."""

import io
import os
import sys
import tempfile
from pathlib import Path

import pytest

_TMP = tempfile.mkdtemp(prefix="resume_tests_")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["UPLOAD_DIR"] = f"{_TMP}/uploads"
os.environ["NLP_BACKEND"] = "lexical"
os.environ["SECRET_KEY"] = "test-secret"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402
from database.connection import Base, engine  # noqa: E402


SAMPLE_RESUME = """Jane Doe
jane.doe@example.com | +1 555-123-4567

Summary
Backend engineer with 5 years of experience building APIs.

Skills
Python, FastAPI, PostgreSQL, Docker, AWS, React

Experience
Senior Software Engineer at Acme Corp (2020 - Present)
Built microservices with Python and FastAPI, deployed on AWS with Docker.

Education
B.S. in Computer Science, State University, 2018
"""


def make_docx(text: str = SAMPLE_RESUME) -> bytes:
    from docx import Document

    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def _register(client, email, role, **extra):
    r = client.post("/register", json={"email": email, "password": "secret123", "role": role, **extra})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def recruiter_headers(client):
    return _register(client, "rec@example.com", "recruiter", company="Acme")


@pytest.fixture()
def candidate_headers(client):
    return _register(client, "cand@example.com", "candidate", name="Jane Doe")


@pytest.fixture()
def register():
    return _register
