# Restoration log - Rip saw blues

* **Performer:** Art Landry Orchestra  ·  **Recorded:** 1924-06-18, Oakland
* **LoC item:** https://www.loc.gov/item/jukebox-334419/  ·  **Disc:** Victor 19398  ·  **Matrix/take:** PB-33 (Matrix ID) / 5
* **Source file:** `data/originals/jukebox-334419_rip-saw-blues/loc_original.wav` (SHA-256 `a35fcf9a279878fd...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -36.7 dBFS (measured from lead-in groove (2.60 s)); programme p90 -24.0 dBFS -> SNR ~12.7 dB
* Clicks/crackle: 630.4 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -15.9 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~172-3208 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -2.54, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: -26.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.54}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 630 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 12.7 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3208 Hz -> hiss low-pass at 5133 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3208 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=1825, repaired=1824, skipped_too_long=1, samples_replaced=19459, percent_samples_replaced=0.2654
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=9787, repaired=9785, skipped_too_long=2, samples_replaced=103357, percent_samples_replaced=1.4098
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=lead-in groove (2.60 s), stft=2048 Hann / hop 512, mean_gain_db=-12.44
6. **hiss low-pass** - fc_hz=5133, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3208.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.08, 2.22]
8. **level match** - original_lufs=-26.38, restored_lufs=-30.08, gain_db=-1.32, limiter=False
9. **timing** - seconds=28.1

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -36.7 | -52.4 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -37.2 | -46.4 |
| Programme (p90) minus surface noise (dB) | 12.7 | 24.9 |
| Impulses per minute (AR detector, k=8) | 630.4 | 19.8 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -15.9 | -40.6 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -37.8, 'removed_vs_original_energy_300_3000hz_db': -14.3, 'removed_vs_original_energy_above_5khz_db': -0.1}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.68% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
