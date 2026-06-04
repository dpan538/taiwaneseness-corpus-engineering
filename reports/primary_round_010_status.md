# Round010 Status

Updated: 2026-06-04T19:45:00+10:00

## Automation-run Progress

- Accepted records in Round010: **200 / 500**
- Push threshold: second **100-record checkpoint** reached
- Execution log rows: **202**
- Unique executed URL/tasks: **202**
- Successful executed URL/tasks: **200**
- Failed executed URL/tasks: **2**
- Failure ratio: **1.0%**
- Count rule: only real accepted records with source refs, date/year evidence, markers, dedupe keys, unique attestation IDs, and successful execution-log rows are counted.

## Batch 005

Added **100** new true accepted records in `working/manual_harvest_primary_round_010_batch_005.csv`.

- Source family: Taiwan Tourism Administration Open Multimedia Data exact restaurant pages
- Scan method: exact restaurant URL range scan with per-page fetch; generated search instructions were not counted
- De-duplication: skipped existing overlay source URLs and restaurant artifact IDs; zh/en duplicates of the same restaurant ID were collapsed to one source artifact
- Source type: `official_open_data`
- Corridor: Taiwan-side
- Validation: grade **A**
- Unique source refs: **100**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**
- Anomaly gate: no critical alerts and no warnings

## Round010 Batches 001-005

`working/manual_harvest_primary_round_010_batches_001_005.csv` now contains **200** accepted records.

- Record quality: grade **A**
- Missing required fields: year 0, original_text 0, dish_marker 0, taiwan_marker 0, source_url 0
- Unique source refs: **200**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**
- Anomaly gate: no critical alerts and no warnings

## Overlay 001-009 Project Snapshot

`working/combined_attestations_plus_manual_candidates_001_009.csv` and `data/harvested/combined_attestations_working_round010.csv` now contain **1761** rows.

- Usable records: **1682**
- Unique sources: **597**
- Health score: **85.36**
- Health grade: **C**
- Credibility index: **0.698** (`good`)
- High-credibility ratio: **37.6%**
- Duplicate rate: **0.0**
- Split artifact groups in health audit: **0**
- Overlay record-quality grade: **B** because inherited older rows still include missing marker/text fields, one suspicious split group, and 7 invalid-year rows.
- Overlay anomaly gate: no critical alerts; one inherited warning remains (`low_conf_probable_rows`: 1). This is outside the current Round010 batch gate.

## Current Files

- `working/manual_harvest_primary_round_010_batch_005.csv`
- `working/manual_harvest_primary_round_010_batches_001_005.csv`
- `working/combined_attestations_plus_manual_candidates_001_009.csv`
- `data/harvested/combined_attestations_working_round010.csv`
- `logs/primary_round_010_execution_log.csv`
- `reports/record_quality_round_010_batch_005.*`
- `reports/record_quality_round_010_batches_001_005.*`
- `reports/anomaly_primary_round_010_batch_005.*`
- `reports/anomaly_primary_round_010_batches_001_005.*`
- `reports/record_quality_round_010_overlay_001_009.*`
- `reports/anomaly_primary_round_010_overlay_001_009.*`
- `reports/corpus_health_round_010_overlay_001_009.*`
- `reports/credibility_*_round_010_overlay_001_009.*`
- `reports/progress_dashboard_round_010_validation.*`

## Next Step

Continue toward **300 / 500** using the same exact-source execution and current-batch validation gates. Do not count URL search plans or duplicated zh/en pages as progress.
