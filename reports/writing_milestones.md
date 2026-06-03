# Writing Milestones

| milestone | status | metric | value | threshold | notes |
| --- | --- | --- | --- | --- | --- |
| M1_method_write_ready | pass | source_registry_records | 29 | >=15 |  |
| M1_method_write_ready | fail | raw_manifest_records | 0 | >=50 |  |
| M1_method_write_ready | pass | negative_search_Korea | present | present |  |
| M1_method_write_ready | pass | negative_search_Vietnam | present | present |  |
| M1_method_write_ready | pass | negative_search_Latin America | present | present |  |
| M2_1946_1987_exploratory_ready | fail | usable_1946_1987 | 230 | >=350 |  |
| M2_1946_1987_exploratory_ready | pass | verified_probable_share | 94.32 | >=60% |  |
| M2_1946_1987_exploratory_ready | pass | time_bins_ge_20 | 4 | >=3 |  |
| M2_1946_1987_exploratory_ready | pass | Taipei_records | 34 | >=30 |  |
| M2_1946_1987_exploratory_ready | fail | Tainan_records | 27 | >=30 |  |
| M2_1946_1987_exploratory_ready | fail | Kaohsiung_records | 29 | >=30 |  |
| M2b_1946_1987_stronger_claim_ready | fail | usable_1946_1987 | 230 | >=600 |  |
| M2b_1946_1987_stronger_claim_ready | pass | verified_probable_share | 94.32 | >=80% |  |
| M2b_1946_1987_stronger_claim_ready | pass | all_time_bins_ge_20 | {'1970-1979': 50, '1946-1959': 39, '1960-1969': 36, '1980-1987': 105} | all four >=20 |  |
| M3_1987_2015_exploratory_ready | fail | usable_1987_2015 | 110 | >=400 |  |
| M3_1987_2015_exploratory_ready | fail | mainland_corridors_ge_50 | {'Singapore': 40, 'North China': 11, 'Yangtze River Delta': 26, 'Taiwan-side': 28, 'Japan': 3, 'North America': 1, 'Hong Kong': 1} | >=3 corridors |  |
| M3_1987_2015_exploratory_ready | fail | time_bins_ge_100 | {'1996-2005': 39, '1988-1995': 19, '2006-2014': 52} | >=2 bins |  |
| M4_platform_reference_ready | fail | target_merchants | 0 | >=60 |  |
| M4_platform_reference_ready | fail | control_a_merchants | 0 | >=30 |  |
| M4_platform_reference_ready | fail | control_b_merchants | 0 | >=30 |  |
| M4_platform_reference_ready | fail | reviews | 0 | >=800 |  |
| M4_platform_reference_ready | fail | platform_ownership_matching_rate | 0.00 | >=40% |  |

## Interpretation

- A failed milestone does not stop writing entirely; it limits what kind of claims can be written.
- If M2 passes but M2b fails, the 1946-1987 chapter should be explicitly exploratory.
- If M3 fails after sustained collection, downgrade 1987-2015 to a transition/case-discussion layer.
