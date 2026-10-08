#!/usr/bin/env python3
"""Step 4 - build the Sound Time Map data (site/data.js) and label thumbnails.

Map bases (decoded and projected here, so the site needs no tile server):
  * world: world-atlas 2.0.2 countries-50m (Natural Earth, public domain)
  * inset: us-atlas 3.0.1 states-10m (US Census Bureau), for the
    New York / Camden / Philadelphia corridor, which is too small to separate
    on the world map.
City points are placed at the city named in each LoC record's `location`
field; no studio street addresses are implied.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from restoration.places import CITIES, REGIONS, place  # noqa: E402
from restoration.text import name_case  # noqa: E402

SITE = ROOT / "site"
TINTS = 5  # hand-tinted atlas colours, assigned so neighbours differ


class Proj:
    """Equirectangular projection of a lon/lat box onto a W-pixel-wide canvas."""

    def __init__(self, bbox, w, cos_lat=None):
        self.b, self.w = bbox, w
        self.k = math.cos(math.radians(cos_lat if cos_lat is not None else (bbox[1] + bbox[3]) / 2))
        self.s = w / ((bbox[2] - bbox[0]) * self.k)
        self.h = round((bbox[3] - bbox[1]) * self.s)

    def __call__(self, lon, lat):
        return ((lon - self.b[0]) * self.k * self.s, (self.b[3] - lat) * self.s)


def decode(topo_path, obj):
    topo = json.loads(Path(topo_path).read_text())
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
    shapes = []
    for g in topo["objects"][obj]["geometries"]:
        if g.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        used = {i if i >= 0 else ~i for poly in polys for r in poly for i in r}
        shapes.append({"name": g["properties"]["name"], "polys": polys, "arcs": used})
    return arcs, shapes


def ring(arcs, idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def path_for(shape, arcs, proj, bbox, min_px=0.8):
    d = []
    for poly in shape["polys"]:
        for r in poly:
            pts = ring(arcs, r)
            if not any(bbox[0] - 3 < lo < bbox[2] + 3 and bbox[1] - 3 < la < bbox[3] + 3 for lo, la in pts):
                continue
            out, last = [], None
            for lo, la in pts:
                x, y = proj(lo, la)
                if last is None or abs(x - last[0]) + abs(y - last[1]) >= min_px:
                    out.append((x, y))
                    last = (x, y)
            if len(out) >= 3:
                d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in out) + "Z")
    return "".join(d)


def colour_shapes(shapes):
    """Greedy colouring: countries sharing a border arc get different tints."""
    order = sorted(range(len(shapes)), key=lambda i: -len(shapes[i]["arcs"]))
    tint = {}
    for i in order:
        taken = {tint[j] for j in tint if shapes[i]["arcs"] & shapes[j]["arcs"]}
        tint[i] = next(t for t in range(TINTS) if t not in taken) if len(taken) < TINTS else hash(shapes[i]["name"]) % TINTS
    return tint


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
            "performer": name_case(m["primary_performer"]), "contributors": m["contributors_with_roles"],
            "date": m["recording_date"], "year": m["year"], "city": m["recording_city"],
            "country": place(m["recording_city"])["country"], "us": bool(place(m["recording_city"]).get("us")),
            "region_only": bool(place(m["recording_city"]).get("region")), "location_loc": m["recording_location_loc"],
            "genre_loc": m["genre_loc"], "category": m["category"], "summary": m["summary"], "matrix": m["matrix"],
            "take": m["take"], "disc": m["disc"], "language": m["language"], "duration_s": b["duration_s"],
            "note": m["curator_note"], "loc_url": m["loc_item_url"], "rights": m["rights"]["status"],
            "rights_caveats": m["rights"]["caveats"], "credit": m["rights"]["credit_line"],
            "date_year_only": m["recording_date"].endswith("-12-31"),
            "audio": {"original": f"data/originals/{m['slug']}/loc_original.mp3",
                      "restored": f"data/restored/{m['slug']}/restored.mp3",
                      "ab": f"data/restored/{m['slug']}/ab_compare.mp3",
                      "removed": f"data/restored/{m['slug']}/removed_component.mp3"},
            "img": {"label": f"site/img/{m['id']}_label.jpg", "spectrogram": f"data/restored/{m['slug']}/spectrogram.jpg"},
            "log": f"data/restored/{m['slug']}/restoration_log.md",
            "metrics": {
                "noise_before": b["surface_noise_rms_dbfs"], "noise_after": a["surface_noise_rms_dbfs"],
                "ipm_before": b["impulses_per_min"], "ipm_after": a["impulses_per_min"], "band": b["usable_band_hz"],
                "replaced_pct": round(pr["stage_log"][2]["percent_samples_replaced"] + pr["stage_log"][3]["percent_samples_replaced"], 2),
            },
        })
    songs.sort(key=lambda s: s["date"])

    # world map
    wb = (-128.0, -57.0, 42.0, 64.0)
    wp = Proj(wb, 1200, cos_lat=20)
    arcs, shapes = decode(SITE / "assets" / "world-atlas-countries-50m.json", "countries")
    tint = colour_shapes(shapes)
    world = []
    for i, sh in enumerate(shapes):
        d = path_for(sh, arcs, wp, wb)
        if d:
            world.append({"n": sh["name"], "t": tint[i], "d": d})
    # insets: places too close together (NY-Philadelphia) or outside the main frame (Japan)
    sarcs, sshapes = decode(SITE / "assets" / "us-atlas-states-10m.json", "states")
    INSETS = [
        {"id": "corridor", "label": "Enlarged: New York – Philadelphia", "bbox": (-75.95, 39.72, -73.45, 40.98), "w": 360,
         "arcs": sarcs, "shapes": sshapes, "tint": colour_shapes(sshapes), "min_px": 0.4},
        {"id": "midwest", "label": "Enlarged: US Midwest", "bbox": (-96.8, 37.0, -81.6, 43.7), "w": 360,
         "arcs": sarcs, "shapes": sshapes, "tint": colour_shapes(sshapes), "min_px": 0.4},
        {"id": "japan", "label": "Inset: Japan (east of the main map)", "bbox": (128.5, 30.2, 146.5, 45.8), "w": 300,
         "arcs": arcs, "shapes": shapes, "tint": tint, "min_px": 0.4},
    ]
    insets = []
    for ins in INSETS:
        pr = Proj(ins["bbox"], ins["w"])
        ins["proj"] = pr
        paths = [{"n": sh["name"], "t": ins["tint"][i], "d": path_for(sh, ins["arcs"], pr, ins["bbox"], ins["min_px"])}
                 for i, sh in enumerate(ins["shapes"])]
        bb = ins["bbox"]
        inside_world = bb[0] >= wb[0] and bb[2] <= wb[2] and bb[1] >= wb[1] and bb[3] <= wb[3]
        box = [round(v, 1) for p_ in (wp(bb[0], bb[3]), wp(bb[2], bb[1])) for v in p_] if inside_world else None
        insets.append({"id": ins["id"], "label": ins["label"], "w": pr.w, "h": pr.h, "shapes": [x for x in paths if x["d"]], "box": box})

    cities = {}
    for name, c in {**CITIES, **REGIONS}.items():
        n = sum(1 for s in songs if s["city"] == name)
        if not n:
            continue
        e = {"country": c["country"], "lat": c["lat"], "lon": c["lon"], "count": n, "region": bool(c.get("region")), "shape": c.get("shape")}
        for k, ins in enumerate(INSETS):
            bb = ins["bbox"]
            if bb[0] <= c["lon"] <= bb[2] and bb[1] <= c["lat"] <= bb[3]:
                ix, iy = ins["proj"](c["lon"], c["lat"])
                e.update(inset=k, ix=round(ix, 1), iy=round(iy, 1))
                break
        else:
            x, y = wp(c["lon"], c["lat"])
            e.update(x=round(x, 1), y=round(y, 1))
        cities[name] = e
    data = {"songs": songs, "map": {
        "w": wp.w, "h": wp.h, "countries": world, "cities": cities, "insets": insets,
        "graticule": {"lons": [round(wp(lo, 0)[0], 1) for lo in range(-120, 41, 20)],
                      "lats": [[la, round(wp(0, la)[1], 1)] for la in range(-40, 61, 20)]},
        "source": "world-atlas 2.0.2 (Natural Earth) and us-atlas 3.0.1 (US Census Bureau)"}}
    (SITE / "data.js").write_text("window.STM = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(len(songs), "songs;", {k: v["count"] for k, v in cities.items()}, f"world {wp.w}x{wp.h}",
          f"data.js {(SITE / 'data.js').stat().st_size // 1024} KiB")


if __name__ == "__main__":
    main()
