# Restoration log - Red hot mamma

* **Performer:** Coon-sanders Original Nighthawk Orchestra  ·  **Recorded:** 1924-04-06, Kansas City
* **LoC item:** https://www.loc.gov/item/jukebox-69818/  ·  **Disc:** Victor 19316  ·  **Matrix/take:** B-29838 (Matrix ID) / 3
* **Source file:** `data/originals/jukebox-69818_red-hot-mamma/loc_original.wav` (SHA-256 `49ef0b7f1cd0798e...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -46.8 dBFS (measured from lead-in groove (0.50 s)); programme p90 -20.4 dBFS -> SNR ~26.4 dB
* Clicks/crackle: 1265.0 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -23.9 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-3833 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -5.63, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -21.0 cents; wow indicator: {'peak_freq_hz': 1.125, 'implied_rpm': 67.5, 'peak_over_neighbourhood_db': 7.2, 'distinct_peak': True, 'voiced_fraction': 0.44}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 1265 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 26.4 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3833 Hz -> hiss low-pass at 6133 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3833 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=3799, repaired=3799, skipped_too_long=0, samples_replaced=41245, percent_samples_replaced=0.5226
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.0, max_ms=1.0, detected=9744, repaired=9743, skipped_too_long=1, samples_replaced=103225, percent_samples_replaced=1.308
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (0.50 s), stft=2048 Hann / hop 512, mean_gain_db=-12.84
6. **hiss low-pass** - fc_hz=6133, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3833.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.95, 2.43]
8. **level match** - original_lufs=-23.3, restored_lufs=-23.3, gain_db=0.83, limiter=False
9. **timing** - seconds=36.4

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -46.8 | -65.6 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -34.3 | -34.1 |
| Programme (p90) minus surface noise (dB) | 26.4 | 45.5 |
| Impulses per minute (AR detector, k=8) | 1265.0 | 291.2 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -23.9 | -38.7 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -43.3, 'removed_vs_original_energy_300_3000hz_db': -24.5, 'removed_vs_original_energy_above_5khz_db': -0.5}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.83% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
