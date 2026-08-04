#!/usr/bin/env bash
# Show the download log (local server)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
FILE="$HERE/telechargements.jsonl"

if [[ ! -f "$FILE" ]] || [[ ! -s "$FILE" ]]; then
  echo "No downloads recorded yet."
  exit 0
fi

python3 - "$FILE" <<'PY'
import json
import sys
from pathlib import Path

rows = []
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError:
        pass
print(f"  {len(rows)} download(s)\n")
for r in reversed(rows):
    print(
        f"  {r.get('date', '')}  |  {r.get('nom', '')}  |  "
        f"{r.get('organisme', '')}  |  {r.get('interface', '')}  |  {r.get('email', '')}"
    )
PY
