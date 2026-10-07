# Restoration log - Tras de las verdes colinas

* **Performer:** Wills, Alejandro  ·  **Recorded:** 1913-11-09, Bogotá
* **LoC item:** https://www.loc.gov/item/jukebox-8910/  ·  **Disc:** Victor 65892  ·  **Matrix/take:** L-375 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-8910_tras-de-las-verdes-colinas/loc_original.wav` (SHA-256 `013a4b1f5ee6d177...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -31.9 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -13.5 dBFS -> SNR ~18.4 dB
* Clicks/crackle: 878.4 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -17.3 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-1400 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.0, 'samples_over_98.5pct_fullscale': 4}
* Tuning offset vs A440: 49.0 cents; wow indicator: {'peak_freq_hz': 1.188, 'implied_rpm': 71.3, 'peak_over_neighbourhood_db': 6.2, 'distinct_peak': True, 'voiced_fraction': 0.56}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 878 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 18.4 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 1400 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2500 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=2817, repaired=2817, skipped_too_long=0, samples_replaced=29105, percent_samples_replaced=0.3417
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.0, max_ms=1.0, detected=10714, repaired=10714, skipped_too_long=0, samples_replaced=111711, percent_samples_replaced=1.3116
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.4
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2500.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.95, 2.5]
8. **level match** - original_lufs=-18.41, restored_lufs=-19.21, gain_db=0.74, limiter=False
9. **timing** - seconds=47.4

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -31.9 | -42.7 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -31.9 | -40.5 |
| Programme (p90) minus surface noise (dB) | 18.4 | 27.6 |
| Impulses per minute (AR detector, k=8) | 878.4 | 49.3 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -17.3 | -43.7 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -32.3, 'removed_vs_original_energy_300_3000hz_db': -25.3, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.65% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
