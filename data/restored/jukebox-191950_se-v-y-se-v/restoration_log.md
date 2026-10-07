# Restoration log - Se vá y se vá ... !

* **Performer:** Schultze, Jorge  ·  **Recorded:** 1917-07-22, La Paz
* **LoC item:** https://www.loc.gov/item/jukebox-191950/  ·  **Disc:** Victor 69846  ·  **Matrix/take:** G-2173 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-191950_se-v-y-se-v/loc_original.wav` (SHA-256 `ae2fc99ae96a4922...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -36.2 dBFS (measured from lead-in groove (1.00 s)); programme p90 -18.1 dBFS -> SNR ~18.1 dB
* Clicks/crackle: 874.9 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -20.5 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~172-3338 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.0, 'samples_over_98.5pct_fullscale': 1}
* Tuning offset vs A440: -4.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 6.8, 'distinct_peak': True, 'voiced_fraction': 0.56}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 875 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 18.1 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3338 Hz -> hiss low-pass at 5341 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3338 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=2259, repaired=2259, skipped_too_long=0, samples_replaced=24365, percent_samples_replaced=0.3642
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=7770, repaired=7770, skipped_too_long=0, samples_replaced=81779, percent_samples_replaced=1.2223
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=lead-in groove (1.00 s), stft=2048 Hann / hop 512, mean_gain_db=-12.34
6. **hiss low-pass** - fc_hz=5341, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3338.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-4.0, 2.5]
8. **level match** - original_lufs=-22.19, restored_lufs=-22.19, gain_db=1.15, limiter=False
9. **timing** - seconds=25.8

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -36.2 | -53.5 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -33.5 | -33.8 |
| Programme (p90) minus surface noise (dB) | 18.1 | 35.5 |
| Impulses per minute (AR detector, k=8) | 874.9 | 17.8 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -20.5 | -45.8 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -37.9, 'removed_vs_original_energy_300_3000hz_db': -21.9, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.59% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
