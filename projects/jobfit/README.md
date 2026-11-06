# JobFit — resume ↔ job-description matcher

Paste a resume and a job posting; get a **fit score**, the **required skills you're missing**, the
**ATS keywords** the posting uses that your resume doesn't, and concrete fixes. Optionally drafts
**tailored bullets with a local LLM** (Ollama) that is instructed never to invent experience.
Give it many job files and it **ranks them** — apply to the best fits first.

```
=== jd_backend.txt: 61% fit (skills 66%, similarity 0.125) ===
Matched:           AWS, CI/CD, Docker, FastAPI, Flask, Kubernetes, PostgreSQL, Python, REST APIs
Missing required:  Unit Testing, Microservices, Pytest, Kafka
Missing preferred: Observability, Redis, Terraform
  • Add evidence for required skills: Kafka, Pytest …
  • Quantify impact — add numbers (%, $, time saved, scale) to your top bullets.
```

## Scoring
`score = 60% weighted skill coverage + 25% TF-IDF similarity + 15% years-of-experience check`
- ~90-skill taxonomy with aliases (`k8s`→Kubernetes, `sklearn`→scikit-learn, `pl/sql`→Oracle …) in `jobfit/skills.py`
- Splits the JD into *required* vs *preferred* sections; required skills weigh 2×, repeated mentions add weight
- Extracts "5+ years" style requirements and compares them to the resume

## Run
```bash
pip install -r requirements.txt
python -m jobfit my_resume.pdf jobs/*.txt            # rank many postings
python -m jobfit my_resume.docx job.txt --tailor     # + local AI rewrite (ollama serve)
uvicorn jobfit.api:app                               # web UI at http://localhost:8000
pytest -q
```

## Making money with it
This is a working core for a paid "resume optimizer" micro-SaaS (a crowded market, but people pay
$10–30/mo for this). Put it behind the `apisaas` starter in this repo for API keys, plans and usage
metering, or sell tailored-resume reviews as a service.
