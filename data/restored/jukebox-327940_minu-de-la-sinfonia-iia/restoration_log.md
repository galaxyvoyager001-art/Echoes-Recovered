# Restoration log - Minué de la sinfonia IIa

* **Performer:** Banda Del Real Cuerpo De Guardias Alabarderos De Madrid  ·  **Recorded:** 1909-02-06, Madrid
* **LoC item:** https://www.loc.gov/item/jukebox-327940/  ·  **Disc:** Victor 62660  ·  **Matrix/take:** 342y (Matrix ID) / [1]
* **Source file:** `data/originals/jukebox-327940_minu-de-la-sinfonia-iia/loc_original.wav` (SHA-256 `059a478a2067a6c5...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -40.8 dBFS (measured from lead-in groove (0.50 s)); programme p90 -22.4 dBFS -> SNR ~18.5 dB
* Clicks/crackle: 369.2 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -17.9 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~172-2196 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -2.63, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -8.0 cents; wow indicator: {'peak_freq_hz': 1.313, 'implied_rpm': 78.8, 'peak_over_neighbourhood_db': 5.2, 'distinct_peak': True, 'voiced_fraction': 0.6}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 369 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.5 sigma.
* Estimated SNR 18.5 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 2196 Hz -> hiss low-pass at 4500 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-2500 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=1136, repaired=1135, skipped_too_long=1, samples_replaced=12267, percent_samples_replaced=0.1515
4. **decrackle (pass 2)** - order=24, k_requested=5.5, k_used=5.5, max_ms=1.0, detected=4296, repaired=4295, skipped_too_long=1, samples_replaced=45587, percent_samples_replaced=0.5629
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=lead-in groove (0.50 s), stft=2048 Hann / hop 512, mean_gain_db=-12.31
6. **hiss low-pass** - fc_hz=4500, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=2500.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.41, 1.59]
8. **level match** - original_lufs=-26.24, restored_lufs=-28.48, gain_db=-1.45, limiter=False
9. **timing** - seconds=29.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -40.8 | -61.4 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -40.5 | -52.2 |
| Programme (p90) minus surface noise (dB) | 18.5 | 37.0 |
| Impulses per minute (AR detector, k=8) | 369.2 | 27.0 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -17.9 | -52.1 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -40.1, 'removed_vs_original_energy_300_3000hz_db': -22.1, 'removed_vs_original_energy_above_5khz_db': -0.0}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 0.71% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
