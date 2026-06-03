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
