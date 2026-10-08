# Restoration log - Yes! We have no bananas

* **Performer:** Furman and Nash  ·  **Recorded:** 1923-03-31, New York
* **LoC item:** https://www.loc.gov/item/jukebox-670477/  ·  **Disc:** Columbia A3873  ·  **Matrix/take:** 80932 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-670477_yes-we-have-no-bananas/loc_original.wav` (SHA-256 `04a4451c472e72b1...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -37.2 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -15.4 dBFS -> SNR ~21.8 dB
* Clicks/crackle: 3915.1 impulses/min, median length 0.23 ms, 2 longer than 2 ms
* Hiss: 5-10 kHz band sits -18.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-4134 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 98}
* Tuning offset vs A440: 29.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 7.7, 'distinct_peak': True, 'voiced_fraction': 0.43}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 3915 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 21.8 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 4134 Hz -> hiss low-pass at 6614 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-4000 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.5, max_ms=4.0, max_percent_replaced=2.0, detected=12770, repaired=12770, skipped_too_long=0, samples_replaced=149983, percent_samples_replaced=1.9925
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.5, max_ms=1.0, detected=9077, repaired=9076, skipped_too_long=1, samples_replaced=95528, percent_samples_replaced=1.269
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.26
6. **hiss low-pass** - fc_hz=6614, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=4000.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.92, 2.5]
8. **level match** - original_lufs=-19.24, restored_lufs=-19.24, gain_db=1.77, limiter=False
9. **timing** - seconds=45.8

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -37.2 | -51.1 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -36.2 | -45.2 |
| Programme (p90) minus surface noise (dB) | 21.8 | 35.8 |
| Impulses per minute (AR detector, k=8) | 3915.1 | 572.0 |
| Impulses longer than 2 ms | 2 | 1 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -18.0 | -29.3 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -33.5, 'removed_vs_original_energy_300_3000hz_db': -22.8, 'removed_vs_original_energy_above_5khz_db': -0.3}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 3.26% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
