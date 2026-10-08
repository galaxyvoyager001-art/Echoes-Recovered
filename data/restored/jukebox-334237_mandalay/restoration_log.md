# Restoration log - Mandalay

* **Performer:** Art Hickman's Orchestra  ·  **Recorded:** 1924-06-13, Los Angeles
* **LoC item:** https://www.loc.gov/item/jukebox-334237/  ·  **Disc:** Victor 19379  ·  **Matrix/take:** PB-20 (Matrix ID) / 4
* **Source file:** `data/originals/jukebox-334237_mandalay/loc_original.wav` (SHA-256 `47d3bbe948ae43b1...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -40.9 dBFS (measured from lead-in groove (0.60 s)); programme p90 -18.5 dBFS -> SNR ~22.4 dB
* Clicks/crackle: 1934.3 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -23.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~237-3208 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -2.23, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 49.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.52}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 1934 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 22.4 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3208 Hz -> hiss low-pass at 5133 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3208 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.0, max_ms=4.0, max_percent_replaced=2.0, detected=10046, repaired=10045, skipped_too_long=1, samples_replaced=108267, percent_samples_replaced=1.2692
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.0, max_ms=1.0, detected=10288, repaired=10287, skipped_too_long=1, samples_replaced=106770, percent_samples_replaced=1.2516
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (0.60 s), stft=2048 Hann / hop 512, mean_gain_db=-12.95
6. **hiss low-pass** - fc_hz=5133, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3208.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.41, 1.99]
8. **level match** - original_lufs=-21.87, restored_lufs=-21.87, gain_db=1.5, limiter=False
9. **timing** - seconds=44.4

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -40.9 | -59.8 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -34.4 | -35.4 |
| Programme (p90) minus surface noise (dB) | 22.4 | 41.2 |
| Impulses per minute (AR detector, k=8) | 1934.3 | 234.0 |
| Impulses longer than 2 ms | 0 | 9 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -23.0 | -39.9 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -39.4, 'removed_vs_original_energy_300_3000hz_db': -23.2, 'removed_vs_original_energy_above_5khz_db': -0.3}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.52% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
