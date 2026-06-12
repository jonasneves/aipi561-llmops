"""Minimal web UI for the TechCorp agent — a real server, no framework.

GET  /          → the chat page (web/index.html)
POST /api/ask   → runs agent.query(query, role) live and returns the full
                  trace (answer, tool calls, tokens, cost) as JSON.

Run: `python app_web.py` then open http://localhost:8479. Auth is Vertex AI
(ADC) by default — see config.py. This is the interface the screenshots in
report/ capture, and the basis for the eventual GKE deployment.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.agent import Agent  # noqa: E402

agent = Agent()
PAGE = (ROOT / "web" / "index.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body, ctype: str = "application/json") -> None:
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self) -> None:
        if self.path != "/api/ask":
            self._send(404, "{}")
            return
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or "{}")
        query = (data.get("query") or "").strip()
        role = data.get("role") or "engineer"
        if not query:
            self._send(400, json.dumps({"error": "empty query"}))
            return
        try:
            self._send(200, json.dumps(agent.query(query, user_role=role)))
        except Exception as e:  # surface failures to the UI
            self._send(500, json.dumps({"error": str(e)}))

    def log_message(self, *args) -> None:  # quiet
        pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8479"))
    print(f"serving TechCorp agent UI on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
