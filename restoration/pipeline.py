"""Restoration pipeline: analysis -> per-recording parameters -> processing.

Stage order (each stage is optional and fully parameterised):
  0. mono fold          LoC transfers of these lateral discs are dual-mono
  1. speed correction   only when explicitly set in config/overrides.json
  2. rumble/DC high-pass + hum notches (only if hum is detected)
  3. declick  (pass 1)  AR-residual detection, LSAR interpolation, <= 4 ms
  4. decrackle (pass 2) lower threshold, <= 1 ms, auto-backs-off if it would
                        replace too many samples (protects musical transients)
  5. spectral denoise   decision-directed Wiener, noise profile from lead-in
                        groove or minimum statistics, bounded gain floor
  6. hiss low-pass      above the measured usable band of the recording
  7. adaptive EQ        bounded resonance flattening inside the usable band
  8. level match        restored file matched to the original's loudness
"""
from __future__ import annotations

import copy
import json
import time

import numpy as np
import pyloudnorm as pyln

from . import analysis, dsp

DEFAULTS = {
    "speed_ratio": 1.0,
    "highpass_hz": None,          # auto
    "hum_notch_hz": None,         # auto (from hum scan)
    "declick": {"order": 32, "k": None, "max_ms": 4.0, "max_percent_replaced": 2.0},
    "decrackle": {"order": 24, "k": None, "max_ms": 1.0, "max_percent_replaced": 1.5},
    "denoise": {"over_sub": None, "gain_floor_db": None, "dd_alpha": 0.96},
    "lowpass_hz": None,
    "eq": {"enabled": True, "f_lo": None, "f_hi": None, "strength": 0.5, "max_db": 4.0, "max_boost_db": 2.5, "tilt_db_per_oct": 0.0},
    "loudness": "match_original",
}


def deep_update(base: dict, upd: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (upd or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_update(out[k], v)
        else:
            out[k] = v
    return out


def auto_params(rep: dict) -> tuple[dict, list[str]]:
    """Derive parameters from the damage analysis. Returns (params, rationale)."""
    p = copy.deepcopy(DEFAULTS)
    why = []
    lo, hi = rep["usable_band_hz"]
    p["highpass_hz"] = 50.0
    why.append("High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.")
    if rep["hum"]:
        p["hum_notch_hz"] = [h["freq_hz"] for h in rep["hum"]]
        why.append(f"Hum detected at {p['hum_notch_hz']} Hz -> narrow notches (Q=30).")
    else:
        p["hum_notch_hz"] = []
        why.append("No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.")
    ipm = rep["impulses_per_min"]
    p["declick"]["k"] = 7.0 if ipm > 1500 else 8.0
    p["decrackle"]["k"] = 5.0 if ipm > 400 else 5.5
    why.append(f"{ipm:.0f} impulses/min measured -> declick threshold {p['declick']['k']} sigma, decrackle {p['decrackle']['k']} sigma.")
    snr = rep["est_snr_db"]
    # worn, low-SNR discs get *gentler* reduction: there the noise overlaps the music
    # in every band, and pushing harder mostly creates artefacts
    if snr < 12:
        p["denoise"].update(over_sub=1.3, gain_floor_db=-10.0)
    elif snr < 20:
        p["denoise"].update(over_sub=1.3, gain_floor_db=-13.0)
    else:
        p["denoise"].update(over_sub=1.2, gain_floor_db=-15.0)
    why.append(f"Estimated SNR {snr} dB -> noise over-subtraction x{p['denoise']['over_sub']}, gain floor {p['denoise']['gain_floor_db']} dB (keeps some surface noise rather than create artefacts).")
    p["lowpass_hz"] = float(np.clip(1.6 * hi, 4500, 8000))
    why.append(f"Usable band ends near {hi} Hz -> hiss low-pass at {p['lowpass_hz']:.0f} Hz (well above the last musical content).")
    p["eq"]["f_lo"] = 250.0
    p["eq"]["f_hi"] = float(min(max(hi, 2500), 4000))
    why.append(f"Adaptive EQ restricted to {p['eq']['f_lo']:.0f}-{p['eq']['f_hi']:.0f} Hz, strength {p['eq']['strength']}, cuts <= {p['eq']['max_db']} dB, boosts <= {p['eq']['max_boost_db']} dB.")
    return p, why


def lufs(x, sr):
    m = pyln.Meter(sr)
    return float(m.integrated_loudness(x))


def restore(x: np.ndarray, sr: int, params: dict, rep: dict):
    """Run the pipeline. Returns (restored, stage_log, extras for plotting)."""
    log, extras = [], {}
    t0 = time.time()
    y = x.copy()

    if params["speed_ratio"] and abs(params["speed_ratio"] - 1.0) > 1e-6:
        y = dsp.change_speed(y, params["speed_ratio"])
        log.append({"stage": "speed correction", "ratio": params["speed_ratio"]})
    else:
        log.append({"stage": "speed correction", "applied": False,
                    "reason": "no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards"})

    y = dsp.highpass(y, sr, params["highpass_hz"], order=4)
    st = {"stage": "high-pass (rumble/DC)", "fc_hz": round(params["highpass_hz"], 1), "order": 4, "zero_phase": True}
    if params["hum_notch_hz"]:
        y = dsp.notch_harmonics(y, sr, params["hum_notch_hz"])
        st["hum_notches_hz"] = params["hum_notch_hz"]
    log.append(st)

    dc = params["declick"]
    k1 = dc["k"]
    for attempt in range(6):
        y1, s1, reg1 = dsp.declick(y, sr, dc["order"], k1, dc["max_ms"])
        if s1["percent_samples_replaced"] <= dc["max_percent_replaced"]:
            break
        k1 += 0.5
    y = y1
    log.append({"stage": "declick (AR detection + LSAR interpolation)", "order": dc["order"], "k_requested": dc["k"],
                "k": k1, "max_ms": dc["max_ms"], "max_percent_replaced": dc["max_percent_replaced"], **s1})
    extras["click_regions"] = reg1

    cr = params["decrackle"]
    k = cr["k"]
    for attempt in range(6):
        y2, s2, reg2 = dsp.declick(y, sr, cr["order"], k, cr["max_ms"])
        if s2["percent_samples_replaced"] <= cr["max_percent_replaced"]:
            break
        k += 0.5
    y = y2
    log.append({"stage": "decrackle (pass 2)", "order": cr["order"], "k_requested": cr["k"], "k_used": k,
                "max_ms": cr["max_ms"], **s2})
    extras["crackle_regions"] = reg2

    nf, npsd, method = dsp.noise_profile(y, sr, rep["lead_in_s"])
    dn = params["denoise"]
    y, mean_gain = dsp.spectral_denoise(y, sr, npsd, dn["over_sub"], dn["gain_floor_db"], dn["dd_alpha"])
    log.append({"stage": "spectral denoise (decision-directed Wiener)", **dn, "noise_profile": method,
                "stft": "2048 Hann / hop 512", "mean_gain_db": round(mean_gain, 2)})
    extras["noise_psd"] = (nf, npsd)

    y = dsp.lowpass(y, sr, params["lowpass_hz"], order=4)
    log.append({"stage": "hiss low-pass", "fc_hz": round(params["lowpass_hz"]), "order": 4, "zero_phase": True})

    if len(y) == len(x):
        # what the noise/click stages took out (EQ is a deliberate tonal change, measured separately)
        extras["removed"] = x - y
    eq = params["eq"]
    if eq["enabled"]:
        y, ef, corr = dsp.adaptive_eq(y, sr, eq["f_lo"], eq["f_hi"], eq["strength"], eq["max_db"], eq["tilt_db_per_oct"], eq["max_boost_db"])
        band = (ef >= eq["f_lo"]) & (ef <= eq["f_hi"])
        log.append({"stage": "adaptive EQ (resonance flattening)", **eq,
                    "applied_range_db": [round(float(corr[band].min()), 2), round(float(corr[band].max()), 2)]})
        extras["eq_curve"] = (ef, corr)

    lo_in, lo_out = lufs(x, sr), lufs(y, sr)
    g = 10 ** ((lo_in - lo_out) / 20)
    peak = np.max(np.abs(y * g))
    if peak > 0.891:  # keep -1 dBFS headroom; plain gain only, no limiter
        g *= 0.891 / peak
    y = y * g
    log.append({"stage": "level match", "original_lufs": round(lo_in, 2), "restored_lufs": round(lufs(y, sr), 2),
                "gain_db": round(20 * np.log10(g), 2), "limiter": False})
    log.append({"stage": "timing", "seconds": round(time.time() - t0, 1)})
    return y, log, extras
