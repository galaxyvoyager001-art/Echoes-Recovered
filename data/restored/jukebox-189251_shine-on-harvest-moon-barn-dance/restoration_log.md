# Restoration log - Shine on, harvest moon barn dance

* **Performer:** Arthur Pryor's Band  ·  **Recorded:** 1910-02-15, Camden
* **LoC item:** https://www.loc.gov/item/jukebox-189251/  ·  **Disc:** Victor 16475  ·  **Matrix/take:** B-8630 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-189251_shine-on-harvest-moon-barn-dance/loc_original.wav` (SHA-256 `59db6a74290e31ab...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -24.6 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -12.2 dBFS -> SNR ~12.4 dB
* Clicks/crackle: 318.6 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -28.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-3876 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.46, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 14.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.5}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 319 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.5 sigma.
* Estimated SNR 12.4 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3876 Hz -> hiss low-pass at 6202 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3876 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=880, repaired=880, skipped_too_long=0, samples_replaced=9769, percent_samples_replaced=0.1406
4. **decrackle (pass 2)** - order=24, k_requested=5.5, k_used=5.5, max_ms=1.0, detected=2063, repaired=2063, skipped_too_long=0, samples_replaced=21777, percent_samples_replaced=0.3134
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.62
6. **hiss low-pass** - fc_hz=6202, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3876.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.68, 2.5]
8. **level match** - original_lufs=-14.94, restored_lufs=-16.44, gain_db=-0.78, limiter=False
9. **timing** - seconds=24.8

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -24.6 | -27.9 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -23.8 | -26.6 |
| Programme (p90) minus surface noise (dB) | 12.4 | 14.8 |
| Impulses per minute (AR detector, k=8) | 318.6 | 69.7 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -28.0 | -41.9 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -33.0, 'removed_vs_original_energy_300_3000hz_db': -20.1, 'removed_vs_original_energy_above_5khz_db': -0.2}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 0.45% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
