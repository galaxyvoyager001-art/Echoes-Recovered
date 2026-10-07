# Restoration log - Torna a Surriento

* **Performer:** Bianca, Lia  ·  **Recorded:** 1910-03-25, Buenos Aires
* **LoC item:** https://www.loc.gov/item/jukebox-192569/  ·  **Disc:** Victor 62914  ·  **Matrix/take:** R-683 (Matrix ID) / [1]
* **Source file:** `data/originals/jukebox-192569_torna-a-surriento/loc_original.wav` (SHA-256 `3805fc0d8aefcda3...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -36.0 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -26.4 dBFS -> SNR ~9.6 dB
* Clicks/crackle: 843.4 impulses/min, median length 0.23 ms, 1 longer than 2 ms
* Hiss: 5-10 kHz band sits -7.7 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~237-1637 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -5.45, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -38.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.82}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 843 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 9.6 dB -> noise over-subtraction x1.3, gain floor -10.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 1637 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2500 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=2505, repaired=2505, skipped_too_long=0, samples_replaced=26885, percent_samples_replaced=0.3411
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.0, max_ms=1.0, detected=8060, repaired=8058, skipped_too_long=2, samples_replaced=83942, percent_samples_replaced=1.0649
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-10.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-7.71
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2500.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-4.0, 2.5]
8. **level match** - original_lufs=-28.5, restored_lufs=-28.5, gain_db=4.11, limiter=False
9. **timing** - seconds=41.7

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -36.0 | -45.5 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -36.0 | -45.2 |
| Programme (p90) minus surface noise (dB) | 9.6 | 19.9 |
| Impulses per minute (AR detector, k=8) | 843.4 | 16.2 |
| Impulses longer than 2 ms | 1 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -7.7 | -33.7 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -35.7, 'removed_vs_original_energy_300_3000hz_db': -18.3, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.41% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
