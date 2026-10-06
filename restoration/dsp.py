"""Core DSP building blocks for acoustic-era disc restoration.

Every function here is deterministic signal processing (filters, AR models,
STFT-domain gain rules). Nothing is synthesised: each stage either attenuates
energy judged to be noise or replaces a few milliseconds of samples that were
destroyed by an impulse with an autoregressive interpolation computed from the
surrounding real samples.
"""
from __future__ import annotations

import numpy as np
from scipy import signal
from scipy.linalg import solve_toeplitz

EPS = 1e-12


# --------------------------------------------------------------------------- #
# Filters
# --------------------------------------------------------------------------- #
def highpass(x: np.ndarray, sr: int, fc: float, order: int = 4) -> np.ndarray:
    sos = signal.butter(order, fc, btype="highpass", fs=sr, output="sos")
    return signal.sosfiltfilt(sos, x)


def lowpass(x: np.ndarray, sr: int, fc: float, order: int = 4) -> np.ndarray:
    sos = signal.butter(order, fc, btype="lowpass", fs=sr, output="sos")
    return signal.sosfiltfilt(sos, x)


def notch_harmonics(x: np.ndarray, sr: int, freqs: list[float], q: float = 30.0) -> np.ndarray:
    for f in freqs:
        b, a = signal.iirnotch(f, q, fs=sr)
        x = signal.filtfilt(b, a, x)
    return x


# --------------------------------------------------------------------------- #
# Autoregressive modelling (Levinson) - used for click detection/interpolation
# --------------------------------------------------------------------------- #
def ar_coeffs(x: np.ndarray, order: int) -> np.ndarray:
    """Return prediction coefficients a[1..p] such that x[n] ~ sum a_k x[n-k]."""
    x = x - x.mean()
    r = np.correlate(x, x, mode="full")[len(x) - 1 : len(x) + order]
    if r[0] <= EPS:
        return np.zeros(order)
    r = r.copy()
    r[0] *= 1.0 + 1e-6  # tiny white-noise correction for numerical stability
    return solve_toeplitz(r[:order], r[1 : order + 1])


def ar_residual(x: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Prediction error e[n] = x[n] - sum a_k x[n-k]."""
    return signal.lfilter(np.concatenate(([1.0], -a)), [1.0], x)


def lsar_interpolate(seg: np.ndarray, missing: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Least-squares AR interpolation (Janssen et al. 1986; Godsill & Rayner 1998).

    seg      : samples incl. >= p known samples of context on both sides
    missing  : boolean mask of samples to re-estimate
    a        : AR coefficients (order p)
    Minimises the AR prediction-error energy over the segment w.r.t. the
    missing samples only; known samples are never changed.
    """
    p, n = len(a), len(seg)
    rows = n - p
    A = np.zeros((rows, n))
    coef = np.concatenate((-a[::-1], [1.0]))  # x[n-p] ... x[n]
    for i in range(rows):
        A[i, i : i + p + 1] = coef
    Au, Ak = A[:, missing], A[:, ~missing]
    rhs = -Ak @ seg[~missing]
    sol, *_ = np.linalg.lstsq(Au, rhs, rcond=None)
    out = seg.copy()
    out[missing] = sol
    return out


def detect_impulses(x: np.ndarray, sr: int, order: int, k: float, block: int = 4096,
                    pre: int = 3, post: int = 6, merge_gap: int = 12):
    """Detect impulsive damage via AR prediction-error thresholding.

    Returns (list of (start, stop) sample regions, per-block AR coefs, block size).
    Threshold is k x robust sigma (1.4826 * MAD) of the residual in each block,
    so it adapts to local programme level.
    """
    n = len(x)
    flags = np.zeros(n, dtype=bool)
    coefs = []
    for b0 in range(0, n, block):
        b1 = min(n, b0 + block)
        h0 = max(0, b0 - order)
        seg = x[h0:b1]
        if len(seg) <= order * 2:
            coefs.append(np.zeros(order))
            continue
        a = ar_coeffs(seg, order)
        coefs.append(a)
        e = ar_residual(seg, a)[b0 - h0 :]
        sig = 1.4826 * np.median(np.abs(e - np.median(e))) + EPS
        flags[b0:b1] = np.abs(e) > k * sig
    idx = np.flatnonzero(flags)
    regions = []
    if idx.size:
        starts = [idx[0]]
        ends = []
        for i0, i1 in zip(idx[:-1], idx[1:]):
            if i1 - i0 > merge_gap:
                ends.append(i0)
                starts.append(i1)
        ends.append(idx[-1])
        for s, e in zip(starts, ends):
            regions.append((max(0, s - pre), min(n, e + post + 1)))
    return regions, coefs, block


def declick(x: np.ndarray, sr: int, order: int, k: float, max_ms: float, block: int = 4096):
    """Detect clicks and repair them with LSAR interpolation.

    Regions longer than max_ms are left untouched (logged) rather than risk
    replacing real music with a long synthetic guess.
    """
    regions, coefs, block = detect_impulses(x, sr, order, k, block)
    y = x.copy()
    max_len = int(max_ms * 1e-3 * sr)
    repaired, skipped, samples = 0, 0, 0
    ctx = max(order * 2, 64)
    for s, e in regions:
        L = e - s
        if L > max_len:
            skipped += 1
            continue
        a = coefs[min(s // block, len(coefs) - 1)]
        c0, c1 = max(0, s - ctx), min(len(y), e + ctx)
        if (s - c0) < order or (c1 - e) < order:
            skipped += 1
            continue
        seg = y[c0:c1]
        miss = np.zeros(len(seg), dtype=bool)
        miss[s - c0 : e - c0] = True
        y[c0:c1] = lsar_interpolate(seg, miss, a)
        repaired += 1
        samples += L
    stats = {"detected": len(regions), "repaired": repaired, "skipped_too_long": skipped,
             "samples_replaced": int(samples), "percent_samples_replaced": round(100.0 * samples / len(x), 4)}
    return y, stats, regions


# --------------------------------------------------------------------------- #
# Spectral noise reduction
# --------------------------------------------------------------------------- #
def stft(x, sr, n_fft=2048, hop=512):
    f, t, Z = signal.stft(x, fs=sr, window="hann", nperseg=n_fft, noverlap=n_fft - hop, boundary="even", padded=True)
    return f, t, Z


def istft(Z, sr, n, n_fft=2048, hop=512):
    _, y = signal.istft(Z, fs=sr, window="hann", nperseg=n_fft, noverlap=n_fft - hop, boundary=True)
    return y[:n]


def noise_profile(x: np.ndarray, sr: int, lead_in_s: float, n_fft=2048, hop=512, percentile=10.0):
    """Estimate surface-noise power spectrum.

    Preferred: the lead-in groove before the music starts (pure surface noise).
    Fallback: per-bin low percentile over the whole recording (minimum statistics),
    scaled up to compensate for the downward bias of a low percentile.
    """
    f, t, Z = stft(x, sr, n_fft, hop)
    P = np.abs(Z) ** 2
    nfr = int(lead_in_s * sr / hop)
    if nfr >= int(0.5 * sr / hop):
        prof = P[:, 2 : max(3, nfr - 2)].mean(axis=1)
        method = f"lead-in groove ({lead_in_s:.2f} s)"
    else:
        prof = np.percentile(P, percentile, axis=1) * 2.0
        method = f"minimum statistics ({percentile:.0f}th percentile x2)"
    return f, prof, method


def spectral_denoise(x: np.ndarray, sr: int, noise_psd: np.ndarray, over_sub: float, gain_floor_db: float,
                     dd_alpha: float = 0.96, freq_smooth: int = 3, n_fft=2048, hop=512):
    """Decision-directed Wiener filter (Ephraim & Malah 1984 a-priori SNR rule).

    over_sub      : multiplies the noise PSD (more = stronger reduction)
    gain_floor_db : lowest gain applied to any bin; keeps a little natural
                    surface noise and prevents 'musical noise' artefacts.
    """
    f, t, Z = stft(x, sr, n_fft, hop)
    P = np.abs(Z) ** 2
    N = noise_psd[:, None] * over_sub + EPS
    gamma = P / N
    gmin = 10 ** (gain_floor_db / 20)
    G = np.empty_like(P)
    prev = np.ones(P.shape[0])
    prev_gamma = np.ones(P.shape[0])
    for j in range(P.shape[1]):
        xi = dd_alpha * (prev ** 2) * prev_gamma + (1 - dd_alpha) * np.maximum(gamma[:, j] - 1, 0)
        g = xi / (1 + xi)
        if freq_smooth > 1:
            g = np.convolve(g, np.ones(freq_smooth) / freq_smooth, mode="same")
        g = np.maximum(g, gmin)
        G[:, j] = g
        prev, prev_gamma = g, gamma[:, j]
    y = istft(Z * G, sr, len(x), n_fft, hop)
    return y, float(np.mean(20 * np.log10(G + EPS)))


# --------------------------------------------------------------------------- #
# Adaptive EQ (resonance flattening within the recorded passband)
# --------------------------------------------------------------------------- #
def octave_smooth(f: np.ndarray, db: np.ndarray, frac: float = 3.0) -> np.ndarray:
    out = np.empty_like(db)
    for i, fc in enumerate(f):
        if fc <= 0:
            out[i] = db[i]
            continue
        lo, hi = fc * 2 ** (-0.5 / frac), fc * 2 ** (0.5 / frac)
        m = (f >= lo) & (f <= hi)
        out[i] = db[m].mean()
    return out


def adaptive_eq(x: np.ndarray, sr: int, f_lo: float, f_hi: float, strength: float, max_db: float,
                tilt_db_per_oct: float = 0.0, max_boost_db: float = 2.5, numtaps: int = 2047):
    """Flatten horn/diaphragm resonances inside [f_lo, f_hi].

    The long-term spectrum is 1/3-octave smoothed and compared with a straight
    line fitted in log-frequency (the recording's own overall tilt). A fraction
    `strength` of the deviation is removed: cuts are bounded to max_db, boosts
    to max_boost_db (resonance peaks are cut more readily than dips are filled).
    The correction fades to 0 dB at the band edges and is never positive
    outside the band, so noise-only regions are never boosted. Linear-phase FIR, so no phase distortion.
    """
    f, pxx = signal.welch(x, fs=sr, nperseg=8192)
    db = 10 * np.log10(pxx + EPS)
    sm = octave_smooth(f, db, 3.0)
    band = (f >= f_lo) & (f <= f_hi)
    lf = np.log2(np.maximum(f, 1.0))
    k, c = np.polyfit(lf[band], sm[band], 1)
    trend = k * lf + c
    corr = np.zeros_like(f)
    corr[band] = np.clip(-strength * (sm[band] - trend[band]), -max_db, max_boost_db)
    if tilt_db_per_oct:
        ref = np.log2(np.sqrt(f_lo * f_hi))
        corr[band] += np.clip(tilt_db_per_oct * (lf[band] - ref), -max_db, max_boost_db)
    # fade the correction to 0 dB over the outer 1/3 octave *inside* the band,
    # so nothing outside [f_lo, f_hi] (noise-dominated) is ever boosted
    edge = np.clip(np.minimum(np.log2(np.maximum(f, 1) / f_lo), np.log2(f_hi / np.maximum(f, 1))) / (1 / 3), 0, 1)
    corr = corr * edge
    corr = octave_smooth(f, corr, 6.0)
    corr[~band] = np.minimum(corr[~band], 0.0)
    gains = 10 ** (corr / 20)
    fir = signal.firwin2(numtaps, f / (sr / 2), gains, fs=2.0)
    y = signal.fftconvolve(x, fir, mode="same")
    return y, f, corr


# --------------------------------------------------------------------------- #
# Speed / wow correction
# --------------------------------------------------------------------------- #
def change_speed(x: np.ndarray, ratio: float) -> np.ndarray:
    """Constant speed correction by resampling (ratio > 1 = faster/higher)."""
    from fractions import Fraction
    fr = Fraction(1 / ratio).limit_denominator(2000)
    return signal.resample_poly(x, fr.numerator, fr.denominator)


def variable_speed(x: np.ndarray, sr: int, times: np.ndarray, cents: np.ndarray) -> np.ndarray:
    """Time-varying resampling that removes a measured pitch-drift curve (wow)."""
    rate = 2 ** (-np.interp(np.arange(len(x)) / sr, times, cents) / 1200.0)
    pos = np.cumsum(rate)
    pos -= pos[0]
    keep = pos <= len(x) - 1
    return np.interp(pos[keep], np.arange(len(x)), x)
