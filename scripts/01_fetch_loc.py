#!/usr/bin/env python3
"""Step 1 - fetch Library of Congress National Jukebox items and verify rights.

For every item in config/selection.json this script:

1. Downloads the official LoC JSON record (https://www.loc.gov/item/<id>/?fo=json)
   and stores it untouched as data/originals/<slug>/loc_item.json.
2. Extracts the "Rights & Access" text (the `rights` field that the item page
   renders) plus the rights advisory, and applies an explicit, conservative
   clearance rule (see `assess_rights`). Items that fail are recorded as
   rejected and are NOT downloaded.
3. Downloads the LoC preservation WAV, the LoC MP3 derivative and the disc-label
   image without modifying them, and records SHA-256 checksums.
4. Writes data/metadata/<slug>.json (normalised metadata + rights record).

Usage:  python scripts/01_fetch_loc.py [--only jukebox-12345 ...]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from restoration.places import city_from_loc, place  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "data" / "originals"
META = ROOT / "data" / "metadata"
UA = {"User-Agent": "EchoesRecovered/1.0 (historical audio restoration research)"}

# The public-domain sentence that must appear in the item's Rights & Access text.
MMA_SENTENCE = "all recordings published prior to 1923 will enter the public domain"
MMA_1923_SENTENCE = "Recordings published between 1923 and 1946 are then protected for 100 years"
# Tier 1 - conservative margin: recordings made before 1922, so that their commercial
# release (normally weeks to months later) also precedes 1923.
RECORDING_CUTOFF = dt.date(1922, 1, 1)
# Tier 2 - recordings made from 1922 up to this date. Under the 100-year term the LoC text
# states for 1923-1946 publications (terms run to the end of the calendar year), anything
# first published by 31 Dec 1925 is public domain from 1 Jan 2026. The cutoff also keeps
# the set acoustic: Columbia and Victor moved to electrical recording in Feb-spring 1925.
TIER2_CUTOFF = dt.date(1925, 2, 1)
TODAY = dt.date.today()


def http_get(url: str, retries: int = 5) -> bytes:
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception as e:  # network hiccups / rate limiting
            last = e
            time.sleep(2 ** (i + 1))
    raise RuntimeError(f"GET failed after {retries} tries: {url}: {last}")


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def slugify(item_id: str, title: str) -> str:
    t = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40].strip("-")
    return f"{item_id}_{t}"


def find_files(record: dict) -> dict:
    """Return the WAV master, MP3 derivative and disc-label image URLs."""
    out = {}
    for res in record.get("resources", []):
        for group in res.get("files", []):
            for f in group:
                mt, url = f.get("mimetype"), f.get("url") or f.get("filename")
                if mt == "audio/wav" and "wav" not in out:
                    out["wav"] = url
                    out["wav_size"] = f.get("size")
                elif mt == "audio/mpeg" and "mp3" not in out:
                    out["mp3"] = f.get("filename") or url
                    out["duration_s"] = f.get("duration")
                    out["can_download"] = f.get("canDownload")
                    out["rights_restricted_flag"] = f.get("rights_restricted")
                elif mt == "image/jpeg" and "jukebox" in res.get("url", "") and res["url"].endswith(".1"):
                    # keep the largest label JPEG offered
                    if (f.get("width") or 0) >= out.get("_lw", 0):
                        out["label"], out["_lw"] = url, f.get("width") or 0
    out.pop("_lw", None)
    return out


def catalog_from_file_id(file_id: str) -> dict:
    """LoC file ids encode the issued disc: e.g. dlc_victor_18255_01_b19331_01."""
    m = re.match(r"^(?P<src>[a-z]+)_(?P<label>victor|col)_(?P<num>[a-z]?\d+[a-z]?)_(?P<side>\d+)_", file_id)
    if not m:
        return {}
    label = {"victor": "Victor", "col": "Columbia"}[m["label"]]
    return {"label": label, "catalog_number": m["num"].upper(), "source_copy_prefix": m["src"]}


def assess_rights(it: dict, files: dict, catalog: dict) -> tuple[bool, list[str]]:
    """Apply the project's clearance rule. Returns (cleared, reasons)."""
    reasons, ok = [], True
    rights = strip_html(" ".join(it.get("rights") or []))
    try:
        rec = dt.date.fromisoformat(it.get("recording_date") or it.get("date"))
    except Exception:
        rec = None
    tier = 1 if rec and rec < RECORDING_CUTOFF else 2 if rec and rec < TIER2_CUTOFF else None
    if tier == 1:
        if MMA_SENTENCE in rights:
            reasons.append("Rights & Access text states that recordings published prior to 1923 are in the public domain (Music Modernization Act).")
        else:
            ok = False
            reasons.append("FAIL: Rights & Access text does not contain the pre-1923 public-domain statement.")
        reasons.append(f"Recording date {rec} is before {RECORDING_CUTOFF} (project margin so that publication also precedes 1923).")
    elif tier == 2:
        if MMA_1923_SENTENCE in rights and TODAY >= dt.date(2026, 1, 1):
            reasons.append("Rights & Access text states that recordings published between 1923 and 1946 are protected for 100 years. "
                           f"Recorded {rec}; first publication by 31 Dec 1925 at the latest means the term ended 31 Dec 2025, so it is public domain as of {TODAY}.")
            reasons.append("Assumption: the disc was first issued no later than 1925 (LoC does not give issue dates; Victor and Columbia normally issued within months of recording). This is the main residual uncertainty for 1922-1925 items.")
        else:
            ok = False
            reasons.append("FAIL: Rights & Access text lacks the 1923-1946 100-year statement, or the 1925 term has not yet expired.")
    else:
        ok = False
        reasons.append(f"FAIL: recording date {rec} is not before {TIER2_CUTOFF} (outside the acoustic, public-domain window).")
    if catalog and files.get("label"):
        reasons.append(f"Evidence of publication: transfer is from an issued {catalog['label']} disc (catalog no. {catalog['catalog_number']} in the LoC file id) and LoC provides the disc label image. Unissued takes (unpublished, protected until 2067) are excluded.")
    else:
        ok = False
        reasons.append("FAIL: no evidence the recording was commercially issued (unpublished pre-1923 recordings are not covered).")
    if it.get("access_restricted") is False and files.get("wav"):
        reasons.append("access_restricted = false and LoC offers the WAV/MP3 files for download.")
    else:
        ok = False
        reasons.append("FAIL: access restricted or no downloadable WAV.")
    return ok, reasons


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def process(entry: dict) -> dict:
    item_id = entry["id"]
    api = f"https://www.loc.gov/item/{item_id}/?fo=json"
    record = json.loads(http_get(api))
    it = record["item"]
    title = it["title"]
    slug = slugify(item_id, title)
    files = find_files(record)
    file_id = (it.get("file_id") or [""])[0]
    catalog = catalog_from_file_id(file_id)
    cleared, reasons = assess_rights(it, files, catalog)
    rec_date = dt.date.fromisoformat(it.get("recording_date") or it.get("date"))

    d = ORIG / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "loc_item.json").write_text(json.dumps(record, indent=1, ensure_ascii=False))

    downloads = {}
    if cleared:
        for key, name in (("wav", "loc_original.wav"), ("mp3", "loc_original.mp3"), ("label", "loc_label.jpg")):
            url = files.get(key)
            if not url:
                continue
            p = d / name
            if not p.exists():
                p.write_bytes(http_get(url))
                time.sleep(1)
            downloads[key] = {"url": url, "file": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)}

    city = city_from_loc(it.get("location"))
    country = place(city)["country"] if city else None
    meta = {
        "id": item_id,
        "slug": slug,
        "title": title,
        "other_titles": it.get("other_title") or [],
        "performers": [next(iter(c)) if isinstance(c, dict) else c for c in (it.get("contributors") or [])],
        "primary_performer": (it.get("contributor_primary") or [""])[0],
        "contributors_with_roles": (it.get("item") or {}).get("contributors") or [],
        "recording_date": it.get("recording_date") or it.get("date"),
        "year": int((it.get("recording_date") or it.get("date"))[:4]),
        "recording_location_loc": it.get("location") or [],
        "recording_city": city,
        "recording_country": country,
        "genre_loc": it.get("genre") or [],
        "category": entry.get("category"),
        "summary": it.get("summary"),
        "description": it.get("description") or [],
        "language": it.get("language"),
        "matrix": it.get("recording_matrix_number"),
        "take": it.get("recording_take_number"),
        "file_id": file_id,
        "disc": catalog,
        "source_copy": it.get("recording_repository"),
        "duration_s": files.get("duration_s"),
        "loc_item_url": f"https://www.loc.gov/item/{item_id}/",
        "loc_api_url": api,
        "loc_files": {k: v for k, v in files.items() if k in ("wav", "mp3", "label")},
        "curator_note": entry.get("note"),
        "rights": {
            "checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "loc_rights_and_access_text": strip_html(" ".join(it.get("rights") or [])),
            "loc_rights_advisory": it.get("rights_advisory"),
            "access_restricted": it.get("access_restricted"),
            "media_player_flags": {"canDownload": files.get("can_download"), "rights_restricted": files.get("rights_restricted_flag")},
            "cleared_for_reuse": cleared,
            "status": ("NOT CLEARED - excluded" if not cleared else
                       "Public domain in the United States (published before 1923; Music Modernization Act, 17 U.S.C. 1401(a)(2)(B)(i))"
                       if rec_date < RECORDING_CUTOFF else
                       "Public domain in the United States (published 1922-1925; 100-year term ended by 31 Dec 2025; 17 U.S.C. 1401(a)(2)(B)(ii))"),
            "rights_tier": 1 if rec_date < RECORDING_CUTOFF else 2,
            "reasons": reasons,
            "caveats": [
                "LoC: 'You are responsible for deciding whether your use of the items in this collection is legal.'",
                "LoC: 'Some materials may be protected under international law.' Public-domain status here is asserted for the United States only.",
                "Required credit line: 'Library of Congress, National Jukebox.'",
            ] + ([f"Recorded in {city}, {country}, outside US jurisdiction, and issued on a US label ({catalog.get('label')} {catalog.get('catalog_number')}). "
                  "The US public-domain status above is the only status assessed here; rights in the country of recording were not separately assessed."]
                 if city and not place(city).get("us") else []),
            "credit_line": "Library of Congress, National Jukebox.",
        },
        "downloads": downloads,
    }
    META.mkdir(parents=True, exist_ok=True)
    (META / f"{slug}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    sel = json.loads((ROOT / "config" / "selection.json").read_text())["items"]
    if args.only:
        sel = [e for e in sel if e["id"] in args.only]
    summary = []
    for e in sel:
        try:
            m = process(e)
            flag = "CLEARED " if m["rights"]["cleared_for_reuse"] else "REJECTED"
            print(f"{flag} {m['id']:16s} {m['recording_date']} {m['title'][:40]:40s} {m['recording_city']}")
            summary.append({"id": m["id"], "slug": m["slug"], "cleared": m["rights"]["cleared_for_reuse"], "reasons": m["rights"]["reasons"]})
        except Exception as ex:
            print(f"ERROR    {e['id']}: {ex}", file=sys.stderr)
            summary.append({"id": e["id"], "cleared": False, "error": str(ex)})
        time.sleep(2)
    sp = ROOT / "data" / "rights_verification_summary.json"
    if args.only and sp.exists():  # partial run: update these entries, keep the rest
        done = {x["id"] for x in summary}
        order = [e["id"] for e in json.loads((ROOT / "config" / "selection.json").read_text())["items"]]
        merged = {x["id"]: x for x in json.loads(sp.read_text())}
        merged.update({x["id"]: x for x in summary})
        summary = [merged[i] for i in order if i in merged]
    sp.write_text(json.dumps(summary, indent=1))
    n = sum(s["cleared"] for s in summary)
    print(f"\n{n}/{len(summary)} items cleared and downloaded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
