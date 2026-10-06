# Restoration log - Alexander's ragtime band

* **Performer:** Collins and Harlan  ·  **Recorded:** 1911-05-23, Camden
* **LoC item:** https://www.loc.gov/item/jukebox-130333/  ·  **Disc:** Victor 16908  ·  **Matrix/take:** B-10374 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-130333_alexander-s-ragtime-band/loc_original.wav` (SHA-256 `7884320da7007b0c...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -30.7 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -14.0 dBFS -> SNR ~16.7 dB
* Clicks/crackle: 192.0 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -22.1 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~172-3575 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 3}
* Tuning offset vs A440: 44.0 cents; wow indicator: {'peak_freq_hz': 1.188, 'implied_rpm': 71.3, 'peak_over_neighbourhood_db': 5.4, 'distinct_peak': True, 'voiced_fraction': 0.51}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 192 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.5 sigma.
* Estimated SNR 16.7 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3575 Hz -> hiss low-pass at 5720 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3575 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=585, repaired=585, skipped_too_long=0, samples_replaced=6334, percent_samples_replaced=0.0782
4. **decrackle (pass 2)** - order=24, k_requested=5.5, k_used=5.5, max_ms=1.0, detected=2945, repaired=2945, skipped_too_long=0, samples_replaced=30495, percent_samples_replaced=0.3763
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.89
6. **hiss low-pass** - fc_hz=5720, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3575.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-4.0, 2.5]
8. **level match** - original_lufs=-17.41, restored_lufs=-17.64, gain_db=2.36, limiter=False
9. **timing** - seconds=27.1

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -30.7 | -34.7 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -30.3 | -33.7 |
| Programme (p90) minus surface noise (dB) | 16.7 | 20.4 |
| Impulses per minute (AR detector, k=8) | 192.0 | 79.7 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -22.1 | -36.0 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -33.6, 'removed_vs_original_energy_300_3000hz_db': -23.5, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 0.45% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
