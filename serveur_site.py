#!/usr/bin/env python3
"""HIADSI server: static files + feedback + download log."""

from __future__ import annotations

import json
import os
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parent
SUGGESTIONS_FILE = ROOT / "suggestions.jsonl"
DOWNLOADS_FILE = ROOT / "telechargements.jsonl"
MAX_LEN = 4000
INTERFACES = {
    "Interface-QE_v1",
    "generation_inputs-QE",
    "generation_pseudos",
    "supra-QE",
    "thermo_pw",
    "plusieurs",
    "autre",
}
DOWNLOAD_INTERFACES = {
    "Interface-QE_v1",
    "generation_inputs-QE",
    "generation_pseudos",
    "supra-QE",
    "thermo_pw",
}


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print(f"  {self.address_string()} — {fmt % args}")

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_jsonl(self, path: Path) -> list:
        items = []
        if not path.exists():
            return items
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return items

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/suggestions":
            items = self._read_jsonl(SUGGESTIONS_FILE)
            items.reverse()
            return self._json(200, {"ok": True, "suggestions": items[:80]})
        if path == "/api/telechargements":
            items = self._read_jsonl(DOWNLOADS_FILE)
            counts: dict[str, int] = {k: 0 for k in DOWNLOAD_INTERFACES}
            for row in items:
                key = str(row.get("interface") or "")
                if key in counts:
                    counts[key] += 1
            recent = list(reversed(items))[:100]
            # Do not expose emails in the default local public read API
            for row in recent:
                if "email" in row and row["email"]:
                    row = row  # kept for local author use via LIRE-TELECHARGEMENTS.sh
            return self._json(
                200,
                {
                    "ok": True,
                    "total": len(items),
                    "counts": counts,
                    "telechargements": recent,
                },
            )
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/suggestions":
            return self._post_suggestion()
        if path == "/api/telechargements":
            return self._post_download()
        self.send_error(404, "Not Found")

    def _parse_body(self) -> dict | None:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > 200_000:
            self._json(400, {"ok": False, "error": "Invalid request."})
            return None
        raw = self.rfile.read(length)
        ctype = (self.headers.get("Content-Type") or "").lower()
        try:
            if "application/json" in ctype:
                return json.loads(raw.decode("utf-8"))
            parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
            return {k: (v[0] if v else "") for k, v in parsed.items()}
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"ok": False, "error": "Unreadable data."})
            return None

    def _post_suggestion(self) -> None:
        data = self._parse_body()
        if data is None:
            return

        nom = str(data.get("nom") or "").strip()[:80]
        email = str(data.get("email") or "").strip()[:120]
        interface = str(data.get("interface") or "").strip()
        message = str(data.get("message") or "").strip()

        if interface not in INTERFACES:
            return self._json(400, {"ok": False, "error": "Please choose an interface."})
        if len(message) < 10:
            return self._json(
                400,
                {"ok": False, "error": "Please write a more detailed message (at least 10 characters)."},
            )
        if len(message) > MAX_LEN:
            return self._json(400, {"ok": False, "error": "Message is too long."})

        entry = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "nom": nom or "Anonymous",
            "email": email,
            "interface": interface,
            "message": message,
        }
        with SUGGESTIONS_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return self._json(201, {"ok": True, "message": "Thank you — your feedback has been saved."})

    def _post_download(self) -> None:
        data = self._parse_body()
        if data is None:
            return

        nom = str(data.get("nom") or "").strip()[:80]
        email = str(data.get("email") or "").strip()[:120]
        organisme = str(data.get("organisme") or "").strip()[:160]
        interface = str(data.get("interface") or "").strip()

        if interface not in DOWNLOAD_INTERFACES:
            return self._json(400, {"ok": False, "error": "Unknown interface."})
        if len(nom) < 2:
            return self._json(400, {"ok": False, "error": "Please enter your name."})
        if len(organisme) < 2:
            return self._json(400, {"ok": False, "error": "Please enter your institution or laboratory."})

        entry = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "nom": nom,
            "email": email,
            "organisme": organisme,
            "interface": interface,
        }
        with DOWNLOADS_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        items = self._read_jsonl(DOWNLOADS_FILE)
        count = sum(1 for row in items if row.get("interface") == interface)
        return self._json(
            201,
            {
                "ok": True,
                "message": "Download recorded.",
                "count": count,
            },
        )


def main() -> None:
    port = int(os.environ.get("SITE_PORT", "8090"))
    host = os.environ.get("SITE_HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), SiteHandler)
    print("")
    print("  HIADSI — site + feedback + downloads")
    print(f"  URL    : http://{host}:{port}/")
    print(f"  Logs   : {SUGGESTIONS_FILE.name} · {DOWNLOADS_FILE.name}")
    print("  Stop   : Ctrl+C")
    print("")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
