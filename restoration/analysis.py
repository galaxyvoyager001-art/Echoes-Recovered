"""Damage analysis for acoustic-era recordings.

All measurements are computed the same way on the original and on the restored
file, so the before/after numbers are directly comparable.
"""
from __future__ import annotations

import numpy as np
from scipy import signal

from . import dsp

EPS = 1e-12


def to_db(p):
    return 10 * np.log10(np.maximum(p, EPS))


def frame_rms_db(x, sr, win_s=0.05):
    n = int(win_s * sr)
    m = len(x) // n
    fr = x[: m * n].reshape(m, n)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + EPS), n


def music_bounds(x, sr, thresh_db=12.0):
    """Find where music starts/ends: frames > (lead-in noise level + thresh_db)."""
    db, n = frame_rms_db(x, sr, 0.1)
    from scipy.ndimage import uniform_filter1d
    dbs = uniform_filter1d(db, 5)  # 0.5 s smoothing so isolated clicks do not count
    level = np.median(dbs)
    active = dbs > level - thresh_db
    idx = np.flatnonzero(active)
    if idx.size == 0:
        return 0.0, len(x) / sr, level
    start, end = idx[0], idx[-1]
    # music onset: only if the first 0.5 s is clearly quieter than the music (a real
    # lead-in groove), take the first point where the level rises 6 dB above it
    lead = dbs[:5].mean()
    if lead < level - 10:
        rise = np.flatnonzero(dbs > lead + 6)
        if rise.size and rise[0] * n / sr < 6.0:
            start = max(0, rise[0] - 1)
    else:
        start = 0
    return start * n / sr, (end + 1) * n / sr, level


def impulse_rate(x, sr, k=8.0, order=24):
    """Impulses per minute detected by the AR residual detector (fixed settings)."""
    regions, _, _ = dsp.detect_impulses(x, sr, order, k)
    return len(regions) / (len(x) / sr / 60.0), regions


def bandwidth(x, sr, margin_db=0.5):
    """Estimate the band that actually carries programme (music) energy.

    Stationary surface noise has an exponential power distribution in every
    STFT bin, for which median/10th-percentile is about 8.2 dB. Bins carrying
    music are more dynamic, so the ratio rises. A band is 'usable' when the
    1/3-octave-smoothed ratio exceeds the 8-16 kHz (noise-only) plateau by
    margin_db. Robust to clicks because medians/percentiles are used.
    """
    f, _, Z = dsp.stft(x, sr)
    P = np.abs(Z) ** 2
    ratio = to_db(np.median(P, axis=1)) - to_db(np.percentile(P, 10, axis=1))
    sm = dsp.octave_smooth(f, ratio, 3.0)
    # reference: 8-16 kHz, where acoustic-era recordings carry essentially no music
    plateau = float(np.median(sm[(f > 8000) & (f < 16000)]))
    ok = sm > plateau + margin_db
    hi_c = f[(f > 1000) & (f < 10000) & ok]
    lo_c = f[(f > 20) & (f < 1000) & ok]
    hi = float(hi_c.max()) if hi_c.size else 3000.0
    lo = float(lo_c.min()) if lo_c.size else 150.0
    return lo, hi, f, sm


def hum_scan(x, sr, bases=(50.0, 60.0), n_harm=4, thresh_db=10.0):
    f, pxx = signal.welch(x, fs=sr, nperseg=1 << 15)
    db = to_db(pxx)
    found = []
    for b in bases:
        for h in range(1, n_harm + 1):
            fh = b * h
            i = np.argmin(np.abs(f - fh))
            nb = (np.abs(f - fh) > 3) & (np.abs(f - fh) < 15)
            prom = db[i] - np.median(db[nb])
            if prom > thresh_db:
                found.append({"freq_hz": fh, "prominence_db": round(float(prom), 1)})
    return found


def hiss_ratio_db(x, sr, f_lo=5000, f_hi=10000):
    """Energy in a high band (above most acoustic recordings' content) vs 300-3000 Hz."""
    f, pxx = signal.welch(x, fs=sr, nperseg=4096)
    hb = pxx[(f >= f_lo) & (f <= f_hi)].sum()
    mb = pxx[(f >= 300) & (f <= 3000)].sum()
    return float(to_db(hb) - to_db(mb))


def clipping(x, thresh=0.985):
    peak = np.max(np.abs(x))
    return {"peak_dbfs": round(float(20 * np.log10(peak + EPS)), 2),
            "samples_over_98.5pct_fullscale": int(np.sum(np.abs(x) >= thresh))}


def tuning_and_wow(x, sr, max_s=90.0):
    """Tuning offset vs A=440 and wow (rotational pitch modulation) indicators."""
    import librosa
    y = signal.resample_poly(x[: int(max_s * sr)], 1, 4)  # 11025 Hz
    srr = sr // 4
    tun = float(librosa.estimate_tuning(y=y, sr=srr)) * 100.0
    hop = 256
    f0, vflag, _ = librosa.pyin(y, fmin=80, fmax=1000, sr=srr, hop_length=hop, frame_length=2048)
    fr = srr / hop
    cents = 1200 * np.log2(np.where(vflag, f0, np.nan) / 440.0)
    # remove note changes: deviation from a 0.25 s running median, only inside voiced runs
    from scipy.ndimage import median_filter
    c = np.copy(cents)
    good = np.isfinite(c)
    if good.sum() < fr * 5:
        return {"tuning_offset_cents_vs_A440": round(tun, 1), "wow": None}
    cf = np.where(good, c, np.nanmedian(c))
    dev = cf - median_filter(cf, size=int(fr * 2.0) | 1)
    dev[~good] = 0.0
    dev = np.clip(dev, -60, 60)
    fq, pw = signal.welch(dev, fs=fr, nperseg=min(len(dev), int(fr * 16)))
    band = (fq > 1.0) & (fq < 1.6)       # 60-96 rpm rotation range
    ref = (fq > 0.4) & (fq < 3.0) & ~band
    bi = np.flatnonzero(band)
    peak_i = bi[np.argmax(pw[bi])]
    is_local_max = bool(pw[peak_i] > pw[peak_i - 1] and pw[peak_i] > pw[peak_i + 1] and peak_i not in (bi[0], bi[-1]))
    ratio = float(to_db(pw[peak_i]) - to_db(np.median(pw[ref])))
    if not is_local_max:
        ratio = 0.0
    return {"tuning_offset_cents_vs_A440": round(tun, 1),
            "wow": {"peak_freq_hz": round(float(fq[peak_i]), 3), "implied_rpm": round(float(fq[peak_i] * 60), 1),
                    "peak_over_neighbourhood_db": round(ratio, 1), "distinct_peak": is_local_max,
                    "voiced_fraction": round(float(good.mean()), 2)}}


def analyze(x, sr, lead_in_s=None, with_pitch=True):
    """Full damage report for one mono signal."""
    t0, t1, floor_db = music_bounds(x, sr)
    lead = t0 if lead_in_s is None else lead_in_s
    nf, npsd, method = dsp.noise_profile(x, sr, lead)
    music = x[int(t0 * sr) : int(t1 * sr)]
    db, _ = frame_rms_db(music, sr)
    prog_db = float(np.percentile(db, 90))
    # surface-noise level: lead-in RMS if available, else 5th percentile frame level
    if lead >= 0.5:
        seg = x[int(0.1 * sr) : int((lead - 0.05) * sr)]
        noise_db = float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + EPS))
    else:
        noise_db = float(np.percentile(frame_rms_db(x, sr)[0], 5))
    # noise floor *during* the music: quietest 5% of 50 ms frames (pauses between phrases)
    noise_in_music = float(np.percentile(db, 5))
    rate, regions = impulse_rate(music, sr)
    lens = np.array([e - s for s, e in regions]) if regions else np.array([0])
    lo, hi, _, _ = bandwidth(music, sr)
    return {
        "duration_s": round(len(x) / sr, 2),
        "music_start_s": round(t0, 2), "music_end_s": round(t1, 2),
        "lead_in_s": round(lead, 2),
        "noise_profile_method": method,
        "surface_noise_rms_dbfs": round(noise_db, 1),
        "programme_level_p90_dbfs": round(prog_db, 1),
        "est_snr_db": round(prog_db - noise_db, 1),
        "noise_floor_in_music_p5_dbfs": round(noise_in_music, 1),
        "impulses_per_min": round(rate, 1),
        "impulse_len_median_ms": round(float(np.median(lens)) / sr * 1000, 2),
        "impulses_longer_than_2ms": int(np.sum(lens > 0.002 * sr)),
        "hiss_band_5_10k_vs_mid_db": round(hiss_ratio_db(music, sr), 1),
        "usable_band_hz": [round(lo), round(hi)],
        "hum": hum_scan(x, sr),
        "clipping": clipping(x),
        **(tuning_and_wow(music, sr) if with_pitch else {}),
    }
