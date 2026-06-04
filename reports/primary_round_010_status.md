# Round010 Status

Updated: 2026-06-04T20:45:00+10:00

## Automation-run Progress

- Accepted records in Round010: **300 / 500**
- Push threshold: third **100-record checkpoint** reached
- Execution log rows: **302**
- Unique executed URL/tasks: **302**
- Successful executed URL/tasks: **300**
- Failed executed URL/tasks: **2**
- Failure ratio: **0.7%**
- Count rule: only real accepted records with source refs, date/year evidence, markers, dedupe keys, unique attestation IDs, and successful execution-log rows are counted.

## Batch 006

Added **100** new true accepted records in `working/manual_harvest_primary_round_010_batch_006.csv`.

- Source family: Taiwan Tourism Administration Open Multimedia Data exact restaurant pages
- Scan method: exact restaurant URL range scan with per-page fetch; generated search instructions were not counted
- De-duplication: skipped existing overlay source URLs and restaurant artifact IDs; zh/en duplicate pages of the same restaurant ID are counted once
- Source type: `official_open_data`
- Corridor: Taiwan-side
- Validation: grade **A**
- Unique source refs: **100**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**
- Anomaly gate: no critical alerts and no warnings

## Round010 Batches 001-006

`working/manual_harvest_primary_round_010_batches_001_006.csv` now contains **300** accepted records.

- Record quality: grade **A**
- Missing required fields: year 0, original_text 0, dish_marker 0, taiwan_marker 0, source_url 0
- Unique source refs: **300**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**
- Anomaly gate: no critical alerts and no warnings

## Overlay 001-010 Project Snapshot

`working/combined_attestations_plus_manual_candidates_001_010.csv` and `data/harvested/combined_attestations_working_round010.csv` now contain **1861** rows.

- Usable records: **1782**
- Unique sources: **697**
- Health score: **85.38**
- Health grade: **C**
- Credibility index: **0.703** (`good`)
- High-credibility ratio: **41.0%**
- Duplicate rate: **0.0**
- Split artifact groups in health audit: **0**
- Overlay record-quality grade: **B** because inherited older rows still include missing marker/text fields, one suspicious split group, and 7 invalid-year rows.
- Overlay anomaly gate: no critical alerts; one inherited warning remains (`low_conf_probable_rows`: 1). This is outside the current Round010 batch gate.

## Next Step

Continue toward **400 / 500** using the same exact-source execution and current-batch validation gates.
