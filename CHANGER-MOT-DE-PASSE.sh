#!/usr/bin/env bash
# Change le mot de passe d'accès au site HIADSI
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

python3 <<'PY'
import getpass
import hashlib
import json
import secrets
from pathlib import Path

path = Path("config_acces.json")
if path.exists():
    cfg = json.loads(path.read_text(encoding="utf-8"))
else:
    cfg = {"secret": secrets.token_hex(32)}

print("")
print("  HIADSI — changer le mot de passe d'accès")
print("")
pwd1 = getpass.getpass("  Nouveau mot de passe : ")
pwd2 = getpass.getpass("  Confirmer             : ")
if not pwd1:
    raise SystemExit("  Mot de passe vide — annulé.")
if pwd1 != pwd2:
    raise SystemExit("  Les mots de passe ne correspondent pas.")

cfg["password_hash"] = hashlib.sha256(pwd1.encode("utf-8")).hexdigest()
cfg.setdefault("secret", secrets.token_hex(32))
cfg["hint"] = "Mot de passe défini localement — ne pas publier ce fichier."
path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
print("")
print("  ✅ Mot de passe mis à jour.")
print("  Relancez le site : ./DEMARRER-SITE.sh")
print("")
PY
