#!/usr/bin/env python3
"""Step 2 - analyse and restore every cleared recording.

Reads   data/originals/<slug>/loc_original.wav     (never modified)
Writes  data/restored/<slug>/
          restored.flac           16-bit (TPDF-dithered) mono restored master
          restored.mp3            web copy (LAME VBR ~190 kbps)
          ab_compare.mp3          same passages: Original -> Restored, x3
          removed_component.mp3   original minus restored = what was taken out
          analysis.json           damage analysis before & after
          params.json             parameters actually used (+ auto rationale)
          restoration_log.md      human-readable log
          waveform.png / spectrogram.jpg / spectrum.png

Usage: python scripts/02_restore.py [--only jukebox-123 ...] [--workers 3]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from restoration import analysis, pipeline, plots  # noqa: E402
from restoration.text import name_case  # noqa: E402

META = ROOT / "data" / "metadata"
ORIG = ROOT / "data" / "originals"
REST = ROOT / "data" / "restored"


def jdump(obj, path):
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def mp3(src: Path, dst: Path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-codec:a", "libmp3lame", "-q:a", "2", str(dst)], check=True)


def ab_compare(x, y, sr, t_start, t_end, seg_s=6.0, gap_s=0.6, n=3):
    """Original/Restored pairs of identical passages, both at matched loudness."""
    span = t_end - t_start
    starts = [t_start + span * f for f in (0.15, 0.45, 0.75)][:n]
    gap = np.zeros(int(gap_s * sr))
    fade = np.linspace(0, 1, int(0.02 * sr))
    parts, cues, t = [], [], 0.0
    for s in starts:
        a, b = int(s * sr), int((s + seg_s) * sr)
        for lab, sig in (("Original", x), ("Restored", y)):
            seg = sig[a:b].copy()
            seg[: len(fade)] *= fade
            seg[-len(fade):] *= fade[::-1]
            parts += [seg, gap]
            cues.append({"label": lab, "source_start_s": round(s, 2), "at_s": round(t, 2), "length_s": seg_s})
            t += seg_s + gap_s
    return np.concatenate(parts), cues


def md_table(before, after, keys):
    rows = ["| Measure | Original | Restored |", "|---|---|---|"]
    for k, label in keys:
        rows.append(f"| {label} | {before.get(k)} | {after.get(k, 'n/a')} |")
    return "\n".join(rows)


KEYS = [
    ("surface_noise_rms_dbfs", "Surface-noise RMS in lead-in / quietest frames (dBFS)"),
    ("noise_floor_in_music_p5_dbfs", "Noise floor during music, 5th pct. 50 ms frames (dBFS)"),
    ("est_snr_db", "Programme (p90) minus surface noise (dB)"),
    ("impulses_per_min", "Impulses per minute (AR detector, k=8)"),
    ("impulses_longer_than_2ms", "Impulses longer than 2 ms"),
    ("hiss_band_5_10k_vs_mid_db", "5-10 kHz energy relative to 300-3000 Hz (dB)"),
]


def process(meta_path: Path, overrides: dict) -> dict:
    meta = json.loads(meta_path.read_text())
    slug = meta["slug"]
    src = ORIG / slug / "loc_original.wav"
    out = REST / slug
    out.mkdir(parents=True, exist_ok=True)
    raw, sr = sf.read(src, always_2d=True)
    corr = float(np.corrcoef(raw[:, 0], raw[:, 1])[0, 1]) if raw.shape[1] > 1 else 1.0
    x = raw.mean(axis=1)

    before = analysis.analyze(x, sr)
    params, why = pipeline.auto_params(before)
    ov = overrides.get(meta["id"], {})
    if ov:
        params = pipeline.deep_update(params, {k: v for k, v in ov.items() if not k.startswith("_")})
    y, log, ex = pipeline.restore(x, sr, params, before)
    after = analysis.analyze(y, sr, lead_in_s=before["lead_in_s"], with_pitch=False)
    after.pop("usable_band_hz", None)  # not meaningful after gating

    # 16-bit master with TPDF dither (+/-1 LSB, about -96 dBFS) - same word length as the LoC source
    rng = np.random.default_rng(0)
    dith = (rng.random(len(y)) - rng.random(len(y))) / 32768.0
    sf.write(out / "restored.flac", np.clip(y + dith, -1, 1), sr, subtype="PCM_16")
    tmpwav = out / "_tmp.wav"
    sf.write(tmpwav, y, sr, subtype="PCM_16")
    mp3(tmpwav, out / "restored.mp3")
    removed_stats = None
    if "removed" in ex:
        r = ex["removed"]
        sf.write(tmpwav, np.clip(r, -1, 1), sr, subtype="PCM_16")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmpwav), "-codec:a", "libmp3lame", "-q:a", "6",
                        str(out / "removed_component.mp3")], check=True)
        from scipy import signal as ss
        f, pr = ss.welch(r, fs=sr, nperseg=4096)
        _, px = ss.welch(x, fs=sr, nperseg=4096)
        mid = (f >= 300) & (f <= 3000)
        removed_stats = {
            "removed_rms_dbfs": round(float(20 * np.log10(np.sqrt(np.mean(r ** 2)) + 1e-12)), 1),
            "removed_vs_original_energy_300_3000hz_db": round(float(10 * np.log10(pr[mid].sum() / px[mid].sum())), 1),
            "removed_vs_original_energy_above_5khz_db": round(float(10 * np.log10(pr[f > 5000].sum() / px[f > 5000].sum())), 1),
        }
    ab, cues = ab_compare(x, y, sr, before["music_start_s"], before["music_end_s"])
    sf.write(tmpwav, ab, sr, subtype="PCM_16")
    mp3(tmpwav, out / "ab_compare.mp3")
    tmpwav.unlink()

    title = f"{meta['title']} - {name_case(meta['primary_performer'])} ({meta['recording_date']})"
    plots.waveform(x, y, sr, ex["click_regions"], title, out / "waveform.png")
    plots.spectrogram(x, y, sr, title, out / "spectrogram.jpg")
    plots.spectrum(x, y, sr, ex.get("eq_curve"), before["usable_band_hz"], title, out / "spectrum.png")

    jdump({"before": before, "after": after, "removed_component": removed_stats,
           "source_channel_correlation": round(corr, 6)}, out / "analysis.json")
    jdump({"params": params, "auto_rationale": why, "overrides": ov, "stage_log": log, "ab_cues": cues,
           "source": str(src.relative_to(ROOT)), "source_sha256": meta["downloads"]["wav"]["sha256"]}, out / "params.json")

    stages = "\n".join(f"{i + 1}. **{s['stage']}** - " + ", ".join(f"{k}={v}" for k, v in s.items() if k != "stage")
                       for i, s in enumerate(log))
    md = f"""# Restoration log - {meta['title']}

* **Performer:** {name_case(meta['primary_performer'])}  ·  **Recorded:** {meta['recording_date']}, {meta['recording_city']}
* **LoC item:** {meta['loc_item_url']}  ·  **Disc:** {meta['disc'].get('label')} {meta['disc'].get('catalog_number')}  ·  **Matrix/take:** {meta['matrix']} / {meta['take']}
* **Source file:** `{src.relative_to(ROOT)}` (SHA-256 `{meta['downloads']['wav']['sha256'][:16]}...`, left unmodified)
* **Source format:** {sr} Hz, {raw.shape[1]} ch; L/R correlation {corr:.6f} -> folded to mono

## Damage assessment (original)
* Surface noise: {before['surface_noise_rms_dbfs']} dBFS (measured from {before['noise_profile_method']}); programme p90 {before['programme_level_p90_dbfs']} dBFS -> SNR ~{before['est_snr_db']} dB
* Clicks/crackle: {before['impulses_per_min']} impulses/min, median length {before['impulse_len_median_ms']} ms, {before['impulses_longer_than_2ms']} longer than 2 ms
* Hiss: 5-10 kHz band sits {before['hiss_band_5_10k_vs_mid_db']} dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~{before['usable_band_hz'][0]}-{before['usable_band_hz'][1]} Hz (acoustic horn recording)
* Hum: {before['hum'] or 'none detected'}
* Peaks/clipping: {before['clipping']}
* Tuning offset vs A440: {before.get('tuning_offset_cents_vs_A440')} cents; wow indicator: {before.get('wow')}

## Why these parameters
""" + "\n".join(f"* {w}" for w in why) + (f"\n* Manual override: `{json.dumps(ov)}`" if ov else "") + f"""

## Processing chain (as executed)
{stages}

## Before / after (same measurement code on both files)
{md_table(before, after, KEYS)}

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {removed_stats}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max {params['declick']['max_ms']} ms per gap; {log[2]['percent_samples_replaced'] + log[3]['percent_samples_replaced']:.2f}% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
"""
    (out / "restoration_log.md").write_text(md)
    return {"slug": slug, "before": before, "after": after}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    ovp = ROOT / "config" / "overrides.json"
    overrides = json.loads(ovp.read_text()) if ovp.exists() else {}
    metas = []
    for m in sorted(META.glob("*.json")):
        d = json.loads(m.read_text())
        if d["rights"]["cleared_for_reuse"] and (not a.only or d["id"] in a.only):
            metas.append(m)
    with ProcessPoolExecutor(a.workers) as ex:
        futs = {ex.submit(process, m, overrides): m for m in metas}
        for f, m in futs.items():
            try:
                r = f.result()
                b, af = r["before"], r["after"]
                print(f"OK  {r['slug'][:50]:50s} noise {b['surface_noise_rms_dbfs']}->{af['surface_noise_rms_dbfs']} dBFS  "
                      f"impulses/min {b['impulses_per_min']}->{af['impulses_per_min']}", flush=True)
            except Exception as e:
                print(f"ERR {m.name}: {e!r}", flush=True)


if __name__ == "__main__":
    main()
