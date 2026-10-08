# Restoration log - Frantic

* **Performer:** Halstead, Henry  ·  **Recorded:** 1924-06-20, Oakland
* **LoC item:** https://www.loc.gov/item/jukebox-317560/  ·  **Disc:** Victor 19513  ·  **Matrix/take:** PB-43 (Matrix ID) / 2
* **Source file:** `data/originals/jukebox-317560_frantic/loc_original.wav` (SHA-256 `aeb74b8eba5663ab...`, left unmodified)
* **Source format:** 44100 Hz, 2 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -44.0 dBFS (measured from lead-in groove (1.10 s)); programme p90 -17.5 dBFS -> SNR ~26.5 dB
* Clicks/crackle: 661.5 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -24.1 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~151-3768 Hz (acoustic horn recording)
* Hum: none detected
* Peaks/clipping: {'peak_dbfs': -3.69, 'samples_over_98.5pct_fullscale': 0}
* Tuning offset vs A440: 49.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.32}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* No mains hum peaks found (50/60 Hz + harmonics) -> no notch filters.
* 662 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.0 sigma.
* Estimated SNR 26.5 dB -> noise over-subtraction x1.2, gain floor -15.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 3768 Hz -> hiss low-pass at 6029 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-3768 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=1755, repaired=1754, skipped_too_long=1, samples_replaced=18425, percent_samples_replaced=0.2614
4. **decrackle (pass 2)** - order=24, k_requested=5.0, k_used=5.5, max_ms=1.0, detected=8801, repaired=8800, skipped_too_long=1, samples_replaced=92280, percent_samples_replaced=1.309
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.2, gain_floor_db=-15.0, dd_alpha=0.96, noise_profile=lead-in groove (1.10 s), stft=2048 Hann / hop 512, mean_gain_db=-12.34
6. **hiss low-pass** - fc_hz=6029, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=3768.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-3.53, 2.5]
8. **level match** - original_lufs=-20.69, restored_lufs=-20.69, gain_db=1.59, limiter=False
9. **timing** - seconds=28.0

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -44.0 | -59.6 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -35.2 | -35.5 |
| Programme (p90) minus surface noise (dB) | 26.5 | 42.1 |
| Impulses per minute (AR detector, k=8) | 661.5 | 136.8 |
| Impulses longer than 2 ms | 0 | 0 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -24.1 | -39.7 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -41.0, 'removed_vs_original_energy_300_3000hz_db': -26.7, 'removed_vs_original_energy_above_5khz_db': -0.3}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 1.57% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
