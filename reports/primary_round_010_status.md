# Round010 Status

Updated: 2026-06-04T21:45:00+10:00

## Automation-run Progress

- Accepted records in Round010: **400 / 500**
- Push threshold: fourth **100-record checkpoint** reached
- Execution log rows: **402**
- Unique executed URL/tasks: **402**
- Successful executed URL/tasks: **400**
- Failed executed URL/tasks: **2**
- Failure ratio: **0.5%**
- Count rule: only real accepted records with source refs, date/year evidence, markers, dedupe keys, unique attestation IDs, and successful execution-log rows are counted.

## Batch 007

Added **100** new true accepted records in `working/manual_harvest_primary_round_010_batch_007.csv`.

- Source family: Taiwan Tourism Administration Open Multimedia Data exact restaurant pages
- Scan method: exact restaurant URL range scan with per-page fetch; generated search instructions were not counted
- De-duplication: skipped existing overlay source URLs and restaurant artifact IDs; zh/en duplicate pages of the same restaurant ID are counted once
- Scan effort: 3060 exact URL attempts were needed to find 100 accepted new artifacts, indicating lower remaining density in this source family
- Source type: `official_open_data`
- Corridor: Taiwan-side
- Validation: grade **A**
- Unique source refs: **100**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**
- Anomaly gate: no critical alerts and no warnings

## Round010 Batches 001-007

`working/manual_harvest_primary_round_010_batches_001_007.csv` now contains **400** accepted records.

- Record quality: grade **A**
- Missing required fields: year 0, original_text 0, dish_marker 0, taiwan_marker 0, source_url 0
- Unique source refs: **400**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**
- Anomaly gate: no critical alerts and no warnings

## Overlay 001-011 Project Snapshot

`working/combined_attestations_plus_manual_candidates_001_011.csv` and `data/harvested/combined_attestations_working_round010.csv` now contain **1961** rows.

- Usable records: **1882**
- Unique sources: **797**
- Health score: **85.41**
- Health grade: **C**
- Credibility index: **0.708** (`good`)
- High-credibility ratio: **44.0%**
- Duplicate rate: **0.0**
- Split artifact groups in health audit: **0**
- Overlay record-quality grade: **B** because inherited older rows still include missing marker/text fields, one suspicious split group, and 7 invalid-year rows.
- Overlay anomaly gate: no critical alerts; one inherited warning remains (`low_conf_probable_rows`: 1). This is outside the current Round010 batch gate.

## Next Step

Continue toward **500 / 500**, but expect lower yield from the same Taiwan Tourism open-data source family. Consider using more targeted seeds for the final 100 rather than only wide sequential scans.
