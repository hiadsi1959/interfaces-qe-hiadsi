#!/usr/bin/env bash
# Affiche le journal des téléchargements (serveur local)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
FILE="$HERE/telechargements.jsonl"

if [[ ! -f "$FILE" ]]; then
  echo "Aucun téléchargement enregistré pour le moment."
  exit 0
fi

python3 <<PY
import json
from pathlib import Path
from collections import Counter

path = Path("$FILE")
rows = []
for line in path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line:
        rows.append(json.loads(line))

print(f"  {len(rows)} téléchargement(s)\n")
counts = Counter(r.get("interface", "?") for r in rows)
print("  Par interface :")
for name, n in counts.most_common():
    print(f"    - {name}: {n}")
print()

for i, r in enumerate(rows, 1):
    print("=" * 60)
    print(f"#{i}  {r.get('date','')}  —  {r.get('interface','')}")
    print(f"Nom : {r.get('nom','')}")
    if r.get("organisme"):
        print(f"Org : {r.get('organisme')}")
    if r.get("email"):
        print(f"Mel : {r.get('email')}")
    print()
PY
