#!/usr/bin/env python3
"""Step 5 - build the public release / archival package (nothing is uploaded).

Writes archive_package/:
  catalog.csv                one row per recording: metadata, rights, provenance
  internet_archive_upload.csv  ready for `ia upload --spreadsheet=...` (internetarchive CLI)
  commons/<id>.wikitext      Wikimedia Commons description pages ({{Information}} + licence)
  manifest-sha256.txt        SHA-256 of every original and restored file in the repo
  bag-info.txt               BagIt-style provenance summary
The prose documents (README, methodology, LoC inquiry draft) live next to them.
"""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "archive_package"
REPO_URL = "https://github.com/galaxyvoyager001-art/Echoes-Recovered"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def tc(s):
    return " ".join(w[:1].upper() + w[1:] for w in s.split())


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "commons").mkdir(exist_ok=True)
    rows, ia_rows, manifest = [], [], []
    for mp in sorted((ROOT / "data" / "metadata").glob("*.json")):
        m = json.loads(mp.read_text())
        if not m["rights"]["cleared_for_reuse"]:
            continue
        slug, rid = m["slug"], m["id"]
        rdir = ROOT / "data" / "restored" / slug
        odir = ROOT / "data" / "originals" / slug
        params = json.loads((rdir / "params.json").read_text())
        an = json.loads((rdir / "analysis.json").read_text())
        disc = f"{m['disc'].get('label', '')} {m['disc'].get('catalog_number', '')}".strip()
        performer = tc(m["primary_performer"])
        rows.append({
            "loc_id": rid, "title": m["title"], "other_titles": "; ".join(m["other_titles"]),
            "primary_performer": performer, "credits": "; ".join(m["contributors_with_roles"]),
            "recording_date": m["recording_date"], "recording_location_loc": ", ".join(m["recording_location_loc"]),
            "recording_city": m["recording_city"], "genre_loc": "; ".join(m["genre_loc"]), "category_project": m["category"],
            "summary_loc": m["summary"], "disc": disc, "matrix": m["matrix"], "take": m["take"], "language": m["language"],
            "loc_item_url": m["loc_item_url"], "loc_wav_url": m["loc_files"].get("wav"), "loc_mp3_url": m["loc_files"].get("mp3"),
            "loc_source_copy": m["source_copy"], "loc_rights_advisory": m["rights"]["loc_rights_advisory"],
            "rights_status": m["rights"]["status"], "rights_checked_utc": m["rights"]["checked_utc"],
            "credit_line": m["rights"]["credit_line"], "original_wav_sha256": m["downloads"]["wav"]["sha256"],
            "original_flac_bit_exact": m.get("lossless_copy", {}).get("bit_exact"),
            "restoration_percent_samples_interpolated": round(params["stage_log"][2]["percent_samples_replaced"] + params["stage_log"][3]["percent_samples_replaced"], 2),
            "surface_noise_before_dbfs": an["before"]["surface_noise_rms_dbfs"], "surface_noise_after_dbfs": an["after"]["surface_noise_rms_dbfs"],
            "impulses_per_min_before": an["before"]["impulses_per_min"], "impulses_per_min_after": an["after"]["impulses_per_min"],
        })
        desc = (f"{m['title']} ({m['summary']}). Recorded {m['recording_date']}, {tc(', '.join(m['recording_location_loc']))}. "
                f"Disc: {disc}, matrix {m['matrix']}, take {m['take']}. "
                f"Source: Library of Congress, National Jukebox, {m['loc_item_url']} . "
                f"This item contains (1) the Library of Congress transfer, losslessly re-encoded from the LoC WAV "
                f"(PCM MD5 verified identical) and (2) a restored version made by the Echoes Recovered project with documented, "
                f"non-generative DSP (AR click interpolation, Wiener noise reduction, band-limited filtering, bounded EQ). "
                f"Full methodology, parameters and code: {REPO_URL} . Credit line: Library of Congress, National Jukebox.")
        files = [("restored.flac", rdir), ("restored.mp3", rdir), ("ab_compare.mp3", rdir), ("restoration_log.md", rdir),
                 ("spectrogram.jpg", rdir), ("waveform.png", rdir), ("params.json", rdir), ("loc_original.flac", odir), ("loc_label.jpg", odir)]
        ident = f"echoes-recovered-{rid}"
        for i, (fn, d) in enumerate(files):
            ia_rows.append({
                "identifier": ident, "file": str((d / fn).relative_to(ROOT)),
                **({"mediatype": "audio", "collection": "opensource_audio", "title": f"{m['title']} - {performer} ({m['recording_date'][:4]}) [LoC transfer + restoration]",
                    "creator": performer, "date": m["recording_date"], "description": desc, "subject[0]": "78rpm", "subject[1]": "acoustic recording",
                    "subject[2]": "National Jukebox", "subject[3]": m["category"], "language": m["language"] or "",
                    "source": m["loc_item_url"], "rights": "Public domain in the United States (sound recording published before 1923; Music Modernization Act). Restoration released under CC0 1.0.",
                    "licenseurl": "https://creativecommons.org/publicdomain/mark/1.0/"} if i == 0 else {}),
            })
        (OUT / "commons" / f"{rid}.wikitext").write_text(f"""=={{{{int:filedesc}}}}==
{{{{Information
|description={{{{en|1={m['title']} - {performer}. {m['summary']}. Recorded {m['recording_date']} in {tc(', '.join(m['recording_location_loc']))}. {disc}, matrix {m['matrix']}, take {m['take']}. Restored version (click interpolation, noise reduction, band-limited filtering, bounded EQ; no generative processing). Original transfer: Library of Congress, National Jukebox.}}}}
|date={m['recording_date']} (recording); {dt.date.today().isoformat()} (restoration)
|source=Library of Congress, National Jukebox: {m['loc_item_url']} ; restoration code and logs: {REPO_URL}
|author={performer} (performer); {disc.split()[0] if disc else 'record company'} (record company); restoration: Echoes Recovered project
|permission=Credit line requested by the Library of Congress: "Library of Congress, National Jukebox."
|other versions=Unrestored LoC transfer: {m['loc_item_url']}
}}}}

=={{{{int:license-header}}}}==
{{{{PD-US-record-expired}}}}
<!-- Check on Commons before uploading: the work must also be PD in its source country (these discs were first published in the US). -->

[[Category:National Jukebox]]
[[Category:{m['recording_date'][:4]} sound recordings]]
""")
        for p in list(odir.glob("loc_original.flac")) + list(odir.glob("loc_original.mp3")) + list(odir.glob("loc_label.jpg")) + list(odir.glob("loc_item.json")) + sorted(rdir.iterdir()):
            manifest.append(f"{sha256(p)}  {p.relative_to(ROOT)}")
    with open(OUT / "catalog.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    keys = []
    for r in ia_rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(OUT / "internet_archive_upload.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(ia_rows)
    (OUT / "manifest-sha256.txt").write_text("\n".join(manifest) + "\n")
    (OUT / "bag-info.txt").write_text(f"""Source-Organization: Echoes Recovered (independent project; not affiliated with the Library of Congress)
External-Description: {len(rows)} acoustic-era recordings from the Library of Congress National Jukebox (recorded {min(r['recording_date'] for r in rows)} to {max(r['recording_date'] for r in rows)}), LoC transfers plus restored versions, with metadata, rights records and restoration logs.
External-Identifier: {REPO_URL}
Bagging-Date: {dt.date.today().isoformat()}
Payload-Oxum-Files: {len(manifest)}
Rights: Underlying sound recordings: public domain in the United States (published before 1923). Restoration outputs, code and documentation: CC0 1.0 / MIT (see LICENSE).
Credit-Line: Library of Congress, National Jukebox.
""")
    print(f"{len(rows)} recordings, {len(ia_rows)} IA file rows, {len(manifest)} manifest entries")


if __name__ == "__main__":
    main()
