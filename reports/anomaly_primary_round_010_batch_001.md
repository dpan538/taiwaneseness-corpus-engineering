# Corpus Anomaly Report

Generated: 2026-06-04T12:29:00

## Summary

- total_rows: 7
- exact_duplicate_rows: 0
- suspicious_split_groups: 0
- year_outliers: 0
- marker_issues: 0
- high_concentration_sources: 7
- low_conf_verified_rows: 0
- low_conf_probable_rows: 0
- short_text_rows: 0
- fuzzy_duplicate_pairs: 0

## Field Completeness

| field | missing_count |
| --- | --- |
| attestation_id | 0 |
| source_id | 0 |
| year | 0 |
| period | 0 |
| corridor | 0 |
| dish_marker | 0 |
| taiwan_marker | 0 |
| verification_level | 0 |

## Verification Level Distribution

| level | count | ratio |
| --- | --- | --- |
| verified | 6 | 0.8571 |
| probable | 1 | 0.1429 |

## Detailed Files

- exact_dups: `reports/anomaly_primary_round_010_batch_001_exact_dups.csv`
- suspicious_split: `reports/anomaly_primary_round_010_batch_001_suspicious_split.csv`
- year_outliers: `reports/anomaly_primary_round_010_batch_001_year_outliers.csv`
- marker_issues: `reports/anomaly_primary_round_010_batch_001_marker_issues.csv`
- source_concentration: `reports/anomaly_primary_round_010_batch_001_source_concentration.csv`
- low_conf_verified: `reports/anomaly_primary_round_010_batch_001_low_conf_verified.csv`
- low_conf_probable: `reports/anomaly_primary_round_010_batch_001_low_conf_probable.csv`
- short_text: `reports/anomaly_primary_round_010_batch_001_short_text.csv`
- fuzzy_dups: `reports/anomaly_primary_round_010_batch_001_fuzzy_dups.csv`

## Recommendations

- Add source-diverse records or downweight concentrated sources in interpretation.
