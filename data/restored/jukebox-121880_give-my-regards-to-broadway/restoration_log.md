# Restoration log - Give my regards to Broadway

* **Performer:** Kernell, Frank [i.e., Samuel H. Dudley]  ·  **Recorded:** 1905-06-21, Philadelphia
* **LoC item:** https://www.loc.gov/item/jukebox-121880/  ·  **Disc:** Victor 4385  ·  **Matrix/take:** B-2654 (Matrix ID) / 3
* **Source file:** `data/originals/jukebox-121880_give-my-regards-to-broadway/loc_original.wav` (SHA-256 `085178030f1e58ef...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -39.5 dBFS (measured from lead-in groove (1.00 s)); programme p90 -20.1 dBFS -> SNR ~19.4 dB
* Clicks/crackle: 162.5 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -22.3 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-3079 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -6.16, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 16.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.75}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 162 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.5 sigma.
* Estimated SNR 19.4 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3079 Hz -> hiss low-pass at 4926 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3079 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=432, repaired=432, skipped_too_long=0, samples_replaced=4807, percent_samples_replaced=0.069
4. **decrackle (pass 2)** - order=24, k_requested=5.5, k_used=5.5, max_ms=1.0, detected=1542, repaired=1542, skipped_too_long=0, samples_replaced=16098, percent_samples_replaced=0.231
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=lead-in groove (1.00 s), stft=2048 Hann / hop 512, mean_gain_db=-12.0
6. **hiss low-pass** - fc_hz=4926, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3079.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.68, 1.64]
8. **level match** - original_lufs=-23.94, restored_lufs=-23.94, gain_db=1.53, limiter=False
9. **timing** - seconds=23.8

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -39.5 | -59.3 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -36.8 | -38.3 |
| Programme (p90) minus surface noise (dB) | 19.4 | 39.1 |
| Impulses per minute (AR detector, k=8) | 162.5 | 55.5 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -22.3 | -50.9 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -39.3, 'removed_vs_original_energy_300_3000hz_db': -26.6, 'removed_vs_original_energy_above_5khz_db': -0.0}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 0.30% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
