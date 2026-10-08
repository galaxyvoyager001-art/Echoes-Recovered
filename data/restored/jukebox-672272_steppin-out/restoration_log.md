# Restoration log - Steppin' out

* **Performer:** Ted Lewis Jazz Band  ·  **Recorded:** 1923-12-04, Chicago
* **LoC item:** https://www.loc.gov/item/jukebox-672272/  ·  **Disc:** Columbia 48D  ·  **Matrix/take:** 81382 (Matrix ID) / 3
* **Source file:** `data/originals/jukebox-672272_steppin-out/loc_original.wav` (SHA-256 `11d4edabb35cd571...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -44.7 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -28.1 dBFS -> SNR ~16.6 dB
* Clicks/crackle: 1388.0 impulses/min, median length 0.23 ms, 1 longer than 2 ms
* Hiss: 5-10 kHz band sits -30.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~215-2864 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -8.43, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -20.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.47}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 1388 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 16.6 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 2864 Hz -> hiss low-pass at 4582 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2864 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=4464, repaired=4459, skipped_too_long=5, samples_replaced=56746, percent_samples_replaced=0.6854
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.0, max_ms=1.0, detected=10755, repaired=10732, skipped_too_long=23, samples_replaced=119067, percent_samples_replaced=1.438
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-9.83
6. **hiss low-pass** - fc_hz=4582, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2864.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.84, 2.19]
8. **level match** - original_lufs=-31.71, restored_lufs=-31.71, gain_db=1.11, limiter=False
9. **timing** - seconds=25.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -44.7 | -47.5 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -43.9 | -45.9 |
| Programme (p90) minus surface noise (dB) | 16.6 | 19.6 |
| Impulses per minute (AR detector, k=8) | 1388.0 | 93.7 |
| Impulses longer than 2 ms | 1 | 1 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -30.0 | -55.7 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -50.2, 'removed_vs_original_energy_300_3000hz_db': -22.9, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.12% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
