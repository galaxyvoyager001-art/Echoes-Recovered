# Restoration log - When my sugar walks down the street

* **Performer:** Warner's Seven Aces  ·  **Recorded:** 1925-01-28, Atlanta
* **LoC item:** https://www.loc.gov/item/jukebox-675275/  ·  **Disc:** Columbia 305D  ·  **Matrix/take:** 140286 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-675275_when-my-sugar-walks-down-the-street/loc_original.wav` (SHA-256 `e50c6e36d400b1f9...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -39.2 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -26.5 dBFS -> SNR ~12.7 dB
* Clicks/crackle: 5478.8 impulses/min, median length 0.25 ms, 6 longer than 2 ms
* Hiss: 5-10 kHz band sits -9.3 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-6632 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.0, 'samples_over_98.5pct_fullscale': 4}
* Tuning offset vs A440: 4.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.28}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 5479 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 12.7 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 6632 Hz -> hiss low-pass at 8000 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-4000 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=10.0, max_ms=4.0, max_percent_replaced=2.0, detected=12188, repaired=12188, skipped_too_long=0, samples_replaced=167896, percent_samples_replaced=2.109
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=8.0, max_ms=1.0, detected=13534, repaired=13531, skipped_too_long=3, samples_replaced=149280, percent_samples_replaced=1.8752
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-7.68
6. **hiss low-pass** - fc_hz=8000, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=4000.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.84, 1.99]
8. **level match** - original_lufs=-29.24, restored_lufs=-29.24, gain_db=2.85, limiter=False
9. **timing** - seconds=101.3

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -39.2 | -45.7 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -38.9 | -44.4 |
| Programme (p90) minus surface noise (dB) | 12.7 | 20.5 |
| Impulses per minute (AR detector, k=8) | 5478.8 | 755.6 |
| Impulses longer than 2 ms | 6 | 1 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -9.3 | -19.1 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -36.8, 'removed_vs_original_energy_300_3000hz_db': -12.6, 'removed_vs_original_energy_above_5khz_db': -0.5}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 3.98% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
