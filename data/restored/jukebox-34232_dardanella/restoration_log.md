# Restoration log - Dardanella

* **Performer:** Selvin's Novelty Orchestra  ·  **Recorded:** 1919-11-20, New York
* **LoC item:** https://www.loc.gov/item/jukebox-34232/  ·  **Disc:** Victor 18633  ·  **Matrix/take:** B-23344 (Matrix ID) / 3
* **Source file:** `data/originals/jukebox-34232_dardanella/loc_original.wav` (SHA-256 `eb872d1783d33df8...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -26.8 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -14.1 dBFS -> SNR ~12.7 dB
* Clicks/crackle: 790.7 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -25.9 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-2799 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 18}
* Tuning offset vs A440: -45.0 cents; wow indicator: {'peak_freq_hz': 1.313, 'implied_rpm': 78.8, 'peak_over_neighbourhood_db': 6.3, 'distinct_peak': True, 'voiced_fraction': 0.39}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 791 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 12.7 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 2799 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2799 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=2549, repaired=2549, skipped_too_long=0, samples_replaced=28193, percent_samples_replaced=0.3258
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=8072, repaired=8070, skipped_too_long=2, samples_replaced=84659, percent_samples_replaced=0.9782
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.32
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2799.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.98, 2.5]
8. **level match** - original_lufs=-17.31, restored_lufs=-19.43, gain_db=-0.66, limiter=False
9. **timing** - seconds=39.3

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -26.8 | -30.8 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -26.2 | -29.9 |
| Programme (p90) minus surface noise (dB) | 12.7 | 14.8 |
| Impulses per minute (AR detector, k=8) | 790.7 | 44.4 |
| Impulses longer than 2 ms | 0 | 1 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -25.9 | -51.9 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -35.1, 'removed_vs_original_energy_300_3000hz_db': -21.4, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.30% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
