#!/usr/bin/env python3
"""Step 6 (optional) - copy the Sound Time Map into a self-contained folder.

The site in site/ references audio and images relative to the repository root
(`../data/...`) so nothing is duplicated in git. For hosting elsewhere, this
script copies index.html, data.js and every referenced file into OUT_DIR with
the same relative layout and sets the base path to "./".

Usage: python scripts/06_bundle_site.py OUT_DIR [--fragment] [--web-kbps N] [--diag-kbps M]
  --fragment    drop the <!doctype>/<html> lines (for hosts that add their own skeleton)
  --web-kbps N  for size-limited hosts: re-encode every MP3 (original, restored, A/B,
                removed) to N kbps mono CBR with identical settings, so the A/B
                comparison stays fair; the page then says it plays web copies.
  --diag-kbps M bitrate for the diagnostic 'removed component' files (default: N)
                (LAME cannot go below 32 kbps at 44.1 kHz, so lower values are clamped)
  --remote URL  for hosts with a file-count limit: link the A/B file, log and spectrogram
                to URL/<path> (e.g. the GitHub tree of a commit) instead of copying them
"""
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = Path(sys.argv[1]).resolve()
    frag = "--fragment" in sys.argv
    kbps = int(sys.argv[sys.argv.index("--web-kbps") + 1]) if "--web-kbps" in sys.argv else None
    diag = int(sys.argv[sys.argv.index("--diag-kbps") + 1]) if "--diag-kbps" in sys.argv else kbps
    remote = sys.argv[sys.argv.index("--remote") + 1].rstrip("/") if "--remote" in sys.argv else None
    out.mkdir(parents=True, exist_ok=True)
    html = (ROOT / "site" / "index.html").read_text()
    if frag:
        html = re.sub(r"^<!doctype html>\s*<html lang=\"en\">\s*", "", html)
    web = f'window.STM_WEBCOPY = "{kbps} kbps mono";' if kbps else ""
    html = html.replace('<script>window.STM_BASE = window.STM_BASE || "../";</script>', f'<script>window.STM_BASE = "./"; {web}</script>')
    (out / "index.html").write_text(html)
    js = (ROOT / "site" / "data.js").read_text()
    head, data = js[: js.index("=") + 1], json.loads(js[js.index("=") + 1 : js.rstrip().rindex(";")])
    files = []
    for s in data["songs"]:
        if remote:
            s["audio"]["ab"], s["img"]["spectrogram"], s["log"] = (
                f"{remote}/{p}" for p in (s["audio"]["ab"], s["img"]["spectrogram"], s["log"]))
        files += [p for p in list(s["audio"].values()) + list(s["img"].values()) + [s["log"]] if not p.startswith("http")]
    (out / "data.js").write_text(js if not remote else head + " " + json.dumps(data, ensure_ascii=False) + ";\n")
    def put(rel):
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if kbps and rel.endswith(".mp3"):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ROOT / rel), "-ac", "1",
                            "-codec:a", "libmp3lame", "-b:a", f"{diag if rel.endswith('removed_component.mp3') else kbps}k", str(dst)], check=True)
        else:
            shutil.copy2(ROOT / rel, dst)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(put, files))
    print(f"bundled {len(files)} files into {out}")


if __name__ == "__main__":
    main()
