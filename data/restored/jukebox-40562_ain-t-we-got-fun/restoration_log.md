# Restoration log - Ain't we got fun

* **Performer:** Benson Orchestra of Chicago  ·  **Recorded:** 1921-04-11, Chicago
* **LoC item:** https://www.loc.gov/item/jukebox-40562/  ·  **Disc:** Victor 18757  ·  **Matrix/take:** B-25150 (Matrix ID) / 4
* **Source file:** `data/originals/jukebox-40562_ain-t-we-got-fun/loc_original.wav` (SHA-256 `2cbe1513668006e6...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -33.1 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -16.5 dBFS -> SNR ~16.6 dB
* Clicks/crackle: 2085.6 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -25.6 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~129-3467 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.35, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -5.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 4.0, 'distinct_peak': True, 'voiced_fraction': 0.39}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 2086 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 16.6 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3467 Hz -> hiss low-pass at 5547 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3467 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=10030, repaired=10030, skipped_too_long=0, samples_replaced=111573, percent_samples_replaced=1.3178
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.0, max_ms=1.0, detected=8794, repaired=8794, skipped_too_long=0, samples_replaced=91383, percent_samples_replaced=1.0793
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.27
6. **hiss low-pass** - fc_hz=5547, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3467.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.88, 1.96]
8. **level match** - original_lufs=-20.41, restored_lufs=-20.41, gain_db=0.66, limiter=False
9. **timing** - seconds=46.5

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -33.1 | -38.1 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -32.9 | -37.5 |
| Programme (p90) minus surface noise (dB) | 16.6 | 21.9 |
| Impulses per minute (AR detector, k=8) | 2085.6 | 409.7 |
| Impulses longer than 2 ms | 0 | 3 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -25.6 | -42.8 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -37.4, 'removed_vs_original_energy_300_3000hz_db': -20.5, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.40% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
