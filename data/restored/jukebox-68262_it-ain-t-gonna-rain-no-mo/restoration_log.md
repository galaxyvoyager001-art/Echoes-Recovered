# Restoration log - It ain't gonna rain no mo'

* **Performer:** Hall, Wendell W.  ·  **Recorded:** 1923-10-12, New York
* **LoC item:** https://www.loc.gov/item/jukebox-68262/  ·  **Disc:** Victor 19171  ·  **Matrix/take:** B-28741 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-68262_it-ain-t-gonna-rain-no-mo/loc_original.wav` (SHA-256 `6a52897da0a54937...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -41.0 dBFS (measured from lead-in groove (2.20 s)); programme p90 -20.9 dBFS -> SNR ~20.1 dB
* Clicks/crackle: 3097.5 impulses/min, median length 0.23 ms, 1 longer than 2 ms
* Hiss: 5-10 kHz band sits -19.7 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~237-3725 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -3.75, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 17.0 cents; wow indicator: {'peak_freq_hz': 1.5, 'implied_rpm': 90.0, 'peak_over_neighbourhood_db': 4.2, 'distinct_peak': True, 'voiced_fraction': 0.4}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 3098 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 20.1 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3725 Hz -> hiss low-pass at 5960 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3725 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.5, max_ms=4.0, max_percent_replaced=2.0, detected=11670, repaired=11670, skipped_too_long=0, samples_replaced=141750, percent_samples_replaced=1.666
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.5, max_ms=1.0, detected=8458, repaired=8458, skipped_too_long=0, samples_replaced=90858, percent_samples_replaced=1.0679
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (2.20 s), stft=2048 Hann / hop 512, mean_gain_db=-13.66
6. **hiss low-pass** - fc_hz=5960, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3725.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.26, 2.5]
8. **level match** - original_lufs=-24.03, restored_lufs=-24.03, gain_db=1.43, limiter=False
9. **timing** - seconds=52.6

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -41.0 | -47.9 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -38.8 | -44.0 |
| Programme (p90) minus surface noise (dB) | 20.1 | 27.0 |
| Impulses per minute (AR detector, k=8) | 3097.5 | 336.3 |
| Impulses longer than 2 ms | 1 | 2 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -19.7 | -35.7 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -38.7, 'removed_vs_original_energy_300_3000hz_db': -16.3, 'removed_vs_original_energy_above_5khz_db': -0.3}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.73% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
