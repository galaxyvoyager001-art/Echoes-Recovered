# Restoration log - Le rêve

* **Performer:** Beyle, Léon  ·  **Recorded:** 1908-12-31, Paris
* **LoC item:** https://www.loc.gov/item/jukebox-307261/  ·  **Disc:** Victor 45008  ·  **Matrix/take:** 5628h (Matrix ID) / [1]
* **Source file:** `data/originals/jukebox-307261_le-r-ve/loc_original.wav` (SHA-256 `6197f50fedb69e0a...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -31.3 dBFS (measured from lead-in groove (1.00 s)); programme p90 -18.1 dBFS -> SNR ~13.2 dB
* Clicks/crackle: 142.7 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -16.3 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~194-3058 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 21}
* Tuning offset vs A440: 41.0 cents; wow indicator: {'peak_freq_hz': 1.125, 'implied_rpm': 67.5, 'peak_over_neighbourhood_db': 7.4, 'distinct_peak': True, 'voiced_fraction': 0.77}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 143 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.5 sigma.
* Estimated SNR 13.2 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3058 Hz -> hiss low-pass at 4893 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3058 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=397, repaired=397, skipped_too_long=0, samples_replaced=4668, percent_samples_replaced=0.0693
4. **decrackle (pass 2)** - order=24, k_requested=5.5, k_used=5.5, max_ms=1.0, detected=1108, repaired=1108, skipped_too_long=0, samples_replaced=11712, percent_samples_replaced=0.1739
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=lead-in groove (1.00 s), stft=2048 Hann / hop 512, mean_gain_db=-12.37
6. **hiss low-pass** - fc_hz=4893, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3058.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.9, 2.5]
8. **level match** - original_lufs=-21.11, restored_lufs=-21.11, gain_db=1.5, limiter=False
9. **timing** - seconds=20.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -31.3 | -52.8 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -33.6 | -42.8 |
| Programme (p90) minus surface noise (dB) | 13.2 | 34.5 |
| Impulses per minute (AR detector, k=8) | 142.7 | 10.2 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -16.3 | -42.3 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -31.3, 'removed_vs_original_energy_300_3000hz_db': -21.2, 'removed_vs_original_energy_above_5khz_db': -0.0}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 0.24% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
