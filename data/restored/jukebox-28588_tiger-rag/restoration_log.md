# Restoration log - Tiger rag

* **Performer:** Original Dixieland Jazz Band  ·  **Recorded:** 1918-03-25, New York
* **LoC item:** https://www.loc.gov/item/jukebox-28588/  ·  **Disc:** Victor 18472  ·  **Matrix/take:** B-21701 (Matrix ID) / 3
* **Source file:** `data/originals/jukebox-28588_tiger-rag/loc_original.wav` (SHA-256 `859a8eac0f83266d...`, left unmodified)
* **Source format:** 44100 Hz, 1 ch; L/R correlation 1.000000 -> folded to mono

## Damage assessment (original)
* Surface noise: -28.0 dBFS (measured from minimum statistics (10th percentile x2)); programme p90 -13.7 dBFS -> SNR ~14.3 dB
* Clicks/crackle: 199.2 impulses/min, median length 0.23 ms, 0 longer than 2 ms
* Hiss: 5-10 kHz band sits -29.1 dB relative to the 300-3000 Hz band
* Frequency range carrying music: ~108-4307 Hz (acoustic horn recording)
* Hum: [{'freq_hz': 50.0, 'prominence_db': 11.8}]
* Peaks/clipping: {'peak_dbfs': 0.0, 'samples_over_98.5pct_fullscale': 296}
* Tuning offset vs A440: -32.0 cents; wow indicator: {'peak_freq_hz': 1.0, 'implied_rpm': 60.0, 'peak_over_neighbourhood_db': 0.0, 'distinct_peak': False, 'voiced_fraction': 0.34}

## Why these parameters
* High-pass at 50 Hz (4th order, zero phase): the acoustic horn captured almost nothing this low, so only turntable rumble/DC is removed.
* Hum detected at [50.0] Hz -> narrow notches (Q=30).
* 199 impulses/min measured -> declick threshold 8.0 sigma, decrackle 5.5 sigma.
* Estimated SNR 14.3 dB -> noise over-subtraction x1.3, gain floor -13.0 dB (keeps some surface noise rather than create artefacts).
* Usable band ends near 4307 Hz -> hiss low-pass at 6891 Hz (well above the last musical content).
* Adaptive EQ restricted to 250-4000 Hz, strength 0.5, cuts <= 4.0 dB, boosts <= 2.5 dB.

## Processing chain (as executed)
1. **speed correction** - applied=False, reason=no override; tuning offset alone cannot distinguish transfer-speed error from period pitch standards
2. **high-pass (rumble/DC)** - fc_hz=50.0, order=4, zero_phase=True, hum_notches_hz=[50.0]
3. **declick (AR detection + LSAR interpolation)** - order=32, k_requested=8.0, k=8.0, max_ms=4.0, max_percent_replaced=2.0, detected=620, repaired=620, skipped_too_long=0, samples_replaced=6807, percent_samples_replaced=0.0807
4. **decrackle (pass 2)** - order=24, k_requested=5.5, k_used=5.5, max_ms=1.0, detected=2093, repaired=2092, skipped_too_long=1, samples_replaced=21710, percent_samples_replaced=0.2573
5. **spectral denoise (decision-directed Wiener)** - over_sub=1.3, gain_floor_db=-13.0, dd_alpha=0.96, noise_profile=minimum statistics (10th percentile x2), stft=2048 Hann / hop 512, mean_gain_db=-8.42
6. **hiss low-pass** - fc_hz=6891, order=4, zero_phase=True
7. **adaptive EQ (resonance flattening)** - enabled=True, f_lo=250.0, f_hi=4000.0, strength=0.5, max_db=4.0, max_boost_db=2.5, tilt_db_per_oct=0.0, applied_range_db=[-4.0, 2.5]
8. **level match** - original_lufs=-15.81, restored_lufs=-18.03, gain_db=-1.07, limiter=False
9. **timing** - seconds=25.8

## Before / after (same measurement code on both files)
| Measure | Original | Restored |
|---|---|---|
| Surface-noise RMS in lead-in / quietest frames (dBFS) | -28.0 | -31.7 |
| Noise floor during music, 5th pct. 50 ms frames (dBFS) | -26.8 | -30.4 |
| Programme (p90) minus surface noise (dB) | 14.3 | 16.2 |
| Impulses per minute (AR detector, k=8) | 199.2 | 172.7 |
| Impulses longer than 2 ms | 0 | 1 |
| 5-10 kHz energy relative to 300-3000 Hz (dB) | -29.1 | -37.6 |

## What was removed
`removed_component.mp3` is the exact difference *original - (signal after the click, noise and filter stages)*, i.e. before the EQ and level match. Listening to it is the
quickest check that the chain removed surface noise and clicks rather than music. Measured: {'removed_rms_dbfs': -37.0, 'removed_vs_original_energy_300_3000hz_db': -24.2, 'removed_vs_original_energy_above_5khz_db': -0.4}

## What was *not* done
* No generative / AI models. Interpolated samples are computed only from neighbouring real samples (LSAR, max 4.0 ms per gap; 0.34% of samples in total).
* No pitch/speed change unless listed above; no reverb, stereo widening, bandwidth extension or limiting.
* Groove distortion / blasting from the original acoustic recording cannot be undone and was left as is.
