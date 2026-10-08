# Restoration log - Down hearted blues

* **Performer:** Williams, Clarence  ·  **Recorded:** 1923-02-15, New York
* **LoC item:** https://www.loc.gov/item/jukebox-670189/  ·  **Disc:** Columbia A3844  ·  **Matrix/take:** 80863 (Matrix ID) / 5
* **Source file:** `data/originals/jukebox-670189_down-hearted-blues/loc_original.wav` (SHA-256 `59c738efa9ff782f...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -33.8 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -17.6 dBFS -> SNR ~16.1 dB
* Clicks/crackle: 2421.9 impulses/min, median length 0.23 ms, 20 longer than 2 ms
* Hiss: 5-10 kHz band sits -12.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~215-2541 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 96}
* Tuning offset vs A440: 2.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 5.6, 'distinct_peak': True, 'voiced_fraction': 0.76}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 2422 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 16.1 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 2541 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2541 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=12360, repaired=12349, skipped_too_long=11, samples_replaced=147970, percent_samples_replaced=1.6178
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.0, max_ms=1.0, detected=11706, repaired=11654, skipped_too_long=52, samples_replaced=124483, percent_samples_replaced=1.361
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-7.26
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2541.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-4.0, 1.82]
8. **level match** - original_lufs=-20.79, restored_lufs=-20.79, gain_db=2.68, limiter=False
9. **timing** - seconds=44.3

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -33.8 | -41.3 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -33.5 | -38.7 |
| Programme (p90) minus surface noise (dB) | 16.1 | 24.1 |
| Impulses per minute (AR detector, k=8) | 2421.9 | 228.8 |
| Impulses longer than 2 ms | 20 | 10 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -12.0 | -36.8 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -29.9, 'removed_vs_original_energy_300_3000hz_db': -19.6, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.98% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
