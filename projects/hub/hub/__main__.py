import argparse
import threading
import webbrowser

import uvicorn

ap = argparse.ArgumentParser(prog="hub")
ap.add_argument("--port", type=int, default=8000)
ap.add_argument("--host", default="127.0.0.1", help="use 0.0.0.0 to open from your phone on the same Wi-Fi (trusted networks only)")
ap.add_argument("--no-browser", action="store_true")
a = ap.parse_args()
if not a.no_browser:
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{a.port}")).start()
uvicorn.run("hub.app:app", host=a.host, port=a.port)
