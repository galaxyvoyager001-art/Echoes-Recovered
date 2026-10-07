# Restoration log - Terence's farewell to Kathleen

* **Performer:** Thomas, William  ·  **Recorded:** 1912-12-31, London
* **LoC item:** https://www.loc.gov/item/jukebox-745857/  ·  **Disc:** Columbia A1385  ·  **Matrix/take:** 28268 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-745857_terence-s-farewell-to-kathleen/loc_original.wav` (SHA-256 `0ef849bd303b5af0...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -38.6 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -25.5 dBFS -> SNR ~13.0 dB
* Clicks/crackle: 6730.5 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -11.3 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-3015 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.59, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 14.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.48}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 6730 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 13.0 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3015 Hz -> hiss low-pass at 4824 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3015 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=9.5, max_ms=4.0, max_percent_replaced=2.0, detected=13215, repaired=13215, skipped_too_long=0, samples_replaced=150321, percent_samples_replaced=1.8711
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=8.0, max_ms=1.0, detected=17655, repaired=17655, skipped_too_long=0, samples_replaced=186697, percent_samples_replaced=2.3239
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-7.94
6. **hiss low-pass** - fc_hz=4824, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3015.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.98, 2.26]
8. **level match** - original_lufs=-27.48, restored_lufs=-27.48, gain_db=1.76, limiter=False
9. **timing** - seconds=149.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -38.6 | -56.9 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -38.2 | -55.0 |
| Programme (p90) minus surface noise (dB) | 13.0 | 31.8 |
| Impulses per minute (AR detector, k=8) | 6730.5 | 111.0 |
| Impulses longer than 2 ms | 0 | 2 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -11.3 | -37.5 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -37.1, 'removed_vs_original_energy_300_3000hz_db': -18.5, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 4.20% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
