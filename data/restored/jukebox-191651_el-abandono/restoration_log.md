# Restoration log - El abandono

* **Performer:** Abreu, Tomás R.  ·  **Recorded:** 1917-01-25, Caracas
* **LoC item:** https://www.loc.gov/item/jukebox-191651/  ·  **Disc:** Victor 69636  ·  **Matrix/take:** G-1787 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-191651_el-abandono/loc_original.wav` (SHA-256 `48a66fdf59c96379...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -37.4 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -17.6 dBFS -> SNR ~19.7 dB
* Clicks/crackle: 436.5 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -22.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~22-3768 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.0, 'samples_over_98.5pct_fullscale': 1}
* Tuning offset vs A440: -6.0 cents; wow indicator: {'peak_freq_hz': 1.313, 'implied_rpm': 78.8, 'peak_over_neighbourhood_db': 6.2, 'distinct_peak': True, 'voiced_fraction': 0.79}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 436 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 19.7 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3768 Hz -> hiss low-pass at 6029 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3768 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=1365, repaired=1365, skipped_too_long=0, samples_replaced=14974, percent_samples_replaced=0.1904
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.0, max_ms=1.0, detected=7243, repaired=7243, skipped_too_long=0, samples_replaced=76840, percent_samples_replaced=0.9771
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.39
6. **hiss low-pass** - fc_hz=6029, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3768.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.85, 2.5]
8. **level match** - original_lufs=-20.27, restored_lufs=-20.61, gain_db=1.5, limiter=False
9. **timing** - seconds=30.3

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -37.4 | -42.7 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -36.8 | -39.9 |
| Programme (p90) minus surface noise (dB) | 19.7 | 24.8 |
| Impulses per minute (AR detector, k=8) | 436.5 | 52.9 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -22.0 | -37.0 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -38.4, 'removed_vs_original_energy_300_3000hz_db': -26.3, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.17% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
