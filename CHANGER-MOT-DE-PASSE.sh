#!/usr/bin/env bash
# Change the HIADSI site access password
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

python3 - <<'PY'
import getpass
import hashlib
import json
from pathlib import Path

cfg_path = Path("config_acces.json")
print("  HIADSI — change access password")
pwd = getpass.getpass("  New password: ")
if not pwd.strip():
    raise SystemExit("  Empty password — cancelled.")
digest = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
cfg = {}
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
cfg["password_sha256"] = digest
cfg["hint"] = "Password set locally — do not publish this file."
cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("  Password updated.")
PY
