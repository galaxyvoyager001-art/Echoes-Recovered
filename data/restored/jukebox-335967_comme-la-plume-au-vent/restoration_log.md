# Restoration log - Comme la plume au vent

* **Performer:** Campagnola, Léon  ·  **Recorded:** 1911-07-08, Paris
* **LoC item:** https://www.loc.gov/item/jukebox-335967/  ·  **Disc:** Victor 45118  ·  **Matrix/take:** 16534u (Matrix ID) / [1]
* **Source file:** `data/originals/jukebox-335967_comme-la-plume-au-vent/loc_original.wav` (SHA-256 `46bc37c29fb23f80...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -37.1 dBFS (measured from lead-in groove (0.70 s)); programme p90 -16.4 dBFS -> SNR ~20.7 dB
* Clicks/crackle: 507.5 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -22.0 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~237-3424 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -0.42, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -32.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.61}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 508 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 20.7 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3424 Hz -> hiss low-pass at 5478 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3424 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=1155, repaired=1155, skipped_too_long=0, samples_replaced=12683, percent_samples_replaced=0.2095
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.0, max_ms=1.0, detected=5191, repaired=5191, skipped_too_long=0, samples_replaced=54647, percent_samples_replaced=0.9028
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (0.70 s), stft=2048 Hann / hop 512, mean_gain_db=-13.59
6. **hiss low-pass** - fc_hz=5478, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3424.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.96, 2.5]
8. **level match** - original_lufs=-18.51, restored_lufs=-19.64, gain_db=0.1, limiter=False
9. **timing** - seconds=20.5

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -37.1 | -58.4 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -36.0 | -45.3 |
| Programme (p90) minus surface noise (dB) | 20.7 | 40.8 |
| Impulses per minute (AR detector, k=8) | 507.5 | 28.8 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -22.0 | -41.2 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -36.5, 'removed_vs_original_energy_300_3000hz_db': -25.8, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.11% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
