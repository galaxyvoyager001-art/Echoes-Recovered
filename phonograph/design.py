#!/usr/bin/env python3
"""Design calculator for the Echoes Recovered acoustic phonograph.

Generates (in phonograph/build/):
  horn_profile.csv      exponential horn radius vs. length
  horn_segments.csv     flat patterns (annular sectors) for 6 conical segments
  horn_template_N.svg   1:1 printable cutting template per segment (mm)
  strobe_50hz.svg / strobe_60hz.svg   1:1 speed-check strobe discs (78 rpm)
  tonearm.txt           pivot geometry and tracking-error table
  drawing.svg           dimensioned top + side view of the whole machine

All numbers in the build guide come from this script. Run:
  python phonograph/design.py
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "build"
C = 343.0  # speed of sound, m/s at 20 C

# ----------------------------- design inputs ------------------------------ #
HORN = dict(throat_d_mm=32.0, mouth_d_mm=360.0, cutoff_hz=200.0, segments=6, overlap_mm=12.0)
TURNTABLE = dict(platter_d_mm=300.0, rpm=78.26, crank_pulley_d_mm=60.0, belt_on="platter rim")
ARM = dict(effective_len_mm=230.0)  # pivot distance is optimised in tonearm()
RECORD = dict(outer_groove_r_mm=120.0, inner_groove_r_mm=55.0)  # 10-inch 78


def horn_profile():
    """Exponential horn S(x) = S0 * exp(m x), m = 4*pi*fc/c."""
    s0 = math.pi * (HORN["throat_d_mm"] / 2000) ** 2
    s1 = math.pi * (HORN["mouth_d_mm"] / 2000) ** 2
    m = 4 * math.pi * HORN["cutoff_hz"] / C
    length = math.log(s1 / s0) / m
    rows = []
    n = 40
    for i in range(n + 1):
        x = length * i / n
        r = math.sqrt(s0 * math.exp(m * x) / math.pi)
        rows.append((x * 1000, r * 1000))
    return m, length * 1000, rows


def segments(rows, length_mm, k):
    """Approximate the horn by k truncated cones; return flat patterns.

    Segment boundaries are spaced so each cone spans an equal ratio of radius
    (constant flare per segment). A truncated cone with end radii r1<r2 and
    slant height s unrolls into an annular sector with radii R1 = r1*s/(r2-r1),
    R2 = R1 + s and angle theta = 2*pi*r2/R2.
    """
    r0, rN = rows[0][1], rows[-1][1]
    m = math.log(rN / r0) / length_mm  # radius grows as exp(m x)
    segs = []
    for j in range(k):
        x1, x2 = length_mm * j / k, length_mm * (j + 1) / k
        r1, r2 = r0 * math.exp(m * x1), r0 * math.exp(m * x2)
        h = x2 - x1
        s = math.hypot(h, r2 - r1)
        R1 = r1 * s / (r2 - r1)
        R2 = R1 + s
        theta = 360.0 * r2 / R2
        segs.append(dict(segment=j + 1, x_start_mm=round(x1, 1), x_end_mm=round(x2, 1), r_small_mm=round(r1, 1),
                         r_large_mm=round(r2, 1), slant_mm=round(s, 1), pattern_inner_R_mm=round(R1, 1),
                         pattern_outer_R_mm=round(R2, 1), pattern_angle_deg=round(theta, 1),
                         glue_tab_mm=HORN["overlap_mm"]))
    return segs


def sector_svg(seg, path):
    R1, R2, th = seg["pattern_inner_R_mm"], seg["pattern_outer_R_mm"], seg["pattern_angle_deg"]
    tab = seg["glue_tab_mm"]
    th_tab = th + math.degrees(tab / R2)
    pad = 10
    def pt(R, a):
        a = math.radians(a)
        return R * math.sin(a), -R * math.cos(a)
    xs, ys = [], []
    for a in [i * th_tab / 50 for i in range(51)]:
        for R in (R1, R2):
            x, y = pt(R, a - th_tab / 2)
            xs.append(x)
            ys.append(y)
    minx, maxx, miny, maxy = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    w, h = maxx - minx, maxy - miny
    def arc(R, a0, a1, sweep):
        x0, y0 = pt(R, a0)
        x1, y1 = pt(R, a1)
        large = 1 if abs(a1 - a0) > 180 else 0
        return f"M{x0:.2f},{y0:.2f} A{R:.2f},{R:.2f} 0 {large} {sweep} {x1:.2f},{y1:.2f}"
    a0, a1 = -th_tab / 2, th_tab / 2
    p_outer = arc(R2, a0, a1, 1)
    p_inner = arc(R1, a1, a0, 0)
    ox0, oy0 = pt(R2, a0)
    ix1, iy1 = pt(R1, a1)
    ox1, oy1 = pt(R2, a1)
    ix0, iy0 = pt(R1, a0)
    fold = a0 + (th_tab - th)
    fx0, fy0 = pt(R1, fold)
    fx1, fy1 = pt(R2, fold)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}mm" height="{h:.1f}mm" viewBox="{minx:.2f} {miny:.2f} {w:.2f} {h:.2f}">
<rect x="{minx}" y="{miny}" width="{w}" height="{h}" fill="#ffffff"/>
<path d="{p_outer} L{ix1:.2f},{iy1:.2f} {p_inner[p_inner.index('A'):]} Z" fill="none" stroke="#000" stroke-width="0.4"/>
<line x1="{fx0:.2f}" y1="{fy0:.2f}" x2="{fx1:.2f}" y2="{fy1:.2f}" stroke="#000" stroke-width="0.3" stroke-dasharray="3 2"/>
<text x="{(minx + 5):.1f}" y="{(maxy - 5):.1f}" font-family="sans-serif" font-size="5">Horn segment {seg['segment']} - print at 100% (1:1). R1={R1} mm, R2={R2} mm, angle={th} deg + {tab} mm glue tab (dashed = fold)</text>
<line x1="{minx + 5:.1f}" y1="{maxy - 14:.1f}" x2="{minx + 55:.1f}" y2="{maxy - 14:.1f}" stroke="#000" stroke-width="0.6"/>
<text x="{minx + 5:.1f}" y="{maxy - 16:.1f}" font-family="sans-serif" font-size="4">50 mm check bar</text>
</svg>"""
    path.write_text(svg)
    return w, h


def strobe(mains_hz, path, d_mm=120.0):
    """Stroboscope disc: under light flickering at 2*mains, N bars look still at rpm."""
    flicker = 2 * mains_hz
    n = round(flicker * 60 / TURNTABLE["rpm"])
    rpm = flicker * 60 / n
    r1, r2 = d_mm / 2 - 14, d_mm / 2 - 2
    parts = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = a0 + math.pi / n
        pts = [(r1 * math.sin(a0), -r1 * math.cos(a0)), (r2 * math.sin(a0), -r2 * math.cos(a0)),
               (r2 * math.sin(a1), -r2 * math.cos(a1)), (r1 * math.sin(a1), -r1 * math.cos(a1))]
        parts.append("M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z")
    R = d_mm / 2
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{d_mm}mm" height="{d_mm}mm" viewBox="{-R} {-R} {d_mm} {d_mm}">
<circle r="{R - 0.5}" fill="#fff" stroke="#000" stroke-width="0.3"/>
<path d="{' '.join(parts)}" fill="#000"/>
<circle r="3.65" fill="none" stroke="#000" stroke-width="0.3"/>
<text y="-8" text-anchor="middle" font-family="sans-serif" font-size="4.2">{n} bars - still at {rpm:.2f} rpm</text>
<text y="0" text-anchor="middle" font-family="sans-serif" font-size="3.6">under {mains_hz} Hz mains lighting ({flicker} Hz flicker)</text>
<text y="7" text-anchor="middle" font-family="sans-serif" font-size="3.2">Print at 100%. Cut centre hole 7.3 mm.</text>
</svg>"""
    path.write_text(svg)
    return n, rpm


def tracking_error(r, L, d):
    """Angle (deg) between needle path (perpendicular to the arm) and the groove tangent."""
    cos_a = (r ** 2 + L ** 2 - d ** 2) / (2 * r * L)  # angle between arm and radius at the needle
    return 90 - math.degrees(math.acos(max(-1, min(1, cos_a))))


def tonearm():
    """A straight (no offset angle) arm tracks best with UNDERHANG: the needle path
    passes short of the spindle. Pick the pivot distance d that minimises the
    worst tracking error over the playing area."""
    L = ARM["effective_len_mm"]
    radii = range(int(RECORD["inner_groove_r_mm"]), int(RECORD["outer_groove_r_mm"]) + 1, 5)
    best = min((max(abs(tracking_error(r, L, d / 10)) for r in radii), d / 10) for d in range(int(L * 10), int(L * 12)))
    worst, d = best
    lines = [f"Effective length L = {L} mm (pivot to needle). Optimal pivot-to-spindle distance d = {d:.1f} mm",
             f"-> underhang {d - L:.1f} mm (needle arc passes this far short of the spindle centre).",
             "radius_mm  tracking_error_deg"]
    for r in radii:
        lines.append(f"{r:9d}  {tracking_error(r, L, d):7.1f}")
    lines.append(f"Worst tracking error {worst:.1f} deg. For comparison, the same arm with zero overhang (d = L) peaks at "
                 f"{max(abs(tracking_error(r, L, L)) for r in radii):.1f} deg.")
    return "\n".join(lines), d


def drawing(path, horn_len, mouth_d, d_pivot):
    W, H = 1100, 760
    s = 1.0  # 1 px = 1 mm (scaled in viewer)
    base_w, base_d = 460, 420
    ox, oy = 60, 60
    cx, cy = ox + 190, oy + 210  # spindle
    pr = TURNTABLE["platter_d_mm"] / 2
    px, py = cx + d_pivot * math.cos(math.radians(-35)), cy + d_pivot * math.sin(math.radians(-35))
    # needle position on a record radius ~ 100 mm
    def needle_at(r):
        L = ARM["effective_len_mm"]
        # intersection of circle(center spindle, r) and circle(center pivot, L)
        dx, dy = cx - px, cy - py
        dd = math.hypot(dx, dy)
        a = (L ** 2 - r ** 2 + dd ** 2) / (2 * dd)
        hgt = math.sqrt(max(0, L ** 2 - a ** 2))
        xm, ym = px + a * dx / dd, py + a * dy / dd
        return xm + hgt * dy / dd, ym - hgt * dx / dd
    nx, ny = needle_at(100)
    side_y = 560
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="13">
<rect width="{W}" height="{H}" fill="#fff"/>
<text x="{ox}" y="34" font-size="18">Echoes Recovered acoustic phonograph - general arrangement (dimensions in mm)</text>
<g stroke="#000" fill="none" stroke-width="1.2">
  <rect x="{ox}" y="{oy}" width="{base_w}" height="{base_d}"/>
  <circle cx="{cx}" cy="{cy}" r="{pr}"/>
  <circle cx="{cx}" cy="{cy}" r="127" stroke-dasharray="6 4"/>
  <circle cx="{cx}" cy="{cy}" r="4"/>
  <circle cx="{px:.1f}" cy="{py:.1f}" r="16"/>
  <line x1="{px:.1f}" y1="{py:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" stroke-width="9" stroke="#999"/>
  <circle cx="{nx:.1f}" cy="{ny:.1f}" r="26"/>
  <circle cx="{ox + base_w - 50}" cy="{oy + base_d - 60}" r="30"/>
</g>
<g font-size="12">
  <text x="{cx - 40}" y="{cy + pr + 18}">platter {TURNTABLE['platter_d_mm']:.0f}</text>
  <text x="{cx - 60}" y="{cy - 133}">10-in record (254)</text>
  <text x="{px + 20:.0f}" y="{py - 18:.0f}">tonearm pivot / horn throat</text>
  <text x="{nx - 120:.0f}" y="{ny + 44:.0f}">soundbox (diaphragm 50, needle)</text>
  <text x="{ox + base_w - 150}" y="{oy + base_d - 100}">crank pulley {TURNTABLE['crank_pulley_d_mm']:.0f}</text>
  <text x="{ox}" y="{oy + base_d + 22}">base {base_w} x {base_d} x 18 plywood · spindle-to-pivot {d_pivot:.0f} · arm {ARM['effective_len_mm']:.0f}</text>
</g>
<g transform="translate(560,70)">
  <text x="0" y="0" font-size="14">Horn (exponential, cut-off {HORN['cutoff_hz']:.0f} Hz)</text>
  <text x="0" y="20">throat {HORN['throat_d_mm']:.0f} -> mouth {mouth_d:.0f}, length {horn_len:.0f}</text>
</g>
<g transform="translate(580,140)" stroke="#000" fill="none" stroke-width="1.2">
"""
    m, L, rows = horn_profile()
    k = 380 / L
    up = " ".join(f"{x * k:.1f},{-r * k:.1f}" for x, r in rows)
    dn = " ".join(f"{x * k:.1f},{r * k:.1f}" for x, r in rows)
    svg += f'<polyline points="{up}"/><polyline points="{dn}"/><line x1="{L * k:.1f}" y1="{-rows[-1][1] * k:.1f}" x2="{L * k:.1f}" y2="{rows[-1][1] * k:.1f}"/>'
    svg += f'<text x="0" y="{rows[-1][1] * k + 30:.0f}" stroke="none" fill="#000">drawn at {k:.2f}:1</text></g>'
    # side elevation
    svg += f"""
<g stroke="#000" fill="none" stroke-width="1.2">
  <rect x="{ox}" y="{side_y}" width="{base_w}" height="18"/>
  <rect x="{cx - pr}" y="{side_y - 22}" width="{2 * pr}" height="18"/>
  <rect x="{cx - 20}" y="{side_y + 18}" width="40" height="60"/>
  <line x1="{cx}" y1="{side_y - 40}" x2="{cx}" y2="{side_y + 78}"/>
  <rect x="{px - 18:.0f}" y="{side_y - 90}" width="36" height="90"/>
  <polyline points="{px:.0f},{side_y - 90} {px:.0f},{side_y - 110} {cx + 60},{side_y - 70} {cx + 60},{side_y - 34}"/>
  <rect x="{cx + 40}" y="{side_y - 46}" width="42" height="12"/>
</g>
<g font-size="12">
  <text x="{ox}" y="{side_y - 130}" font-size="14">Side elevation (schematic)</text>
  <text x="{cx - 120}" y="{side_y + 100}">bearing block: 2 x 627ZZ (7x22x7) on 7 mm spindle</text>
  <text x="{px + 24:.0f}" y="{side_y - 60}">pivot post: 608ZZ, horn throat below</text>
  <text x="{cx + 90}" y="{side_y - 30}">needle on record</text>
</g>
</svg>"""
    path.write_text(svg)


def main():
    OUT.mkdir(exist_ok=True)
    m, L, rows = horn_profile()
    with open(OUT / "horn_profile.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["x_mm_from_throat", "radius_mm", "diameter_mm"])
        for x, r in rows:
            w.writerow([round(x, 1), round(r, 1), round(2 * r, 1)])
    segs = segments(rows, L, HORN["segments"])
    with open(OUT / "horn_segments.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(segs[0]))
        w.writeheader()
        w.writerows(segs)
    sizes = [sector_svg(s, OUT / f"horn_template_{s['segment']}.svg") for s in segs]
    n50, rpm50 = strobe(50, OUT / "strobe_50hz.svg")
    n60, rpm60 = strobe(60, OUT / "strobe_60hz.svg")
    arm_txt, d = tonearm()
    (OUT / "tonearm.txt").write_text(arm_txt + "\n")
    drawing(OUT / "drawing.svg", L, HORN["mouth_d_mm"], d)
    ratio = TURNTABLE["platter_d_mm"] / TURNTABLE["crank_pulley_d_mm"]
    print(f"Horn: m = {m:.3f} 1/m, length = {L:.0f} mm, throat {HORN['throat_d_mm']} -> mouth {HORN['mouth_d_mm']} mm")
    print("  ideal mouth diameter for full loading at cut-off (circumference = wavelength): "
          f"{C / (math.pi * HORN['cutoff_hz']) * 1000:.0f} mm")
    for s, (w_, h_) in zip(segs, sizes):
        print(f"  segment {s['segment']}: r {s['r_small_mm']}->{s['r_large_mm']} mm, flat R1={s['pattern_inner_R_mm']} R2={s['pattern_outer_R_mm']} angle {s['pattern_angle_deg']} deg, sheet {w_:.0f}x{h_:.0f} mm")
    print(f"Strobe: 50 Hz -> {n50} bars ({rpm50:.2f} rpm); 60 Hz -> {n60} bars ({rpm60:.2f} rpm)")
    print(f"Drive: belt on {TURNTABLE['platter_d_mm']:.0f} mm platter rim from {TURNTABLE['crank_pulley_d_mm']:.0f} mm pulley = {ratio:.1f}:1 -> crank at {TURNTABLE['rpm'] / ratio:.1f} rpm for {TURNTABLE['rpm']} rpm")
    print(arm_txt)


if __name__ == "__main__":
    main()
