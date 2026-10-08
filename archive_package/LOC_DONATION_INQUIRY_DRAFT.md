# DRAFT - not sent. Fill in the bracketed fields and decide whether to send.

**To:** sounddonations@loc.gov
**Subject:** Donation inquiry: documented restorations of 103 National Jukebox recordings (1901-1925)

Dear Recorded Sound Section,

I am writing to ask whether the Recorded Sound Section would have any interest in a small set of digital restoration files I produced from recordings in the National Jukebox. I understand from your donations page that you must avoid unnecessary duplication. These files are derivatives of transfers the Library already holds, so I would understand completely if they fall outside your collecting scope.

**What the files are**
* 103 commercially issued Victor and Columbia acoustic discs recorded between May 1901 and January 1925 in 30 cities (in the United States, Puerto Rico, Latin America, Europe and Japan), selected from the National Jukebox. Each item's Rights & Access statement and its recording and issue information were checked: each was recorded either before 1922 or between 1922 and January 1925 (on the assumption that the latter were issued by the end of 1925, so their 100-year term ended on 31 December 2025), and LoC holds a disc label image for each. The list with LoC item URLs is attached (catalog.csv).
* For each recording: the unmodified LoC transfer (preserved bit-exact, with SHA-256 checksums), a restored version (16-bit/44.1 kHz FLAC, mono), an A/B comparison file, the exact difference signal, before/after spectrograms, and a parameter log.
* The restoration used documented, non-generative signal processing: autoregressive click detection with least-squares interpolation, decision-directed Wiener noise reduction, low-pass filtering above the measured recorded band, and a bounded resonance EQ. No machine-learning or generative models were used, and no speed or pitch changes were made. Full source code and methodology are public: https://github.com/galaxyvoyager001-art/Echoes-Recovered

**Donor information**
* Name: [YOUR NAME]
* Address: [YOUR MAILING ADDRESS]
* Phone: [YOUR PHONE]
* Title/description: "Echoes Recovered" restorations of 103 National Jukebox recordings (Victor and Columbia, 1901-1925)
* Record labels: Victor Talking Machine Co.; Columbia Phonograph Co. (original issues)
* Count: 103 recordings (about [SIZE] GB in total)
* Physical condition: born-digital files; no physical media

The files carry the credit line "Library of Congress, National Jukebox." This is an independent project and does not imply any endorsement by the Library.

Thank you for your time and for making these recordings available.

Sincerely,
[YOUR NAME]
