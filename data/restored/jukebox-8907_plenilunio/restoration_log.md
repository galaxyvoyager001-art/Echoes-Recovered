# Restoration log - Plenilunio

* **Performer:** Cuarteto Nacional  ·  **Recorded:** 1913-11-08, Bogotá
* **LoC item:** https://www.loc.gov/item/jukebox-8907/  ·  **Disc:** Victor 65887  ·  **Matrix/take:** L-372 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-8907_plenilunio/loc_original.wav` (SHA-256 `8a264ef9b701df2e...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -39.5 dBFS (measured from lead-in groove (0.70 s)); programme p90 -25.0 dBFS -> SNR ~14.5 dB
* Clicks/crackle: 2067.6 impulses/min, median length 0.25 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -12.3 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-1658 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.0, 'samples_over_98.5pct_fullscale': 1}
* Tuning offset vs A440: 3.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 8.8, 'distinct_peak': True, 'voiced_fraction': 0.39}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 2068 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 14.5 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 1658 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2500 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=8563, repaired=8561, skipped_too_long=2, samples_replaced=103392, percent_samples_replaced=1.2354
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=11319, repaired=11311, skipped_too_long=8, samples_replaced=119796, percent_samples_replaced=1.4314
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=lead-in groove (0.70 s), stft=2048 Hann / hop 512, mean_gain_db=-8.82
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2500.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.82, 2.31]
8. **level match** - original_lufs=-27.32, restored_lufs=-27.32, gain_db=1.67, limiter=False
9. **timing** - seconds=44.4

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -39.5 | -57.8 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -36.3 | -35.7 |
| Programme (p90) minus surface noise (dB) | 14.5 | 33.6 |
| Impulses per minute (AR detector, k=8) | 2067.6 | 5.9 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -12.3 | -50.5 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -36.0, 'removed_vs_original_energy_300_3000hz_db': -18.4, 'removed_vs_original_energy_above_5khz_db': -0.0}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.67% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
