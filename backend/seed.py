"""Populate the database with demo data.

Usage (from backend/):  python seed.py

Creates one recruiter, three jobs and four candidates with generated DOCX
resumes, then scores every candidate against every job.
All demo accounts use the password: demo1234
"""

import os
import uuid

from dotenv import load_dotenv

load_dotenv()

from docx import Document  # noqa: E402

import models  # noqa: E402,F401
from auth.jwt_handler import get_password_hash  # noqa: E402
from database.connection import Base, SessionLocal, engine  # noqa: E402
from models import Candidate, Job, Recruiter, Resume, User  # noqa: E402
from models.user import UserRole  # noqa: E402
from services.ranking_service import RankingService  # noqa: E402
from services.resume_parser import ResumeParser  # noqa: E402

PASSWORD = "demo1234"
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/resumes")

JOBS = [
    {
        "title": "Senior Backend Engineer",
        "description": "Design and build scalable REST APIs and microservices. Own services end to end, "
        "from data modelling in PostgreSQL to deployment on AWS with Docker and Kubernetes.",
        "required_skills": "Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS",
        "experience": "5+ years",
        "location": "Remote",
    },
    {
        "title": "Frontend Developer",
        "description": "Build responsive, accessible user interfaces with React and TypeScript. "
        "Collaborate with designers and backend engineers to ship product features.",
        "required_skills": "JavaScript, TypeScript, React, HTML, CSS, Tailwind",
        "experience": "2+ years",
        "location": "New York, NY",
    },
    {
        "title": "Machine Learning Engineer",
        "description": "Train, evaluate and deploy NLP and deep learning models to production. "
        "Work with large datasets and build reliable ML pipelines.",
        "required_skills": "Python, PyTorch, TensorFlow, NLP, Machine Learning, Pandas, NumPy",
        "experience": "3+ years",
        "location": "San Francisco, CA",
    },
]

CANDIDATES = [
    ("alice@demo.com", """Alice Johnson
alice@demo.com | +1 415-555-0101

Summary
Backend engineer with 6 years of experience building high-traffic APIs.

Skills
Python, FastAPI, Django, PostgreSQL, Redis, Docker, Kubernetes, AWS, Git, CI/CD

Experience
Senior Software Engineer, CloudCorp (2020 - Present)
Led a team building microservices in Python and FastAPI on AWS EKS.
Software Engineer, DataWorks (2018 - 2020)
Built REST APIs with Django and PostgreSQL.

Education
B.S. Computer Science, University of Washington, 2018
"""),
    ("bob@demo.com", """Bob Martinez
bob@demo.com | +1 212-555-0144

Summary
Frontend developer passionate about clean UI and accessibility.

Skills
JavaScript, TypeScript, React, HTML, CSS, Tailwind, Git, Agile

Experience
Frontend Developer, PixelPerfect (2021 - Present)
Built React and TypeScript dashboards used by 50k users.

Education
B.A. Interactive Design, NYU, 2020
"""),
    ("carol@demo.com", """Carol Chen
carol@demo.com | +1 650-555-0199

Summary
ML engineer focused on NLP and deep learning.

Skills
Python, PyTorch, TensorFlow, NLP, Machine Learning, Deep Learning, Pandas, NumPy, Scikit-learn

Experience
Machine Learning Engineer, AI Labs (2021 - Present)
Trained transformer models for text classification and deployed them with Docker.

Education
M.S. Computer Science (Machine Learning), Stanford University, 2021
"""),
    ("dave@demo.com", """Dave Patel
dave@demo.com | +1 312-555-0177

Summary
Full-stack developer comfortable across the stack.

Skills
JavaScript, React, Node.js, Python, Flask, MySQL, Docker, Git

Experience
Full Stack Developer, StartupHub (2022 - Present)
Developed React frontends and Flask APIs backed by MySQL.

Education
B.S. Software Engineering, University of Illinois, 2022
"""),
]


def write_docx(text: str) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.docx")
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(path)
    return path


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "recruiter@demo.com").first():
            print("Demo data already present - skipping.")
            return

        rec_user = User(email="recruiter@demo.com", password_hash=get_password_hash(PASSWORD), role=UserRole.RECRUITER)
        db.add(rec_user)
        db.flush()
        recruiter = Recruiter(user_id=rec_user.id, company="Demo Corp")
        db.add(recruiter)
        db.flush()
        jobs = [Job(recruiter_id=recruiter.id, **j) for j in JOBS]
        db.add_all(jobs)

        for email, text in CANDIDATES:
            user = User(email=email, password_hash=get_password_hash(PASSWORD), role=UserRole.CANDIDATE)
            db.add(user)
            db.flush()
            path = write_docx(text)
            parsed = ResumeParser.parse_resume(path)
            cand = Candidate(
                user_id=user.id,
                name=parsed["name"],
                phone=parsed["phone"],
                skills=parsed["skills"],
                education=parsed["education"],
                experience=parsed["experience"],
            )
            db.add(cand)
            db.flush()
            db.add(Resume(candidate_id=cand.id, file_path=path, file_name=f"{parsed['name'].replace(' ', '_')}.docx",
                          parsed_text=parsed["parsed_text"]))
        db.commit()

        print("Scoring candidates (first run may download the NLP model)...")
        for job in jobs:
            RankingService.rank_candidates(db, job)

        print("Demo data created. Log in with password", repr(PASSWORD), "as:")
        print("  recruiter@demo.com")
        for email, _ in CANDIDATES:
            print(" ", email)
    finally:
        db.close()


if __name__ == "__main__":
    main()
