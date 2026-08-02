#!/usr/bin/env python3
"""Serveur HIADSI : fichiers statiques + collecte des suggestions."""

from __future__ import annotations

import json
import os
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parent
SUGGESTIONS_FILE = ROOT / "suggestions.jsonl"
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

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/suggestions":
            items = []
            if SUGGESTIONS_FILE.exists():
                for line in SUGGESTIONS_FILE.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            items.reverse()
            return self._json(200, {"ok": True, "suggestions": items[:80]})
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/api/suggestions":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > 200_000:
            return self._json(400, {"ok": False, "error": "Requête invalide."})

        raw = self.rfile.read(length)
        ctype = (self.headers.get("Content-Type") or "").lower()
        data: dict = {}
        try:
            if "application/json" in ctype:
                data = json.loads(raw.decode("utf-8"))
            else:
                parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
                data = {k: (v[0] if v else "") for k, v in parsed.items()}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._json(400, {"ok": False, "error": "Données illisibles."})

        nom = str(data.get("nom") or "").strip()[:80]
        email = str(data.get("email") or "").strip()[:120]
        interface = str(data.get("interface") or "").strip()
        message = str(data.get("message") or "").strip()

        if interface not in INTERFACES:
            return self._json(400, {"ok": False, "error": "Choisissez une interface."})
        if len(message) < 10:
            return self._json(400, {"ok": False, "error": "Écrivez une suggestion plus détaillée (10 caractères min.)."})
        if len(message) > MAX_LEN:
            return self._json(400, {"ok": False, "error": "Suggestion trop longue."})

        entry = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "nom": nom or "Anonyme",
            "email": email,
            "interface": interface,
            "message": message,
        }
        with SUGGESTIONS_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return self._json(201, {"ok": True, "message": "Merci — votre suggestion a été enregistrée."})


def main() -> None:
    port = int(os.environ.get("SITE_PORT", "8090"))
    host = os.environ.get("SITE_HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), SiteHandler)
    print("")
    print("  HIADSI — site + suggestions")
    print(f"  URL    : http://{host}:{port}/")
    print(f"  Fichier: {SUGGESTIONS_FILE.name}")
    print("  Arrêt  : Ctrl+C")
    print("")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Arrêt du serveur.")
        server.server_close()


if __name__ == "__main__":
    main()
