# LogLens — AI test-failure root-cause analyzer

CI runs fail by the hundreds, but usually for a handful of reasons. LogLens reads raw test logs
(pytest, unittest, JUnit, or anything with error lines), **collapses failures that share a root cause**,
flags the ones you've **already triaged**, and (optionally) asks a **local LLM** for a likely cause —
no data leaves the machine.

```
8 failures → 4 distinct root causes (1 already known).
| # | Failures | Headline                                   | Known issue |
| 1 | 3        | requests...ConnectionError: ...            | INFRA-482   |
| 2 | 2        | AssertionError: assert 0.0731 < 0.05       | —           |
```

## How it works
1. **Parse** — splits logs into per-test failure blocks (pytest `____ name ____`, `FAIL:`, `[FAIL]`, JUnit summaries; falls back to error lines).
2. **Normalize** — masks volatile tokens (timestamps, IPs, UUIDs, hex, paths, numbers) so the same bug yields the same signature.
3. **Cluster** — TF-IDF char n-grams + cosine similarity, greedy deterministic clustering, ranked by impact.
4. **Match** — compares clusters to a JSON knowledge base of known issues (ticket + notes).
5. **Triage (optional)** — sends the top clusters to Ollama (`llama3.1:8b` by default) for a 3-bullet diagnosis.

## Run
```bash
pip install -r requirements.txt
python -m loglens analyze sample_logs --known sample_logs/known_issues.json --md report.md
python -m loglens analyze build/logs --llm                 # with local AI triage (ollama serve)
python -m loglens analyze build/logs --known kb.json --fail-on-new   # CI gate: fail only on NEW causes
python -m loglens learn --known kb.json --ticket BUG-12 --signature "KeyError: 'PatientID'"
uvicorn loglens.api:app --reload                           # REST API → http://localhost:8000/docs
pytest -q
```

## API
- `GET /health` – status + whether Ollama is reachable
- `POST /analyze` – `{"logs": {"run1.log": "..."}, "threshold": 0.6, "use_llm": false}`
- `POST /analyze/files?fmt=markdown` – multipart upload of log files (20 MB cap)

Config: `OLLAMA_URL`, `OLLAMA_MODEL`, `LOGLENS_KNOWN_ISSUES`.

## Ideas to extend
JUnit XML parsing, flaky-test detection across runs, Jira ticket auto-creation, Slack summary bot,
GitHub Action that comments the report on PRs.
