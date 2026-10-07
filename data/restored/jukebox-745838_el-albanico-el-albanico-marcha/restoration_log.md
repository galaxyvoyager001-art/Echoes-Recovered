# Restoration log - El albanico, El albanico : Marcha

* **Performer:** Regt. Band of H. M. Scots Guards  ·  **Recorded:** 1911-12-31, London
* **LoC item:** https://www.loc.gov/item/jukebox-745838/  ·  **Disc:** Columbia A1398  ·  **Matrix/take:** 27678 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-745838_el-albanico-el-albanico-marcha/loc_original.wav` (SHA-256 `26c5de6c3c0e19d0...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -38.4 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -24.2 dBFS -> SNR ~14.3 dB
* Clicks/crackle: 2298.3 impulses/min, median length 0.23 ms, 4 longer than 2 ms
* Hiss: 5-10 kHz band sits -11.7 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~172-2089 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.59, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 6.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.55}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 2298 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 14.3 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 2089 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2500 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=11884, repaired=11884, skipped_too_long=0, samples_replaced=135572, percent_samples_replaced=1.6252
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.5, max_ms=1.0, detected=6584, repaired=6584, skipped_too_long=0, samples_replaced=67921, percent_samples_replaced=0.8142
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.46
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2500.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.21, 1.24]
8. **level match** - original_lufs=-27.0, restored_lufs=-27.0, gain_db=1.31, limiter=False
9. **timing** - seconds=58.3

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -38.4 | -53.9 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -38.3 | -52.5 |
| Programme (p90) minus surface noise (dB) | 14.3 | 30.2 |
| Impulses per minute (AR detector, k=8) | 2298.3 | 27.5 |
| Impulses longer than 2 ms | 4 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -11.7 | -39.9 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -36.9, 'removed_vs_original_energy_300_3000hz_db': -17.5, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.44% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
