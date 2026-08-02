#!/usr/bin/env python3
"""Serveur HIADSI protégé par mot de passe (session cookie)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config_acces.json"
COOKIE_NAME = "hiadsi_session"
SESSION_DAYS = 7

# Accessible sans mot de passe (page de connexion uniquement)
PUBLIC_EXACT = {
    "/login.html",
    "/css/style.css",
    "/css/login.css",
    "/favicon.ico",
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def default_config() -> dict:
    # Mot de passe initial — à changer avec ./CHANGER-MOT-DE-PASSE.sh
    password = "hiadsi-acces"
    return {
        "password_hash": hash_password(password),
        "secret": secrets.token_hex(32),
        "hint": "Changez ce mot de passe avec ./CHANGER-MOT-DE-PASSE.sh",
    }


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        cfg = default_config()
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        print("  [info] config_acces.json créé")
        print("  Mot de passe initial : hiadsi-acces")
        print("  Changez-le : ./CHANGER-MOT-DE-PASSE.sh")
        return cfg
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def sign_token(secret: str, expires: int) -> str:
    payload = str(expires)
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def valid_token(secret: str, token: str | None) -> bool:
    if not token or "." not in token:
        return False
    payload, sig = token.rsplit(".", 1)
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return False
    try:
        return int(payload) >= int(time.time())
    except ValueError:
        return False


class ProtectedHandler(SimpleHTTPRequestHandler):
    config: dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print(f"  {self.address_string()} — {fmt % args}")

    def _cookies(self) -> dict[str, str]:
        raw = self.headers.get("Cookie", "")
        out: dict[str, str] = {}
        for part in raw.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                out[k] = v
        return out

    def _authorized(self) -> bool:
        token = self._cookies().get(COOKIE_NAME)
        return valid_token(self.config["secret"], token)

    def _send_redirect(self, location: str, cookie: str | None = None, clear: bool = False) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        if cookie:
            self.send_header(
                "Set-Cookie",
                f"{COOKIE_NAME}={cookie}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_DAYS * 86400}",
            )
        if clear:
            self.send_header(
                "Set-Cookie",
                f"{COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0",
            )
        self.end_headers()

    def _is_public(self, path: str) -> bool:
        return path in PUBLIC_EXACT

    def _guard(self) -> bool:
        """Retourne True si la requête peut continuer, sinon envoie la redirection."""
        path = self.path.split("?", 1)[0]

        if path == "/logout":
            self._send_redirect("/login.html", clear=True)
            return False

        if path == "/login":
            self._send_redirect("/login.html")
            return False

        if not self._is_public(path) and not self._authorized():
            self._send_redirect("/login.html")
            return False

        if path == "/":
            self.path = "/index.html"
        return True

    def do_GET(self) -> None:
        if not self._guard():
            return
        return super().do_GET()

    def do_HEAD(self) -> None:
        if not self._guard():
            return
        return super().do_HEAD()

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/login":
            self.send_error(405, "Method Not Allowed")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        data = parse_qs(body)
        password = (data.get("password") or [""])[0]

        if hmac.compare_digest(hash_password(password), self.config["password_hash"]):
            expires = int(time.time()) + SESSION_DAYS * 86400
            token = sign_token(self.config["secret"], expires)
            self._send_redirect("/", cookie=token)
            return

        self._send_redirect("/login.html?erreur=1")


def main() -> None:
    port = int(os.environ.get("SITE_PORT", "8090"))
    host = os.environ.get("SITE_HOST", "127.0.0.1")
    cfg = load_config()
    ProtectedHandler.config = cfg

    server = ThreadingHTTPServer((host, port), ProtectedHandler)
    print("")
    print("  HIADSI — site protégé par mot de passe")
    print(f"  URL    : http://{host}:{port}/")
    print("  Arrêt  : Ctrl+C")
    print("")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Arrêt du serveur.")
        server.server_close()


if __name__ == "__main__":
    main()
