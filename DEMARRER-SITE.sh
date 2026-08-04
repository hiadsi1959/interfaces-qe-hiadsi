#!/usr/bin/env bash
# Start the HIADSI site (downloads + feedback)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PORT="${SITE_PORT:-8090}"
export SITE_PORT="$PORT"
cd "$HERE"

echo ""
echo "  HIADSI — QE interfaces (open access)"
echo "  Open  : http://127.0.0.1:${PORT}/"
echo "  Read feedback : ./LIRE-SUGGESTIONS.sh"
echo "  Stop  : Ctrl+C"
echo ""

if command -v xdg-open >/dev/null 2>&1; then
  (sleep 1; xdg-open "http://127.0.0.1:${PORT}/") >/dev/null 2>&1 &
fi

exec python3 "$HERE/serveur_site.py"
