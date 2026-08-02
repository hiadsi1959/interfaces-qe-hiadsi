#!/usr/bin/env bash
# Affiche les suggestions envoyées par les utilisateurs
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
FILE="$HERE/suggestions.jsonl"

if [[ ! -f "$FILE" ]]; then
  echo "Aucune suggestion pour le moment."
  exit 0
fi

python3 <<PY
import json
from pathlib import Path
path = Path("$FILE")
rows = []
for line in path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line:
        rows.append(json.loads(line))
print(f"  {len(rows)} suggestion(s)\n")
for i, r in enumerate(rows, 1):
    print("=" * 60)
    print(f"#{i}  {r.get('date','')}  —  {r.get('interface','')}")
    print(f"De : {r.get('nom','Anonyme')}" + (f"  <{r['email']}>" if r.get('email') else ""))
    print("-" * 60)
    print(r.get("message", ""))
    print()
PY
