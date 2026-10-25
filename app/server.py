#!/usr/bin/env python3
"""Library API - starter server (Python standard library only, no pip install needed).

Implement every endpoint in docs/api-spec.md. Only GET /healthcheck works so far.

Run locally:
    python3 app/server.py            # listens on http://127.0.0.1:8080

Environment variables:
    PORT     listen port            (default 8080)
    DB_PATH  SQLite database file   (default ./library.db)
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", "8080"))
DB_PATH = os.environ.get("DB_PATH", "library.db")

# TODO: open a sqlite3 connection to DB_PATH and create the books table.
#       sqlite3 is part of the standard library. Use check_same_thread=False and a
#       threading.Lock(), because ThreadingHTTPServer handles requests on many threads.


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_json(self, status, payload=None, headers=None):
        """Send a JSON response. Pass payload=None for a response with no body (204)."""
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_response(status)
        if payload is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def read_json(self):
        """Return the parsed JSON request body (raises ValueError on invalid JSON)."""
        length = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(length) or b"null")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/healthcheck":
            return self.send_json(200, {"status": "ok"})
        # TODO: GET /v1/books, GET /v1/books/{id}
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        # TODO: POST /v1/login, POST /v1/books, POST /v1/books/{id}/checkout, POST /v1/books/{id}/return
        self.send_json(404, {"error": "not found"})

    def do_PUT(self):
        # TODO: PUT /v1/books/{id}
        self.send_json(404, {"error": "not found"})

    def do_DELETE(self):
        # TODO: DELETE /v1/books/{id}
        self.send_json(404, {"error": "not found"})


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Library API listening on port {PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
