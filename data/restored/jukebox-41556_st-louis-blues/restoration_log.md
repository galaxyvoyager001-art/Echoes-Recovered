# Restoration log - St. Louis blues

* **Performer:** Original Dixieland Jazz Band  ·  **Recorded:** 1921-05-25, New York
* **LoC item:** https://www.loc.gov/item/jukebox-41556/  ·  **Disc:** Victor 18772  ·  **Matrix/take:** B-25412 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-41556_st-louis-blues/loc_original.wav` (SHA-256 `808f119cf86d6d95...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -27.3 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -15.5 dBFS -> SNR ~11.7 dB
* Clicks/crackle: 2899.3 impulses/min, median length 0.23 ms, 1 longer than 2 ms
* Hiss: 5-10 kHz band sits -26.1 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-4565 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.42, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 18.0 cents; wow indicator: {'peak_freq_hz': 1.313, 'implied_rpm': 78.8, 'peak_over_neighbourhood_db': 8.1, 'distinct_peak': True, 'voiced_fraction': 0.51}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 2899 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 11.7 dB -> noise over-subtraction x1.3, gain floor -10.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 4565 Hz -> hiss low-pass at 7304 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-4000 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=14196, repaired=14196, skipped_too_long=0, samples_replaced=163106, percent_samples_replaced=1.8915
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.5, max_ms=1.0, detected=7174, repaired=7174, skipped_too_long=0, samples_replaced=74901, percent_samples_replaced=0.8686
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-10.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-6.8
6. **hiss low-pass** - fc_hz=7304, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=4000.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.77, 2.5]
8. **level match** - original_lufs=-18.51, restored_lufs=-18.51, gain_db=1.52, limiter=False
9. **timing** - seconds=60.1

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -27.3 | -28.5 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -27.0 | -27.8 |
| Programme (p90) minus surface noise (dB) | 11.7 | 13.1 |
| Impulses per minute (AR detector, k=8) | 2899.3 | 357.2 |
| Impulses longer than 2 ms | 1 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -26.1 | -34.3 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -35.5, 'removed_vs_original_energy_300_3000hz_db': -19.1, 'removed_vs_original_energy_above_5khz_db': -0.5}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.76% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
