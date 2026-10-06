#!/usr/bin/env python3
"""Step 3 - make bit-exact lossless (FLAC) copies of the LoC WAV masters.

The LoC WAV files (~20-25 MB each) are kept byte-for-byte in data/originals/
(git-ignored because of size; re-downloadable with checksums by step 1).
For the repository and the archive package we store FLAC copies and *prove*
they are lossless: the MD5 of the decoded PCM stream must equal the MD5 of the
WAV's PCM stream (ffmpeg -f md5). The result is written into the metadata.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pcm_md5(path: Path) -> str:
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-map", "0:a", "-c:a", "pcm_s16le", "-f", "md5", "-"],
                         check=True, capture_output=True, text=True).stdout.strip()
    return out.split("=", 1)[1]


def main():
    for mp in sorted((ROOT / "data" / "metadata").glob("*.json")):
        meta = json.loads(mp.read_text())
        if not meta["rights"]["cleared_for_reuse"]:
            continue
        d = ROOT / "data" / "originals" / meta["slug"]
        wav, flac = d / "loc_original.wav", d / "loc_original.flac"
        if not flac.exists():
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "flac", "-compression_level", "8", str(flac)], check=True)
        a, b = pcm_md5(wav), pcm_md5(flac)
        meta["lossless_copy"] = {"file": str(flac.relative_to(ROOT)), "bytes": flac.stat().st_size,
                                 "pcm_md5_wav": a, "pcm_md5_flac": b, "bit_exact": a == b}
        mp.write_text(json.dumps(meta, indent=1, ensure_ascii=False))
        print(("OK  " if a == b else "BAD ") + meta["slug"], flac.stat().st_size // 1024, "KiB")


if __name__ == "__main__":
    main()
