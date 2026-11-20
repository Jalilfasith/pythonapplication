import os
import sqlite3
from contextlib import closing
from html import escape
from pathlib import Path
from urllib.parse import parse_qs

DB_PATH = os.environ.get("DB_PATH", "/data/notes.sqlite3")
PAGE = Path(__file__).with_name("index.html").read_text()


def reply(start, status, body, content_type="text/plain; charset=utf-8", extra=()):
    data = body.encode()
    start(status, [("Content-Type", content_type), ("Content-Length", str(len(data))),
                   ("Cache-Control", "no-store"), *extra])
    return [data]


def application(env, start):
    path = env["PATH_INFO"]
    method = env["REQUEST_METHOD"]
    if path not in ("/", "/health", "/notes"):
        return reply(start, "404 Not Found", "Page not found")
    allowed = "POST" if path == "/notes" else "GET"
    if method != allowed:
        return reply(start, "405 Method Not Allowed", "Unsupported method", extra=[("Allow", allowed)])
    try:
        with closing(sqlite3.connect(DB_PATH, timeout=5)) as db:
            db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL)")
            if path == "/health":
                db.execute("SELECT id FROM notes LIMIT 1").fetchone()
                return reply(start, "200 OK", "healthy\n")
            if path == "/notes":
                try:
                    size = int(env.get("CONTENT_LENGTH") or 0)
                except ValueError:
                    return reply(start, "400 Bad Request", "Invalid request size")
                if not 0 < size <= 4096:
                    return reply(start, "413 Content Too Large", "Enter a shorter note")
                fields = parse_qs(env["wsgi.input"].read(size).decode("utf-8", errors="replace"))
                note = fields.get("note", [""])[0].strip()
                if not 1 <= len(note) <= 200:
                    return reply(start, "400 Bad Request", "Enter 1 to 200 characters")
                db.execute("INSERT INTO notes(body) VALUES (?)", (note,))
                db.commit()
                return reply(start, "303 See Other", "", extra=[("Location", "/")])
            rows = db.execute("SELECT body FROM notes ORDER BY id DESC LIMIT 50")
            items = "".join(f"<li>{escape(body)}</li>" for body, in rows)
            return reply(start, "200 OK", PAGE.replace("<!-- notes -->", items or "<li>No notes yet.</li>"),
                         "text/html; charset=utf-8")
    except sqlite3.Error as error:
        print(f"Database error: {error}", file=env["wsgi.errors"])
        return reply(start, "503 Service Unavailable", "Database temporarily unavailable")
