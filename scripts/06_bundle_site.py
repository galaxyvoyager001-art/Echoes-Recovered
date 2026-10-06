#!/usr/bin/env python3
"""Step 6 (optional) - copy the Sound Time Map into a self-contained folder.

The site in site/ references audio and images relative to the repository root
(`../data/...`) so nothing is duplicated in git. For hosting elsewhere, this
script copies index.html, data.js and every referenced file into OUT_DIR with
the same relative layout and sets the base path to "./".

Usage: python scripts/06_bundle_site.py OUT_DIR [--fragment]
  --fragment  drop the <!doctype>/<html> lines (for hosts that add their own skeleton)
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = Path(sys.argv[1]).resolve()
    frag = "--fragment" in sys.argv
    out.mkdir(parents=True, exist_ok=True)
    html = (ROOT / "site" / "index.html").read_text()
    if frag:
        html = re.sub(r"^<!doctype html>\s*<html lang=\"en\">\s*", "", html)
    html = html.replace('<script>window.STM_BASE = window.STM_BASE || "../";</script>', '<script>window.STM_BASE = "./";</script>')
    (out / "index.html").write_text(html)
    js = (ROOT / "site" / "data.js").read_text()
    (out / "data.js").write_text(js)
    data = json.loads(js[js.index("=") + 1 : js.rstrip().rindex(";")])
    files = []
    for s in data["songs"]:
        files += list(s["audio"].values()) + list(s["img"].values()) + [s["log"]]
    for rel in files:
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
    print(f"bundled {len(files)} files into {out}")


if __name__ == "__main__":
    main()
