# Restoration log - Wabash blues

* **Performer:** Bargy, Roy  ·  **Recorded:** 1921-09-29, Chicago
* **LoC item:** https://www.loc.gov/item/jukebox-42639/  ·  **Disc:** Victor 18820  ·  **Matrix/take:** B-25703 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-42639_wabash-blues/loc_original.wav` (SHA-256 `f79d0fdfdeb1d82c...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -25.7 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -13.5 dBFS -> SNR ~12.2 dB
* Clicks/crackle: 4804.0 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -17.3 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-3295 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 57}
* Tuning offset vs A440: 42.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 7.3, 'distinct_peak': True, 'voiced_fraction': 0.63}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 4804 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 12.2 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3295 Hz -> hiss low-pass at 5272 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3295 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=8.5, max_ms=4.0, max_percent_replaced=2.0, detected=13017, repaired=13017, skipped_too_long=0, samples_replaced=147447, percent_samples_replaced=1.7006
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=7.5, max_ms=1.0, detected=10651, repaired=10651, skipped_too_long=0, samples_replaced=111746, percent_samples_replaced=1.2888
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-7.02
6. **hiss low-pass** - fc_hz=5272, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3295.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.72, 2.12]
8. **level match** - original_lufs=-15.95, restored_lufs=-17.73, gain_db=-0.28, limiter=False
9. **timing** - seconds=120.3

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -25.7 | -31.0 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -24.7 | -29.1 |
| Programme (p90) minus surface noise (dB) | 12.2 | 16.0 |
| Impulses per minute (AR detector, k=8) | 4804.0 | 233.3 |
| Impulses longer than 2 ms | 0 | 1 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -17.3 | -34.5 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -29.0, 'removed_vs_original_energy_300_3000hz_db': -18.6, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.99% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
