# Restoration log - Rock all our babies to sleep

* **Performer:** Puckett, Riley  ·  **Recorded:** 1924-03-08, Atlanta
* **LoC item:** https://www.loc.gov/item/jukebox-673240/  ·  **Disc:** Columbia 107D  ·  **Matrix/take:** 81633 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-673240_rock-all-our-babies-to-sleep/loc_original.wav` (SHA-256 `e3de7f45c7bd8a58...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -54.9 dBFS (measured from lead-in groove (0.50 s)); programme p90 -25.4 dBFS -> SNR ~29.5 dB
* Clicks/crackle: 1987.7 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -18.7 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-2799 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.21, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 5.0 cents; wow indicator: {'peak_freq_hz': 1.188, 'implied_rpm': 71.3, 'peak_over_neighbourhood_db': 5.2, 'distinct_peak': True, 'voiced_fraction': 0.77}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 1988 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 29.5 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 2799 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2799 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=9369, repaired=9369, skipped_too_long=0, samples_replaced=106577, percent_samples_replaced=1.2705
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=11866, repaired=11861, skipped_too_long=5, samples_replaced=124700, percent_samples_replaced=1.4865
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (0.50 s), stft=2048 Hann / hop 512, mean_gain_db=-1.62
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2799.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.93, 2.5]
8. **level match** - original_lufs=-29.37, restored_lufs=-29.37, gain_db=1.54, limiter=False
9. **timing** - seconds=28.7

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -54.9 | -69.4 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -43.7 | -44.3 |
| Programme (p90) minus surface noise (dB) | 29.5 | 44.0 |
| Impulses per minute (AR detector, k=8) | 1987.7 | 21.8 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -18.7 | -43.3 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -44.8, 'removed_vs_original_energy_300_3000hz_db': -23.4, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.76% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
