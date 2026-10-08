# Restoration log - Wreck of the Old 97

* **Performer:** Dalhart, Vernon  ·  **Recorded:** 1924-08-13, New York
* **LoC item:** https://www.loc.gov/item/jukebox-70956/  ·  **Disc:** Victor 19427  ·  **Matrix/take:** B-30632 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-70956_wreck-of-the-old-97/loc_original.wav` (SHA-256 `d994b48ce11b6fe6...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -53.3 dBFS (measured from lead-in groove (0.70 s)); programme p90 -33.2 dBFS -> SNR ~20.0 dB
* Clicks/crackle: 465.1 impulses/min, median length 0.23 ms, 2 longer than 2 ms
* Hiss: 5-10 kHz band sits -19.9 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-3467 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -5.14, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -27.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 5.8, 'distinct_peak': True, 'voiced_fraction': 0.59}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 465 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 20.0 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3467 Hz -> hiss low-pass at 5547 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3467 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=1444, repaired=1444, skipped_too_long=0, samples_replaced=18475, percent_samples_replaced=0.2238
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.0, max_ms=1.0, detected=11001, repaired=10995, skipped_too_long=6, samples_replaced=117580, percent_samples_replaced=1.4243
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (0.70 s), stft=2048 Hann / hop 512, mean_gain_db=-13.78
6. **hiss low-pass** - fc_hz=5547, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3467.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-1.83, 2.42]
8. **level match** - original_lufs=-36.02, restored_lufs=-36.02, gain_db=1.22, limiter=False
9. **timing** - seconds=21.2

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -53.3 | -70.9 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -47.8 | -50.1 |
| Programme (p90) minus surface noise (dB) | 20.0 | 37.8 |
| Impulses per minute (AR detector, k=8) | 465.1 | 56.9 |
| Impulses longer than 2 ms | 2 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -19.9 | -44.1 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -51.1, 'removed_vs_original_energy_300_3000hz_db': -18.2, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.65% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
