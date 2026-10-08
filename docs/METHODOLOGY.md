# Restoration methodology

This document describes exactly what `restoration/` does. The code is the authoritative reference. Every recording's `data/restored/<slug>/params.json` records the parameters that were actually used.

## Principles
1. **The original is never modified.** LoC WAV masters are read-only inputs. They are preserved bit-exact (SHA-256 recorded; FLAC copies verified by PCM MD5).
2. **Nothing is invented.** No generative or machine-learning model is used. The only stage that writes new sample values is click interpolation, and it computes them from the neighbouring real samples (least-squares AR interpolation, gaps of at most 4 ms). The share of interpolated samples is logged for every track.
3. **Measure first, then choose parameters.** Every track is analysed, and its parameters are derived from that analysis (`pipeline.auto_params`). Manual overrides are possible through `config/overrides.json` and would be logged; this run used none.
4. **Prefer leaving noise over creating artefacts.** Noise-reduction gain is floored (-10 to -15 dB), and worn, low-SNR discs get *gentler* settings.
5. **Show the work.** Each track has before/after plots, an A/B file, and the exact signal that was removed.

## Damage analysis (`restoration/analysis.py`)
| Damage | How it is measured |
|---|---|
| Surface noise / hiss | RMS of the lead-in groove when the first 0.5 s is at least 10 dB below the music; otherwise the 5th-percentile 50 ms frame level. A second measure, the noise floor *during* the music (5th percentile of frames between music start and end), is also reported. |
| Clicks, pops, crackle | Impulses detected by the AR prediction-error detector (order 24, threshold 8 × robust σ, block 4096). Reported as impulses per minute and as the count of impulses longer than 2 ms. |
| Frequency loss (band limits) | Per STFT bin, the ratio median/10th-percentile power. Stationary noise gives about 8.2 dB; music raises it. The usable band is where the 1/3-octave-smoothed ratio exceeds the 8–16 kHz (noise-only) plateau by 0.5 dB. |
| Hiss above the band | 5–10 kHz energy relative to 300–3000 Hz. |
| Hum | Prominence of 50/60 Hz and harmonics over ±3–15 Hz neighbours (> 10 dB flags hum). |
| Distortion / clipping | Peak level and the count of samples at or above 98.5 % of full scale. Groove distortion from the original cutting cannot be undone, and none was attempted. |
| Speed / pitch | Tuning offset against A440 (librosa chroma estimate). Reported, **not** auto-corrected: period pitch standards (A = 435–440 Hz and others) make the offset ambiguous. |
| Wow (speed instability) | pYIN f0 track → deviation from a 2 s running median → spectrum. A distinct local peak in 1.0–1.6 Hz (60–96 rpm rotation) indicates eccentricity or wow. Reported, **not** auto-corrected, because melody and vibrato make automatic correction unsafe. |

## Processing chain (`restoration/pipeline.py`, `restoration/dsp.py`)
1. **Mono fold.** The LoC transfers are dual-mono (L/R correlation ≥ 0.9999 on the stereo files; some files are mono). The channels are averaged.
2. **Speed correction.** Supported (`change_speed`, `variable_speed`) but applied only through an override. None was applied in this run.
3. **High-pass at 50 Hz** (4th-order Butterworth, zero-phase). Removes rumble and DC. The acoustic horn captured almost nothing this low. Hum notches (Q = 30) are added only where a 50/60 Hz peak is detected. One track was flagged: *Tiger Rag* has a 50 Hz peak 11.8 dB above its neighbours, which was notched. That disc was recorded and transferred in the US (60 Hz mains), so the peak is more likely a musical tone than mains hum; it sits at the 50 Hz high-pass corner, so the notch has little audible effect.
4. **Declick, pass 1.** AR(32) prediction error per 4096-sample block, threshold k·σ (σ = 1.4826·MAD; k = 7 or 8 depending on the measured impulse rate). Detections within 12 samples are merged and padded by 3 samples before and 6 after. Regions up to 4 ms are re-estimated by LSAR interpolation (Janssen, Veldhuis & Vries 1986; Godsill & Rayner 1998). If more than 2 % of samples would be replaced, k is raised in 0.5 steps.
5. **Decrackle, pass 2.** The same method with AR(24), k = 5–5.5 and a 1 ms limit; backs off automatically above 1.5 % of samples replaced.
6. **Spectral noise reduction.** STFT (2048 Hann, hop 512) with a decision-directed Wiener gain (Ephraim & Malah 1984; α = 0.96). The noise PSD comes from the lead-in groove, or from minimum statistics (10th percentile × 2). Over-subtraction is 1.2–1.3 and the gain floor −10 to −15 dB, both chosen from the measured SNR. A 3-bin frequency smoothing reduces musical noise.
7. **Hiss low-pass** at 1.6 × the measured upper band edge, clamped to 4.5–8 kHz (4th order, zero-phase).
8. **Adaptive EQ.** The long-term spectrum is smoothed to 1/3 octave and compared with a straight-line fit in log-frequency over 250 Hz–min(4 kHz, band edge). Half of the deviation is removed. Cuts are limited to 4 dB and boosts to 2.5 dB, the correction fades to 0 dB at the band edges, and it is never positive outside the band. A linear-phase FIR (2047 taps) applies it.
9. **Level match** to the original's integrated loudness (ITU-R BS.1770 via pyloudnorm), with plain gain only and a −1 dBFS peak ceiling. No limiter.
10. **Output.** 16-bit FLAC with TPDF dither, and MP3 (LAME V2) for the web.

## Verification outputs per recording
* `analysis.json`: the same metrics computed on the original and the restored file, plus statistics on the removed component (energy removed in 300–3000 Hz and above 5 kHz, relative to the original).
* `removed_component.mp3`: original minus the signal after the click, noise and filter stages (before EQ and level). If music is clearly audible here, the settings were too strong.
* `ab_compare.mp3`: three 6-second passages, each played as Original and then Restored, both at matched loudness.
* `waveform.png`, `spectrogram.jpg` (shared colour scale), `spectrum.png` (long-term spectrum and the EQ curve actually applied).

## Known limitations
* Parameters were derived from objective measurements and inspection of the plots. **No formal listening test** has been run. Listening to the A/B and "removed" files is the recommended next step, and `config/overrides.json` exists for per-track adjustments.
* The impulse-rate metric counts strong musical transients (drums, banjo plucks, brass attacks) as well as clicks. On loud dance-band records it overstates the remaining damage.
* Several LoC transfers already contain samples at or above 98.5 % of full scale. On *Swanee* (268) and *There's Ragtime in the Air* (92), all of them fall within 20 samples of a detected impulse, so they are click peaks that declicking replaces. On *Rusty Rags* that holds for 62 of 78, and on *Tiger Rag* for only 81 of 296: most of the *Tiger Rag* peaks are loud music that was clipped in the transfer or the original cutting. That clipping cannot be undone and was left as is.
* On *Cardeal* (Rio de Janeiro, voice and violão) the impulse count *rises* after restoration (153 → 291 per minute). Its spectra match below 4 kHz and the zoom plot shows the clicks removed; with the surface noise lowered, the detector's relative threshold falls and the guitar's plucked attacks now exceed it. On *Imitação d'um batuque africano* (215 → 178) and *Tiger Rag* (199 → 173) the count falls only slightly, which is consistent with strong percussive and brass attacks being counted. The same happens on *Paisano* (Guayaquil, rondador panpipe solo, 737 → 653): the breathy attacks of the panpipe are counted. The count is reported as measured.
* The usable-band estimate can be fooled by very dense crackle. On *When My Sugar Walks Down the Street* (Atlanta, January 1925; 5,479 impulses per minute) it reports 6.6 kHz, but the long-term spectrum shows the music ending near 3 kHz with flat noise above it, as expected for an acoustic recording. The hiss low-pass is clamped to 8 kHz, so no music was cut. LoC metadata does not state the recording method for any item.
* Tuning offsets of up to about ±45 cents and possible 1.0–1.6 Hz wow peaks were measured on several tracks and left uncorrected (see each `restoration_log.md`).
