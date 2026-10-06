#!/usr/bin/env python3
"""Step 4 - build the Sound Time Map data (site/data.js) and label thumbnails.

Map base: US state boundaries from the us-atlas 3.0.1 TopoJSON (US Census
Bureau cartographic boundaries), decoded and projected here so the site needs
no tile server. City points are placed at the city named in the LoC record's
`location` field; no studio street addresses are implied.
"""
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# City centres (city-level only; the LoC metadata gives city, state, country)
CITIES = {
    "New York": {"lat": 40.7128, "lon": -74.0060, "state": "New York"},
    "Camden": {"lat": 39.9259, "lon": -75.1196, "state": "New Jersey"},
    "Philadelphia": {"lat": 39.9526, "lon": -75.1652, "state": "Pennsylvania"},
    "Chicago": {"lat": 41.8781, "lon": -87.6298, "state": "Illinois"},
}
BBOX = (-75.95, 39.72, -73.45, 40.98)  # lon0, lat0, lon1, lat1
W = 1000
LATC = math.radians((BBOX[1] + BBOX[3]) / 2)
SX = W / ((BBOX[2] - BBOX[0]) * math.cos(LATC))
H = round((BBOX[3] - BBOX[1]) * SX)


def proj(lon, lat):
    return ((lon - BBOX[0]) * math.cos(LATC) * SX, (BBOX[3] - lat) * SX)


def decode_topo(path):
    topo = json.loads(path.read_text())
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts

    out = {}
    for g in topo["objects"]["states"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        d = []
        for poly in polys:
            for r in poly:
                pts = ring(r)
                if not any(BBOX[0] - 2 < lo < BBOX[2] + 2 and BBOX[1] - 2 < la < BBOX[3] + 2 for lo, la in pts):
                    continue
                d.append("M" + "L".join(f"{proj(lo, la)[0]:.1f},{proj(lo, la)[1]:.1f}" for lo, la in pts) + "Z")
        if d:
            out[g["properties"]["name"]] = "".join(d)
    return out


def main():
    songs = []
    for mp in sorted((ROOT / "data" / "metadata").glob("*.json")):
        m = json.loads(mp.read_text())
        if not m["rights"]["cleared_for_reuse"]:
            continue
        rdir = ROOT / "data" / "restored" / m["slug"]
        if not (rdir / "restored.mp3").exists():
            continue
        an = json.loads((rdir / "analysis.json").read_text())
        pr = json.loads((rdir / "params.json").read_text())
        (SITE / "img").mkdir(exist_ok=True)
        thumb = SITE / "img" / f"{m['id']}_label.jpg"
        im = Image.open(ROOT / "data" / "originals" / m["slug"] / "loc_label.jpg").convert("RGB")
        im.thumbnail((360, 360))
        im.save(thumb, quality=82)
        b, a = an["before"], an["after"]
        songs.append({
            "id": m["id"], "slug": m["slug"], "title": m["title"], "other_titles": m["other_titles"],
            "performer": m["primary_performer"], "contributors": m["contributors_with_roles"],
            "date": m["recording_date"], "year": m["year"], "city": m["recording_city"],
            "location_loc": m["recording_location_loc"], "genre_loc": m["genre_loc"], "category": m["category"],
            "summary": m["summary"], "matrix": m["matrix"], "take": m["take"], "disc": m["disc"],
            "language": m["language"], "duration_s": b["duration_s"], "note": m["curator_note"],
            "loc_url": m["loc_item_url"], "rights": m["rights"]["status"], "credit": m["rights"]["credit_line"],
            "audio": {"original": f"data/originals/{m['slug']}/loc_original.mp3",
                      "restored": f"data/restored/{m['slug']}/restored.mp3",
                      "ab": f"data/restored/{m['slug']}/ab_compare.mp3",
                      "removed": f"data/restored/{m['slug']}/removed_component.mp3"},
            "img": {"label": f"site/img/{m['id']}_label.jpg", "spectrogram": f"data/restored/{m['slug']}/spectrogram.jpg"},
            "log": f"data/restored/{m['slug']}/restoration_log.md",
            "metrics": {
                "noise_before": b["surface_noise_rms_dbfs"], "noise_after": a["surface_noise_rms_dbfs"],
                "music_floor_before": b["noise_floor_in_music_p5_dbfs"], "music_floor_after": a["noise_floor_in_music_p5_dbfs"],
                "ipm_before": b["impulses_per_min"], "ipm_after": a["impulses_per_min"],
                "band": b["usable_band_hz"],
                "replaced_pct": round(pr["stage_log"][2]["percent_samples_replaced"] + pr["stage_log"][3]["percent_samples_replaced"], 2),
            },
            "ab_cues": pr["ab_cues"],
        })
    songs.sort(key=lambda s: s["date"])
    states = decode_topo(SITE / "assets" / "us-atlas-states-10m.json")
    cities = {}
    for name, c in CITIES.items():
        n = sum(1 for s in songs if s["city"] == name)
        if n:
            x, y = proj(c["lon"], c["lat"])
            cities[name] = {**c, "x": round(x, 1), "y": round(y, 1), "count": n}
    data = {"songs": songs, "map": {"w": W, "h": H, "states": states, "cities": cities,
                                     "bbox": BBOX, "source": "us-atlas 3.0.1 (US Census Bureau cartographic boundaries)"}}
    (SITE / "data.js").write_text("window.STM = " + json.dumps(data, ensure_ascii=False) + ";\n")
    print(len(songs), "songs;", {k: v["count"] for k, v in cities.items()}, f"map {W}x{H}")


if __name__ == "__main__":
    main()
