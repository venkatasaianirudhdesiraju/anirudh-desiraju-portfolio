# Hub

One local server that mounts every app in `projects/` and serves a single home page.

```bash
python -m hub                 # http://localhost:8000 (opens your browser)
python -m hub --host 0.0.0.0  # reach it from your phone on the same Wi-Fi (trusted networks only — there is no login)
pytest -q
```
Routes: `/` home · `/lifeos/` · `/jobfit/` · `/ui/tradescout` · `/ui/loglens` · `/ui/dataguard` · `/apisaas/docs` · `/health`.
If one app's dependencies are missing, the others still run, and its tile is dimmed with the error on hover.
The shared design system is `hub/static/style.css`.
