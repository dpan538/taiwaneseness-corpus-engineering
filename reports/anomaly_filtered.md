# Corpus Anomaly Report

Generated: 2026-06-03T22:22:11

## Summary

- total_rows: 1427
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
| probable | 1323 | 0.9271 |
| candidate | 79 | 0.0554 |
| (blank) | 25 | 0.0175 |

## Detailed Files

- exact_dups: `reports/anomaly_filtered_exact_dups.csv`
- suspicious_split: `reports/anomaly_filtered_suspicious_split.csv`
- year_outliers: `reports/anomaly_filtered_year_outliers.csv`
- marker_issues: `reports/anomaly_filtered_marker_issues.csv`
- source_concentration: `reports/anomaly_filtered_source_concentration.csv`
- low_conf_verified: `reports/anomaly_filtered_low_conf_verified.csv`
- low_conf_probable: `reports/anomaly_filtered_low_conf_probable.csv`
- short_text: `reports/anomaly_filtered_short_text.csv`
- fuzzy_dups: `reports/anomaly_filtered_fuzzy_dups.csv`

## Recommendations

- Review low-confidence probable rows and demote if needed.
