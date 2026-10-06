# Restoration log - Livery stable blues

* **Performer:** Handy's Orchestra  ·  **Recorded:** 1917-09-24, New York
* **LoC item:** https://www.loc.gov/item/jukebox-657649/  ·  **Disc:** Columbia A2419  ·  **Matrix/take:** 77377 (Matrix ID) / 1
* **Source file:** `data/originals/jukebox-657649_livery-stable-blues/loc_original.wav` (SHA-256 `21224debcc4f6af4...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -47.7 dBFS (measured from lead-in groove (0.50 s)); programme p90 -16.5 dBFS -> SNR ~31.2 dB
* Clicks/crackle: 4444.2 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -14.8 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~22-3122 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 57}
* Tuning offset vs A440: 4.0 cents; wow indicator: {'peak_freq_hz': 1.375, 'implied_rpm': 82.5, 'peak_over_neighbourhood_db': 7.0, 'distinct_peak': True, 'voiced_fraction': 0.47}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 4444 impulses/min measured -> declick threshold 7.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 31.2 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3122 Hz -> hiss low-pass at 4995 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3122 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=7.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=12829, repaired=12829, skipped_too_long=0, samples_replaced=145885, percent_samples_replaced=1.929
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=7.0, max_ms=1.0, detected=10280, repaired=10280, skipped_too_long=0, samples_replaced=106799, percent_samples_replaced=1.4121
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (0.50 s), stft=2048 Hann / hop 512, mean_gain_db=-0.9
6. **hiss low-pass** - fc_hz=4995, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3122.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-2.88, 2.42]
8. **level match** - original_lufs=-18.48, restored_lufs=-18.48, gain_db=1.53, limiter=False
9. **timing** - seconds=86.2

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -47.7 | -73.2 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -28.0 | -30.1 |
| Programme (p90) minus surface noise (dB) | 31.2 | 57.0 |
| Impulses per minute (AR detector, k=8) | 4444.2 | 60.5 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -14.8 | -34.3 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -30.5, 'removed_vs_original_energy_300_3000hz_db': -22.0, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 3.34% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
