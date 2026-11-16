# AI Resume Screening & Candidate Ranking Platform

Production-quality full-stack application for AI-powered resume screening, ATS scoring, and candidate ranking.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, Tailwind CSS, Recharts, React Router |
| Backend | FastAPI (async), SQLAlchemy, JWT Auth |
| Database | PostgreSQL |
| NLP | sentence-transformers (`all-MiniLM-L6-v2`) |
| Resume Parsing | pdfplumber, python-docx |

## Features

### Authentication
- Register / Login with JWT
- Role-based access (Recruiter / Candidate)
- Protected routes

### Candidate
- Upload PDF/DOCX resumes
- Auto-extract name, email, phone, skills, education, experience
- Profile dashboard

### Recruiter
- Create job descriptions
- View all candidates and resumes
- AI semantic matching (0–100%)
- ATS compatibility scoring (0–100)
- Rank, search, filter, sort candidates
- Analytics dashboard with charts
- Export ranked candidates as CSV

## Project Structure

```
ai_resume_screening_platform/
├── docker-compose.yml   # Postgres + backend + frontend
├── backend/
│   ├── main.py
│   ├── seed.py          # demo data loader
│   ├── routers/         # auth, candidates, jobs, ranking, analytics
│   ├── models/          # User, Candidate, Recruiter, Job, Resume, Score
│   ├── database/        # SQLAlchemy connection
│   ├── services/        # resume_parser, nlp_service, ats_scorer, ranking
│   ├── auth/            # JWT handler
│   ├── schemas/         # Pydantic schemas
│   ├── tests/           # pytest suite
│   └── requirements.txt
└── frontend/
    └── src/
        ├── pages/       # Login, Register, Dashboards, Jobs, Rank, Analytics
        ├── components/  # Layout, Navbar, ProtectedRoute, etc.
        ├── utils/       # error helpers
        └── api/         # Axios client
```

## Quick Start (Docker, everything)

```bash
docker compose up --build
```

- App: http://localhost:8080
- API docs: http://localhost:8000/docs

Load demo data (optional):

```bash
docker compose exec backend python seed.py
```

## Manual Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (or SQLite for a quick local run)

### 1. Database

```bash
docker compose up -d postgres
```

Or create it yourself: `CREATE DATABASE resume_screening;`

No Postgres? Set `DATABASE_URL=sqlite:///./resume_screening.db` in `backend/.env`.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # then edit as needed
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

The first ranking request downloads the `all-MiniLM-L6-v2` model (~90 MB).
If the model or `sentence-transformers` is unavailable, the service falls back
to a lexical (term-frequency cosine) matcher; set `NLP_BACKEND=lexical` to force it.

Demo data (1 recruiter, 3 jobs, 4 candidates; password `demo1234`):

```bash
python seed.py
```

Run the tests:

```bash
pip install -r requirements-dev.txt
pytest
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 (requests to `/api/*` are proxied to the backend).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register user |
| POST | `/login` | Login, get JWT |
| POST | `/upload-resume` | Upload & parse resume (candidate) |
| GET | `/candidate/me/profile` | Current candidate's profile |
| POST | `/create-job` | Create job description (recruiter) |
| GET | `/jobs` | List jobs |
| GET | `/jobs/{id}` | Get a job |
| DELETE | `/jobs/{id}` | Delete own job (recruiter) |
| GET | `/candidates` | List candidates (recruiter) |
| GET | `/candidate/{id}` | Candidate profile (recruiter, or self) |
| DELETE | `/candidate/{id}` | Delete candidate + account (recruiter) |
| POST | `/rank` | Rank candidates for a job |
| POST | `/rank/export` | Export ranked CSV |
| GET | `/analytics` | Analytics data (recruiter) |
| GET | `/resume/{id}/preview` | Download resume file (recruiter, or owner) |

## Scoring Algorithms

### Semantic Match Score (0–100%)
1. Encode job description and resume using `all-MiniLM-L6-v2`
2. Compute cosine similarity
3. Normalize to 0–100 scale

### ATS Score (0–100)
Weighted combination of:
- **Keyword matching** (45%) — required skills vs resume
- **Formatting** (25%) — length, special chars, section headers
- **Content** (30%) — education, experience, contact info presence

## Usage Flow

1. **Register** as Recruiter or Candidate
2. **Candidate**: Upload resume → profile auto-populated
3. **Recruiter**: Create job → Rank Candidates → view scores (only candidates with an uploaded resume are ranked)
4. **Analytics**: Review pipeline metrics and charts
5. **Export**: Download ranked results as CSV

## License

MIT
