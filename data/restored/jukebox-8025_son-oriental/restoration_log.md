# Restoration log - Son oriental

* **Performer:** Martínez, Pedro  ·  **Recorded:** 1923-03-09, Havana
* **LoC item:** https://www.loc.gov/item/jukebox-8025/  ·  **Disc:** Victor 77089  ·  **Matrix/take:** G-2935 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-8025_son-oriental/loc_original.wav` (SHA-256 `25d970ac06bd8473...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -38.0 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -14.3 dBFS -> SNR ~23.7 dB
* Clicks/crackle: 1155.7 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -23.6 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-3252 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.0, 'samples_over_98.5pct_fullscale': 2}
* Tuning offset vs A440: 0.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.68}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 1156 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 23.7 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3252 Hz -> hiss low-pass at 5203 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3252 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=3304, repaired=3301, skipped_too_long=3, samples_replaced=36088, percent_samples_replaced=0.4844
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=8614, repaired=8610, skipped_too_long=4, samples_replaced=91747, percent_samples_replaced=1.2315
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-7.96
6. **hiss low-pass** - fc_hz=5203, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3252.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.78, 2.5]
8. **level match** - original_lufs=-18.09, restored_lufs=-18.09, gain_db=1.98, limiter=False
9. **timing** - seconds=23.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -38.0 | -43.7 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -37.0 | -40.6 |
| Programme (p90) minus surface noise (dB) | 23.7 | 29.4 |
| Impulses per minute (AR detector, k=8) | 1155.7 | 177.7 |
| Impulses longer than 2 ms | 0 | 2 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -23.6 | -40.2 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -36.9, 'removed_vs_original_energy_300_3000hz_db': -26.7, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.72% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
