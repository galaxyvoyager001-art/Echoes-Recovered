# Restoration log - Amar, eso es todo

* **Performer:** Montaner, Rita  ·  **Recorded:** 1923-03-15, Havana
* **LoC item:** https://www.loc.gov/item/jukebox-8045/  ·  **Disc:** Victor 73879  ·  **Matrix/take:** G-2955 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-8045_amar-eso-es-todo/loc_original.wav` (SHA-256 `4c738bde70b182ad...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -39.9 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -17.5 dBFS -> SNR ~22.4 dB
* Clicks/crackle: 682.6 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -21.8 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~172-3402 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.0, 'samples_over_98.5pct_fullscale': 2}
* Tuning offset vs A440: -16.0 cents; wow indicator: {'peak_freq_hz': 1.125, 'implied_rpm': 67.5, 'peak_over_neighbourhood_db': 5.3, 'distinct_peak': True, 'voiced_fraction': 0.46}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 683 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 22.4 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3402 Hz -> hiss low-pass at 5443 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3402 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=1864, repaired=1864, skipped_too_long=0, samples_replaced=21033, percent_samples_replaced=0.2997
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.0, max_ms=1.0, detected=6150, repaired=6149, skipped_too_long=1, samples_replaced=65007, percent_samples_replaced=0.9262
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.27
6. **hiss low-pass** - fc_hz=5443, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3402.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.63, 2.5]
8. **level match** - original_lufs=-20.37, restored_lufs=-20.61, gain_db=1.22, limiter=False
9. **timing** - seconds=18.8

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -39.9 | -55.0 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -39.0 | -49.6 |
| Programme (p90) minus surface noise (dB) | 22.4 | 37.4 |
| Impulses per minute (AR detector, k=8) | 682.6 | 21.1 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -21.8 | -39.1 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -38.5, 'removed_vs_original_energy_300_3000hz_db': -28.2, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.23% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
