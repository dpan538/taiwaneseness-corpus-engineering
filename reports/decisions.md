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
