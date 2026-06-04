# Corpus Anomaly Report

Generated: 2026-06-04T13:42:03

## Summary

- total_rows: 1861
- exact_duplicate_rows: 0
- suspicious_split_groups: 0
- year_outliers: 0
- marker_issues: 0
- high_concentration_sources: 0
- low_conf_verified_rows: 0
- low_conf_probable_rows: 1
- short_text_rows: 0
- fuzzy_duplicate_pairs: 0

## Field Completeness

| field | missing_count |
| --- | --- |
| attestation_id | 0 |
| source_id | 25 |
| year | 0 |
| period | 0 |
| corridor | 19 |
| dish_marker | 63 |
| taiwan_marker | 25 |
| verification_level | 25 |

## Verification Level Distribution

| level | count | ratio |
| --- | --- | --- |
| probable | 1461 | 0.7851 |
| verified | 296 | 0.1591 |
| candidate | 79 | 0.0425 |
| (blank) | 25 | 0.0134 |

## Detailed Files

- exact_dups: `reports/anomaly_primary_round_010_overlay_001_010_exact_dups.csv`
- suspicious_split: `reports/anomaly_primary_round_010_overlay_001_010_suspicious_split.csv`
- year_outliers: `reports/anomaly_primary_round_010_overlay_001_010_year_outliers.csv`
- marker_issues: `reports/anomaly_primary_round_010_overlay_001_010_marker_issues.csv`
- source_concentration: `reports/anomaly_primary_round_010_overlay_001_010_source_concentration.csv`
- low_conf_verified: `reports/anomaly_primary_round_010_overlay_001_010_low_conf_verified.csv`
- low_conf_probable: `reports/anomaly_primary_round_010_overlay_001_010_low_conf_probable.csv`
- short_text: `reports/anomaly_primary_round_010_overlay_001_010_short_text.csv`
- fuzzy_dups: `reports/anomaly_primary_round_010_overlay_001_010_fuzzy_dups.csv`

## Recommendations

- Review low-confidence probable rows and demote if needed.
