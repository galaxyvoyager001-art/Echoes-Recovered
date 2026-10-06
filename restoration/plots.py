"""Before/after figures: waveform, spectrogram, long-term spectrum + EQ curve."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy import signal

ORIG = "#8a8984"      # original: recessive neutral
REST = "#2a78d6"      # restored: categorical slot 1
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SEQ = LinearSegmentedColormap.from_list("seq_blue", ["#fcfcfb", "#b9d3f2", "#2a78d6", "#0d2f5c"])

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.titlecolor": INK, "axes.titlesize": 10, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
})


def _envelope(x, sr, n=3000):
    hop = max(1, len(x) // n)
    m = len(x) // hop
    fr = x[: m * hop].reshape(m, hop)
    t = np.arange(m) * hop / sr
    return t, fr.min(axis=1), fr.max(axis=1)


def waveform(x, y, sr, regions, title, path):
    fig, ax = plt.subplots(3, 1, figsize=(10, 6.4), constrained_layout=True)
    for a, sig, col, lab in ((ax[0], x, ORIG, "Original (LoC transfer)"), (ax[1], y, REST, "Restored")):
        t, lo, hi = _envelope(sig, sr)
        a.fill_between(t, lo, hi, color=col, linewidth=0)
        a.set_ylim(-1, 1)
        a.set_xlim(0, len(x) / sr)
        a.set_title(lab, loc="left")
        a.set_ylabel("amplitude")
    ax[1].set_xlabel("time (s)")
    # zoom on the largest repaired impulse
    if regions:
        s, e = max(regions, key=lambda r: np.max(np.abs(x[r[0]:r[1]])) if r[1] > r[0] else 0)
        c = (s + e) // 2
        w = int(0.02 * sr)
        i0, i1 = max(0, c - w), min(len(x), c + w)
        tt = (np.arange(i0, i1) - c) / sr * 1000
        ax[2].plot(tt, x[i0:i1], color=ORIG, lw=1.4, label="Original")
        ax[2].plot(tt, y[i0:i1], color=REST, lw=1.4, label="Restored")
        ax[2].axvspan((s - c) / sr * 1000, (e - c) / sr * 1000, color=GRID, zorder=0)
        ax[2].set_title(f"Zoom: largest repaired click at {c / sr:.2f} s (shaded = interpolated samples)", loc="left")
        ax[2].set_xlabel("ms around click")
        ax[2].legend(frameon=False, loc="upper right")
    fig.suptitle(title, x=0.01, ha="left", color=INK, fontsize=11)
    fig.savefig(path, dpi=100)
    plt.close(fig)


def spectrogram(x, y, sr, title, path, fmax=8000):
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True, sharex=True)
    specs = []
    for sig in (x, y):
        hop = max(1024, int(len(sig) / 1400))
        f, t, Z = signal.stft(sig, fs=sr, nperseg=2048, noverlap=max(0, 2048 - hop) if hop < 2048 else 0)
        S = 20 * np.log10(np.abs(Z) + 1e-9)
        specs.append((f, t, S))
    vmax = max(np.percentile(s[2], 99.5) for s in specs)
    vmin = vmax - 70
    for a, (f, t, S), lab in zip(ax, specs, ("Original (LoC transfer)", "Restored")):
        m = f <= fmax
        im = a.pcolormesh(t, f[m], S[m], cmap=SEQ, vmin=vmin, vmax=vmax, shading="auto", rasterized=True)
        a.set_ylabel("frequency (Hz)")
        a.set_title(lab, loc="left")
        a.grid(False)
    ax[1].set_xlabel("time (s)")
    fig.colorbar(im, ax=ax, label="level (dB, shared scale)", shrink=0.8)
    fig.suptitle(title, x=0.01, ha="left", color=INK, fontsize=11)
    fig.savefig(path, dpi=100, pil_kwargs={"quality": 85})
    plt.close(fig)


def spectrum(x, y, sr, eq_curve, band, title, path):
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True, sharex=True,
                           gridspec_kw={"height_ratios": [2.2, 1]})
    for sig, col, lab in ((x, ORIG, "Original"), (y, REST, "Restored")):
        f, p = signal.welch(sig, fs=sr, nperseg=8192)
        ax[0].semilogx(f[1:], 10 * np.log10(p[1:] + 1e-14), color=col, lw=2, label=lab)
    ax[0].axvspan(*band, color=GRID, alpha=0.6, zorder=0, label="measured usable band")
    ax[0].set_ylabel("power (dB/Hz)")
    ax[0].set_title("Long-term average spectrum", loc="left")
    ax[0].legend(frameon=False, loc="lower left")
    if eq_curve is not None:
        ef, corr = eq_curve
        ax[1].semilogx(ef[1:], corr[1:], color=INK2, lw=2)
    ax[1].axhline(0, color=GRID, lw=1)
    ax[1].set_ylabel("EQ (dB)")
    ax[1].set_title("Adaptive EQ correction actually applied", loc="left")
    ax[1].set_xlabel("frequency (Hz)")
    ax[1].set_xlim(30, sr / 2)
    fig.suptitle(title, x=0.01, ha="left", color=INK, fontsize=11)
    fig.savefig(path, dpi=100)
    plt.close(fig)
