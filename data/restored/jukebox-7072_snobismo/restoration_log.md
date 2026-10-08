# Restoration log - Snobismo

* **Performer:** Orquesta Típica Fresedo  ·  **Recorded:** 1922-05-20, Buenos Aires
* **LoC item:** https://www.loc.gov/item/jukebox-7072/  ·  **Disc:** Victor 73367  ·  **Matrix/take:** BA-48 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-7072_snobismo/loc_original.wav` (SHA-256 `e53927b25f1caa79...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -33.8 dBFS (measured from lead-in groove (1.80 s)); programme p90 -14.3 dBFS -> SNR ~19.5 dB
* Clicks/crackle: 2161.7 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -21.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~172-2455 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 2}
* Tuning offset vs A440: 47.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.69}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 2162 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 19.5 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 2455 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2500 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=10366, repaired=10366, skipped_too_long=0, samples_replaced=111272, percent_samples_replaced=1.4652
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.0, max_ms=1.0, detected=9933, repaired=9933, skipped_too_long=0, samples_replaced=103513, percent_samples_replaced=1.3631
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=lead-in groove (1.80 s), stft=2048 Hann / hop 512, mean_gain_db=-12.26
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2500.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.93, 2.3]
8. **level match** - original_lufs=-18.6, restored_lufs=-19.48, gain_db=0.33, limiter=False
9. **timing** - seconds=34.7

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -33.8 | -54.3 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -30.1 | -32.2 |
| Programme (p90) minus surface noise (dB) | 19.5 | 39.2 |
| Impulses per minute (AR detector, k=8) | 2161.7 | 2.9 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -21.0 | -54.6 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -35.4, 'removed_vs_original_energy_300_3000hz_db': -24.3, 'removed_vs_original_energy_above_5khz_db': -0.0}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.83% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
