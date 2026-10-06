# Restoration log - The Memphis blues

* **Performer:** Harvey, Morton  ·  **Recorded:** 1914-10-02, Camden
* **LoC item:** https://www.loc.gov/item/jukebox-11226/  ·  **Disc:** Victor 17657  ·  **Matrix/take:** B-15244 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-11226_the-memphis-blues/loc_original.wav` (SHA-256 `200274cbc78297b3...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -32.2 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -14.3 dBFS -> SNR ~17.9 dB
* Clicks/crackle: 1351.2 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -23.6 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-3424 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 11}
* Tuning offset vs A440: 28.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.58}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 1351 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 17.9 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3424 Hz -> hiss low-pass at 5478 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3424 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=3681, repaired=3681, skipped_too_long=0, samples_replaced=44340, percent_samples_replaced=0.626
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=8895, repaired=8894, skipped_too_long=1, samples_replaced=95711, percent_samples_replaced=1.3513
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.05
6. **hiss low-pass** - fc_hz=5478, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3424.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.14, 2.46]
8. **level match** - original_lufs=-16.96, restored_lufs=-19.45, gain_db=-1.08, limiter=False
9. **timing** - seconds=31.9

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -32.2 | -38.1 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -31.4 | -36.3 |
| Programme (p90) minus surface noise (dB) | 17.9 | 21.4 |
| Impulses per minute (AR detector, k=8) | 1351.2 | 170.6 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -23.6 | -40.2 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -35.2, 'removed_vs_original_energy_300_3000hz_db': -23.0, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.98% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
