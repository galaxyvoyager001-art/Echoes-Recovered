# Restoration log - In the evening

* **Performer:** Jean Goldkette Orchestra  ·  **Recorded:** 1924-03-27, Detroit
* **LoC item:** https://www.loc.gov/item/jukebox-69781/  ·  **Disc:** Victor 19308  ·  **Matrix/take:** B-29807 (Matrix ID) / 3
* **Source file:** `data/originals/jukebox-69781_in-the-evening/loc_original.wav` (SHA-256 `bd83e86b64b2f691...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -45.0 dBFS (measured from lead-in groove (0.60 s)); programme p90 -20.8 dBFS -> SNR ~24.2 dB
* Clicks/crackle: 3238.6 impulses/min, median length 0.23 ms, 4 longer than 2 ms
* Hiss: 5-10 kHz band sits -22.9 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-3618 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -6.85, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -13.0 cents; wow indicator: {'peak_freq_hz': 1.063, 'implied_rpm': 63.8, 'peak_over_neighbourhood_db': 4.8, 'distinct_peak': True, 'voiced_fraction': 0.39}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 3239 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 24.2 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3618 Hz -> hiss low-pass at 5789 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3618 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=7.5, max_ms=4.0, max_percent_replaced=2.0, detected=12059, repaired=12059, skipped_too_long=0, samples_replaced=148391, percent_samples_replaced=1.7906
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=6.5, max_ms=1.0, detected=9145, repaired=9145, skipped_too_long=0, samples_replaced=97983, percent_samples_replaced=1.1823
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (0.60 s), stft=2048 Hann / hop 512, mean_gain_db=-13.22
6. **hiss low-pass** - fc_hz=5789, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3618.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.77, 2.16]
8. **level match** - original_lufs=-24.33, restored_lufs=-24.33, gain_db=0.88, limiter=False
9. **timing** - seconds=54.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -45.0 | -65.7 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -36.5 | -37.0 |
| Programme (p90) minus surface noise (dB) | 24.2 | 45.0 |
| Impulses per minute (AR detector, k=8) | 3238.6 | 221.3 |
| Impulses longer than 2 ms | 4 | 4 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -22.9 | -47.1 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -42.1, 'removed_vs_original_energy_300_3000hz_db': -22.9, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 2.97% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
