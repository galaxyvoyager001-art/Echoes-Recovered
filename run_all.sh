#!/usr/bin/env bash
# Reproduce the whole project from scratch.
#   1. fetch LoC records + rights check + downloads   2. restore
#   3. lossless copies of originals                     4. Sound Time Map data
#   5. archive package                                  6. phonograph design files
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/01_fetch_loc.py
python3 scripts/02_restore.py --workers "${WORKERS:-3}"
python3 scripts/03_preserve_originals.py
python3 scripts/04_build_site.py
python3 scripts/05_build_archive_package.py
python3 scripts/07_results_table.py
python3 phonograph/design.py
echo "Done. Serve with: python3 scripts/serve.py . 8000  ->  http://localhost:8000/site/"
