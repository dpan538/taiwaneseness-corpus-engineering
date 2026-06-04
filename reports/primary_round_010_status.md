# Round010 Status

Updated: 2026-06-04T18:25:00+10:00

## Automation-run Progress

- Accepted records in Round010: **100 / 500**
- Push threshold: **100 accepted records** reached
- Execution log rows: **102**
- Successful executed URL/tasks: **100**
- Failed executed URL/tasks: **2**
- Failure ratio: **2.0%**
- Count rule: only real accepted records with source refs, date/year evidence, markers, dedupe keys, and execution-log success rows are counted.

## Batch 004

Added **41** new true accepted records in `working/manual_harvest_primary_round_010_batch_004.csv`.

- Source family: Taiwan Tourism Administration Open Multimedia Data exact restaurant pages
- Source type: `official_open_data`
- Corridor: Taiwan-side
- Validation: grade **A**
- Unique source refs: **41**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**

Two initial candidate URLs returned 404 and were not counted. One replacement candidate was detected as an inherited duplicate (`橋頭邊肉圓`) and was not counted. The final replacement record (`肉圓輝`) was verified through a separate exact source URL fetch.

## Round010 Batches 001-004

`working/manual_harvest_primary_round_010_batches_001_004.csv` now contains **100** accepted records.

- Record quality: grade **A**
- Missing required fields: year 0, original_text 0, dish_marker 0, taiwan_marker 0, source_url 0
- Unique source refs: **100**
- Duplicate URL groups: **0**
- Duplicate artifact groups: **0**
- Suspicious split groups: **0**
- Invalid years: **0**
- Anomaly gate: no critical alerts and no warnings

Source distribution for Round010 accepted records:

- `official_open_data`: 58
- `official_tourism_news`: 27
- `official_open_data_michelin`: 8
- `michelin_restaurant_page`: 3
- `official_tourism_profile`: 2
- `michelin_editorial`: 1
- `michelin_press_release_pdf`: 1

Corridor distribution:

- Taiwan-side: 96
- Korea: 4

## Overlay 001-008 Project Snapshot

`working/combined_attestations_plus_manual_candidates_001_008.csv` and `data/harvested/combined_attestations_working_round010.csv` now contain **1661** rows.

- Usable records: **1582**
- Unique sources: **497**
- Health score: **85.33**
- Health grade: **C**
- Credibility index: **0.692** (`good`)
- High-credibility ratio: **33.9%**
- Duplicate rate: **0.0**
- Split artifact groups in health audit: **0**
- Overlay record-quality grade: **B** because inherited older rows still include missing marker/text fields, one suspicious split group, and 7 invalid-year rows.
- Overlay anomaly gate: no critical alerts; one inherited warning remains (`low_conf_probable_rows`: 1). This is outside the current Round010 batch gate.

## Files Updated

- `working/manual_harvest_primary_round_010_batch_004.csv`
- `working/manual_harvest_primary_round_010_batches_001_004.csv`
- `working/combined_attestations_plus_manual_candidates_001_008.csv`
- `data/harvested/combined_attestations_working_round010.csv`
- `logs/primary_round_010_execution_log.csv`
- `reports/record_quality_round_010_batch_004.*`
- `reports/record_quality_round_010_batches_001_004.*`
- `reports/anomaly_primary_round_010_batch_004.*`
- `reports/anomaly_primary_round_010_batches_001_004.*`
- `reports/record_quality_round_010_overlay_001_008.*`
- `reports/anomaly_primary_round_010_overlay_001_008.*`
- `reports/corpus_health_round_010_overlay_001_008.*`
- `reports/credibility_*_round_010_overlay_001_008.*`
- `reports/progress_dashboard_round_010_validation.*`

## Commit Plan

Because Round010 reached the 100-record push threshold, commit and push this checkpoint with a description documenting the first 100 verified accepted records, the exact-source execution principle, and validation results.
