# Writing Milestones

| milestone | status | metric | value | threshold | notes |
| --- | --- | --- | --- | --- | --- |
| M1_method_write_ready | fail | source_registry_records | 0 | >=15 |  |
| M1_method_write_ready | fail | raw_manifest_records | 0 | >=50 |  |
| M1_method_write_ready | fail | negative_search_Korea | missing | present |  |
| M1_method_write_ready | fail | negative_search_Vietnam | missing | present |  |
| M1_method_write_ready | fail | negative_search_Latin America | missing | present |  |
| M2_1946_1987_exploratory_ready | fail | usable_1946_1987 | 109 | >=350 |  |
| M2_1946_1987_exploratory_ready | pass | verified_probable_share | 94.81 | >=60% |  |
| M2_1946_1987_exploratory_ready | fail | time_bins_ge_20 | 2 | >=3 |  |
| M2_1946_1987_exploratory_ready | fail | Taipei_records | 22 | >=30 |  |
| M2_1946_1987_exploratory_ready | fail | Tainan_records | 3 | >=30 |  |
| M2_1946_1987_exploratory_ready | fail | Kaohsiung_records | 18 | >=30 |  |
| M2b_1946_1987_stronger_claim_ready | fail | usable_1946_1987 | 109 | >=600 |  |
| M2b_1946_1987_stronger_claim_ready | pass | verified_probable_share | 94.81 | >=80% |  |
| M2b_1946_1987_stronger_claim_ready | fail | all_time_bins_ge_20 | {'1960-1969': 19, '1970-1979': 34, '1980-1987': 38, '1946-1959': 18} | all four >=20 |  |
| M3_1987_2015_exploratory_ready | fail | usable_1987_2015 | 12 | >=400 |  |
| M3_1987_2015_exploratory_ready | fail | mainland_corridors_ge_50 | {'Taiwan-side': 5, 'Yangtze River Delta': 4, 'North China': 3} | >=3 corridors |  |
| M3_1987_2015_exploratory_ready | fail | time_bins_ge_100 | {'1988-1995': 1, '1996-2005': 5, '2006-2014': 6} | >=2 bins |  |
| M4_platform_reference_ready | fail | target_merchants | 0 | >=60 |  |
| M4_platform_reference_ready | fail | control_a_merchants | 0 | >=30 |  |
| M4_platform_reference_ready | fail | control_b_merchants | 0 | >=30 |  |
| M4_platform_reference_ready | fail | reviews | 0 | >=800 |  |
| M4_platform_reference_ready | fail | platform_ownership_matching_rate | 0.00 | >=40% |  |

## Interpretation

- A failed milestone does not stop writing entirely; it limits what kind of claims can be written.
- If M2 passes but M2b fails, the 1946-1987 chapter should be explicitly exploratory.
- If M3 fails after sustained collection, downgrade 1987-2015 to a transition/case-discussion layer.
