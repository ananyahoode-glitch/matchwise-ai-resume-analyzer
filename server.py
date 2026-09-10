"""Run Matchwise locally: python server.py"""
from __future__ import annotations

import json
import mimetypes
import base64
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.analyzer import analyze
from src.document_parser import DocumentParseError, extract_text

ROOT = Path(__file__).parent
STATIC = ROOT / "static"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        super().end_headers()

    def _json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != "/api/analyze":
            return self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found."})
        size = int(self.headers.get("Content-Length", "0"))
        if not 0 < size <= MAX_UPLOAD_BYTES:
            return self._json(HTTPStatus.BAD_REQUEST, {"error": "Request must be smaller than 5 MB."})
        try:
            data = json.loads(self.rfile.read(size).decode("utf-8"))
            resume, job = (data.get("resume") or "").strip(), (data.get("job") or "").strip()
            if data.get("file"):
                uploaded = data["file"]
                resume = extract_text(uploaded.get("name", "resume"), base64.b64decode(uploaded["content"]))
            if len(resume) < 40 or len(job) < 40:
                raise ValueError("Add at least a few sentences for both the resume and job description.")
            return self._json(HTTPStatus.OK, analyze(resume, job))
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception:
            return self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Analysis could not be completed. Please try again."})

    def do_GET(self):
        if urlparse(self.path).path == "/api/health":
            return self._json(HTTPStatus.OK, {"status": "ok"})
        return super().do_GET()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    print("Matchwise is running at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), AppHandler).serve_forever()
