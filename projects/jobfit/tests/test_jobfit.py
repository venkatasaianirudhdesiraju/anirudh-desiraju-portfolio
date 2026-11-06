from pathlib import Path

from fastapi.testclient import TestClient

from jobfit.cli import main
from jobfit.scoring import score
from jobfit.skills import find_skills

EX = Path(__file__).parent.parent / "examples"
RESUME = (EX / "resume.md").read_text()


def test_skill_extraction_aliases():
    s = find_skills("Built REST APIs in FastAPI on AWS Lambda with k8s and sklearn; C++ and C# too.")
    assert {"REST APIs", "FastAPI", "AWS", "Kubernetes", "scikit-learn", "C++", "C#"} <= s.keys()
    assert "Java" not in find_skills("JavaScript only")


def test_backend_is_better_fit_than_ml():
    be = score(RESUME, (EX / "jd_backend.txt").read_text())
    ml = score(RESUME, (EX / "jd_ml.txt").read_text())
    assert be.score > ml.score + 15
    assert "Kafka" in be.missing_required and "Terraform" in be.missing_preferred
    assert "FastAPI" in be.matched and be.required_years == 5 and be.resume_years == 6
    assert "PyTorch" in ml.missing_required and ml.required_years == 7


def test_suggestions_present():
    r = score(RESUME, (EX / "jd_backend.txt").read_text())
    assert any("Kafka" in s for s in r.suggestions)
    assert any("Quantify" in s for s in r.suggestions)


def test_cli_ranks_jobs(capsys):
    assert main([str(EX / "resume.md"), str(EX / "jd_ml.txt"), str(EX / "jd_backend.txt")]) == 0
    out = capsys.readouterr().out
    assert out.index("jd_backend") < out.index("jd_ml")


def test_api():
    from jobfit.api import app
    c = TestClient(app)
    assert "JobFit" in c.get("/").text
    r = c.post("/fit", json={"resume": RESUME, "job_description": (EX / "jd_backend.txt").read_text()})
    assert r.status_code == 200 and r.json()["score"] > 50
    assert c.post("/fit", json={"resume": "x", "job_description": "y"}).status_code == 422
