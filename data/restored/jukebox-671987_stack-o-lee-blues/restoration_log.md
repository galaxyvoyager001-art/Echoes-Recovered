# Restoration log - Stack o' Lee blues

* **Performer:** Frank Westphal Orchestra  ·  **Recorded:** 1923-10-18, Chicago
* **LoC item:** https://www.loc.gov/item/jukebox-671987/  ·  **Disc:** Columbia 32D  ·  **Matrix/take:** 81315 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-671987_stack-o-lee-blues/loc_original.wav` (SHA-256 `5ab3e86dd199f2f2...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -39.5 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -25.3 dBFS -> SNR ~14.2 dB
* Clicks/crackle: 3348.4 impulses/min, median length 0.23 ms, 2 longer than 2 ms
* Hiss: 5-10 kHz band sits -16.8 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~215-3295 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -2.43, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 14.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 5.6, 'distinct_peak': True, 'voiced_fraction': 0.48}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 3348 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 14.2 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3295 Hz -> hiss low-pass at 5272 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3295 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.5, max_ms=4.0, max_percent_replaced=2.0, detected=11992, repaired=11992, skipped_too_long=0, samples_replaced=139821, percent_samples_replaced=1.7735
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.5, max_ms=1.0, detected=9971, repaired=9971, skipped_too_long=0, samples_replaced=105856, percent_samples_replaced=1.3427
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-7.7
6. **hiss low-pass** - fc_hz=5272, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3295.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.39, 2.27]
8. **level match** - original_lufs=-27.77, restored_lufs=-27.77, gain_db=1.59, limiter=False
9. **timing** - seconds=52.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -39.5 | -42.3 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -38.6 | -40.9 |
| Programme (p90) minus surface noise (dB) | 14.2 | 17.4 |
| Impulses per minute (AR detector, k=8) | 3348.4 | 365.9 |
| Impulses longer than 2 ms | 2 | 1 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -16.8 | -33.1 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -42.3, 'removed_vs_original_energy_300_3000hz_db': -18.8, 'removed_vs_original_energy_above_5khz_db': -0.4}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 3.12% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
