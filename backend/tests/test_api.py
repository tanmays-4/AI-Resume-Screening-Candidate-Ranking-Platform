from tests.conftest import make_docx

JOB = {
    "title": "Backend Engineer",
    "description": "Build Python APIs with FastAPI and PostgreSQL on AWS.",
    "required_skills": "Python, FastAPI, Kubernetes",
    "experience": "3+ years",
    "location": "Remote",
}


def upload(client, headers, name="resume.docx", content=None):
    return client.post(
        "/upload-resume",
        headers=headers,
        files={"file": (name, content if content is not None else make_docx(), "application/octet-stream")},
    )


def test_health(client):
    assert client.get("/health").json()["status"] == "healthy"


def test_register_login_and_duplicate(client, register):
    register(client, "a@example.com", "candidate")
    dup = client.post("/register", json={"email": "a@example.com", "password": "secret123", "role": "candidate"})
    assert dup.status_code == 400
    ok = client.post("/login", json={"email": "a@example.com", "password": "secret123"})
    assert ok.status_code == 200 and ok.json()["role"] == "candidate"
    bad = client.post("/login", json={"email": "a@example.com", "password": "wrong"})
    assert bad.status_code == 401


def test_role_protection(client, candidate_headers):
    assert client.post("/create-job", json=JOB, headers=candidate_headers).status_code == 403
    assert client.get("/candidates", headers=candidate_headers).status_code == 403
    assert client.get("/jobs").status_code == 401


def test_my_profile_route_not_shadowed(client, candidate_headers):
    r = client.get("/candidate/me/profile", headers=candidate_headers)
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "cand@example.com"


def test_upload_validation(client, candidate_headers):
    assert upload(client, candidate_headers, name="resume.txt").status_code == 400
    assert upload(client, candidate_headers, content=b"").status_code == 400


def test_full_flow(client, recruiter_headers, candidate_headers, register):
    r = upload(client, candidate_headers)
    assert r.status_code == 201, r.text
    resume_id = r.json()["id"]

    profile = client.get("/candidate/me/profile", headers=candidate_headers).json()
    assert "python" in profile["skills"].lower()
    assert profile["resume_count"] == 1
    cand_id = profile["id"]

    # A candidate without a resume should not appear in rankings
    register(client, "empty@example.com", "candidate", name="No Resume")

    job = client.post("/create-job", json=JOB, headers=recruiter_headers)
    assert job.status_code == 201
    job_id = job.json()["id"]
    assert client.get(f"/jobs/{job_id}", headers=recruiter_headers).json()["title"] == JOB["title"]

    rank = client.post("/rank", json={"job_id": job_id}, headers=recruiter_headers)
    assert rank.status_code == 200, rank.text
    body = rank.json()
    assert body["total"] == 1
    top = body["results"][0]
    assert top["candidate_id"] == cand_id and top["rank"] == 1
    assert "kubernetes" in top["missing_skills"]
    assert 0 < top["match_score"] <= 100 and 0 < top["ats_score"] <= 100

    # Filters
    none = client.post("/rank", json={"job_id": job_id, "min_ats_score": 101}, headers=recruiter_headers)
    assert none.json()["total"] == 0

    csv = client.post("/rank/export", json={"job_id": job_id}, headers=recruiter_headers)
    assert csv.status_code == 200 and "Jane Doe" in csv.text
    assert "ranked_candidates_Backend_Engineer.csv" in csv.headers["content-disposition"]

    detail = client.get(f"/candidate/{cand_id}", headers=recruiter_headers).json()
    assert detail["scores"][0]["job_title"] == JOB["title"]

    analytics = client.get("/analytics", headers=recruiter_headers).json()
    assert analytics["total_jobs"] == 1 and analytics["total_candidates"] == 2
    assert analytics["top_candidates"][0]["name"] == "Jane Doe"

    assert client.get(f"/resume/{resume_id}/preview", headers=recruiter_headers).status_code == 200

    # Another candidate cannot see this profile or resume
    other = register(client, "other@example.com", "candidate")
    assert client.get(f"/candidate/{cand_id}", headers=other).status_code == 403
    assert client.get(f"/resume/{resume_id}/preview", headers=other).status_code == 403

    # Delete candidate removes their account as well
    assert client.delete(f"/candidate/{cand_id}", headers=recruiter_headers).status_code == 200
    assert client.post("/login", json={"email": "cand@example.com", "password": "secret123"}).status_code == 401

    assert client.delete(f"/jobs/{job_id}", headers=recruiter_headers).status_code == 200


def test_recruiter_cannot_delete_others_job(client, recruiter_headers, register):
    job_id = client.post("/create-job", json=JOB, headers=recruiter_headers).json()["id"]
    other = register(client, "rec2@example.com", "recruiter")
    assert client.delete(f"/jobs/{job_id}", headers=other).status_code == 403
