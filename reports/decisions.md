# Pipeline Decisions Log

Use this file to record decisions after alerts. The point is not bureaucracy;
it is to prevent silent data pollution and make exclusions or strategy changes
auditable.

## 2026-06-03

- **Alert**: Writing milestones and stop rules added to the project.
- **Source / batch**: Project-level research design.
- **Decision**: Link corpus thresholds directly to paper sections. Methods can be drafted before analysis, but historical claims require the milestone checks in `docs/writing_milestones_and_stop_rules.md`.
- **Reason**: The project needs explicit stop rules for collection and clear rules for when each paper section can be written.
- **Action taken**: Added `scripts/check_writing_milestones.py` and will run it alongside the weekly health audit.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: Literature review and publication strategy incorporated.
- **Source / batch**: Project-level writing strategy.
- **Decision**: Keep an English-first literature and journal strategy file, plus lightweight registries for references and journal targets.
- **Reason**: The thesis needs a stable theoretical and methodological spine before the data are fully collected; however, bibliographic details and journal metrics must be re-verified before submission.
- **Action taken**: Added `docs/literature_review_and_publication_strategy.md`, `data/literature_registry.csv`, and `data/journal_targets.csv`.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: First information-harvesting checkpoint completed after repository publication.
- **Source / batch**: `HARVEST_011` plus archive-search and negative-search setup.
- **Decision**: Treat the current corpus as a collection checkpoint, not an inference-ready dataset. The 1946-1987 layer has 113 usable records, which is enough to guide targeted harvesting but not enough for exploratory historical analysis under the project thresholds.
- **Reason**: The audit shows strong verification quality (94.96%) and improved method infrastructure, but the historical layer remains far below the 350-record exploratory threshold and the 600-record stronger-claim threshold. Taipei, Tainan, and Kaohsiung local quotas remain underfilled.
- **Action taken**: Generated 1,008 archive-search instructions, registered 29 source targets, logged negative-search effort for Korea, Vietnam, and Latin America, added a four-record Tainan batch, rebuilt `combined_attestations_working.csv`, and reran macro, formation-quota, corpus-health, writing-milestone, and binding-index audits.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: Southern Taiwan early-bin top-up changed the temporal-balance status.
- **Source / batch**: `HARVEST_012`.
- **Decision**: Mark the 1946-1987 internal time-bin distribution as provisionally balanced for exploratory planning, while keeping the full historical layer blocked for analysis because total usable records remain far below threshold.
- **Reason**: The top-up batch raised the 1946-1959 bin from 19 to 22 usable records, so all four 1946-1987 bins now have at least 20 records. However, the 1946-1987 layer has only 116 usable records against the 350 exploratory threshold and 600 stronger-claim threshold.
- **Action taken**: Added three southern market/old-shop records from Kaohsiung Travel, TVBS Food Player, and TaiwanFoodie; rebuilt the combined corpus; reran macro, formation-quota, health, writing-milestone, and binding-index audits.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: Taipei-focused public-web harvest moved the Taipei city quota close to threshold.
- **Source / batch**: `HARVEST_013`.
- **Decision**: Keep using public web sources for short targeted top-ups, but treat them as gap-filling evidence rather than the core historical proof layer. With Taipei now passing the city threshold, shift the next public-web sweep back to Tainan and Kaohsiung.
- **Reason**: The batch raised 1946-1987 usable records from 116 to 128, Taipei records from 22 to 30, and Kaohsiung records from 20 to 24. However, the corpus remains far below the 350-record exploratory threshold and still depends heavily on retrospective public-web sources.
- **Action taken**: Added 14 records in `data/harvested/taipei_southern_old_shop_batch_1946_1987_20260603_c.csv`, rebuilt the working corpus, and reran macro, formation-quota, health, writing-milestone, and binding-index audits. Two weaker rows remain candidate-level.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: Southern public-web top-up added non-duplicate Tainan and Kaohsiung old-shop evidence.
- **Source / batch**: `HARVEST_014`.
- **Decision**: Continue small source-grounded southern top-ups, but mark relative-date rows conservatively and do not duplicate prior shop/year/source attestations.
- **Reason**: Tainan remains far below the city threshold and Kaohsiung remains short of threshold. The batch adds two Tainan records and one usable Kaohsiung record, while retaining one Kaohsiung relative-date row as candidate until a firmer founding source is found.
- **Action taken**: Added four records in `data/harvested/tainan_kaohsiung_public_web_topup_1946_1987_20260603_d.csv`, appended them to the working corpus, fixed a pre-existing duplicate `attestation_id` for the Changhua Black Meat Noodles row, and reran macro, formation-quota, health, writing-milestone, and binding-index audits.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: Second southern top-up brought Kaohsiung to the city threshold while Tainan remains short.
- **Source / batch**: `HARVEST_015`.
- **Decision**: Treat Kaohsiung city coverage as provisionally threshold-complete for planning, and shift the next southern public-web pass mainly toward Tainan until it reaches 30 records.
- **Reason**: The batch added non-duplicate Tainan and Kaohsiung corroboration/ecology rows. Kaohsiung reached 30 records, while Tainan rose to 15 records and remains below threshold.
- **Action taken**: Added 11 records in `data/harvested/tainan_kaohsiung_public_web_topup_1946_1987_20260603_e.csv`, appended them to the working corpus, reran lightweight audits, verified CSV parsing, and checked duplicate `attestation_id` plus duplicate source/brand/year/type keys.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: City thresholds are provisionally complete, but the 1946-1987 layer remains far below the exploratory record threshold.
- **Source / batch**: `HARVEST_018`.
- **Decision**: Shift manual top-ups away from Tainan-only collection toward late-formation Taiwan-side records and overseas corridor evidence, while marking approximate retrospective dates as candidates.
- **Reason**: Taipei, Tainan, and Kaohsiung have all reached the city threshold, but `usable_1946_1987` remains blocked. The weakest active quota areas include late Taiwan-side years, North America, Japan, Singapore, and mainland China.
- **Action taken**: Added four non-duplicate records in `data/harvested/late_formation_corridor_topup_1946_1987_20260603_h.csv`, appended them to the working corpus, and upgraded the existing Yumama old noodle shop row from candidate to probable after recapturing the ROC-year source line.
- **Responsible reviewer**: project researcher.

## 2026-06-03

- **Alert**: North America remains under quota and Mainland China remains especially thin, but some mainland food-route evidence is weakly sourced.
- **Source / batch**: `HARVEST_019`.
- **Decision**: Add strong North America corridor records as probable, but retain the Mr Lee Beijing 1987 returnee-chain row as candidate until a better biography or contemporaneous source confirms the Taiwan migration link.
- **Reason**: The 99 Ranch official history and Los Angeles Times archive sources are direct enough for probable corridor evidence. The Mr Lee official page supports California origin and 1987 Beijing opening, but the Taiwan route is currently dependent on a weaker secondary capture.
- **Action taken**: Added four records in `data/harvested/north_america_mainland_corridor_topup_1946_1987_20260603_i.csv`, appended them to the working corpus, and prepared the batch for lightweight audit validation.
- **Responsible reviewer**: project researcher.

## Template

```markdown
## YYYY-MM-DD

- **Alert**:
- **Source / batch**:
- **Decision**:
- **Reason**:
- **Action taken**:
- **Responsible reviewer**:
```
