#!/usr/bin/env bash
# Show user feedback
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
FILE="$HERE/suggestions.jsonl"

if [[ ! -f "$FILE" ]] || [[ ! -s "$FILE" ]]; then
  echo "No feedback recorded yet."
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
print(f"  {len(rows)} feedback item(s)\n")
for r in reversed(rows):
    print(f"  {r.get('date', '')}  |  {r.get('nom', '')}  |  {r.get('interface', '')}")
    print(f"    {r.get('message', '')}")
    print()
PY
