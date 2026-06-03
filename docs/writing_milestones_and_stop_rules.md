# Writing Milestones and Stop Rules

## Purpose

This project links data collection directly to thesis production. The question is not only "How much data can we collect?" but also "Which parts of the paper are now defensible enough to write?"

The corpus should therefore use explicit acceptance criteria:

- when a section may be drafted;
- when a section may make only exploratory claims;
- when a section may make stronger inferential claims;
- when a phase should be downgraded or abandoned as an independent chapter.

## Paper Sections and Data Requirements

| Paper section | Can start when | Evidence requirement |
|---|---|---|
| Introduction | now | no corpus threshold |
| Literature review | now | no corpus threshold |
| Method / corpus construction | Milestone 1 | source registry, manifest, negative searches, health audit |
| Historical semantic evolution, 1946-1987 | Milestone 2 | enough Taiwan-side historical records for exploratory analysis |
| Cross-strait diffusion, 1987-2015 | Milestone 3 | enough mainland/cross-strait records, or downgrade to limited cases |
| Platform/capital layer, 2015-2025 | Milestone 4 | modern platform/control sample, exploratory only unless scaled |
| Discussion/conclusion | after at least one analysis chapter is complete | depends on which claim flags are true |

## Milestone 1: Corpus Is Auditable

Method section can be written when:

- `data/source_registry.csv` has at least 15 source records.
- `raw/manifests/raw_capture_manifest.jsonl` has at least 50 raw-capture records.
- `data/negative_searches.csv` includes Korea, Vietnam, and Latin America, at least one row each.
- `scripts/audit_corpus_health.py` runs successfully and produces:
  - `reports/corpus_health.md`;
  - `reports/corpus_health.csv`;
  - `reports/claim_flags.json`.

Allowed writing:

- corpus design;
- source-family map;
- limitation statement;
- reproducibility workflow.

Forbidden:

- historical claims;
- regional absence claims without negative-search logs.

## Milestone 2: 1946-1987 Historical Layer Is Exploratory-Ready

Exploratory historical analysis can be written when:

- 1946-1987 usable records >= 350.
- verified/probable share >= 60%.
- at least three internal bins have >= 20 usable records:
  - 1946-1959;
  - 1960-1969;
  - 1970-1979;
  - 1980-1987.
- Taipei, Tainan, and Kaohsiung each have >= 30 usable records, or the shortfall is explicitly reported.

Allowed writing:

- descriptive analysis of collected records;
- source-type comparison;
- cautious discussion of binding patterns within the observed corpus.

Forbidden:

- strong frequency claims;
- claims of complete historical evolution;
- strong regional comparison if city quotas are not met.

## Milestone 2b: 1946-1987 Historical Layer Is Stronger-Claim Ready

Stronger historical claims require:

- 1946-1987 usable records >= 600.
- verified/probable share >= 80%.
- all four internal bins have >= 20 usable records.
- major Taiwan-side city coverage is documented.
- dedupe and negative-search audits pass.

If this is not reached, the chapter should be framed as an exploratory corpus analysis.

## Milestone 3: 1987-2015 Mobility Layer

Exploratory cross-strait diffusion analysis can be written when:

- 1987-2015 usable records >= 400.
- at least three mainland corridors have >= 50 records each:
  - YRD;
  - southeast/Fujian;
  - PRD;
  - North;
  - inland.
- at least two time bins have >= 100 records:
  - 1988-1995;
  - 1996-2005;
  - 2006-2014.

Downgrade rule:

- If after two additional collection weeks, 1987-2015 adds fewer than 10 usable records per week, this layer should not be an independent analysis chapter.
- Instead, use it as limited transition evidence in the discussion.

## Milestone 4: Platform/Capital Layer as Contemporary Reference

The platform layer should be a contemporary comparison, not the historical core.

Exploratory platform chapter can be written when:

- target merchants >= 60;
- control group A >= 30;
- control group B >= 30;
- reviews >= 800;
- ownership matching rate >= 40%;
- platform-generated fields are separated from merchant-provided and consumer-generated fields.

Large journal-level platform design, if pursued:

- target group: 480 merchants;
- control A: 320 merchants;
- control B: 320 merchants;
- total: about 1,120 merchants.

For the current project, the reduced exploratory platform design is preferred unless the thesis is recentered on modern platform discourse.

## Stop Rules

### 1946-1987

If three consecutive weeks add fewer than 20 verified/probable records per week:

- decide whether to add new archive sources, such as offline library scans;
- or accept the current corpus and frame the chapter as exploratory.

### 1987-2015

If two consecutive weeks add fewer than 10 verified/probable records per week:

- downgrade the phase to a limited case-study/discussion layer;
- do not promise a standalone diffusion chapter.

### Platform Layer

If platform capture is blocked or ownership matching remains below 40%:

- keep the layer as a short exploratory comparison;
- avoid statistical inference or ownership-shift claims.

## Weekly Review Routine

Every week:

1. Merge and dedupe the latest records.
2. Run `scripts/audit_corpus_health.py`.
3. Run `scripts/check_writing_milestones.py`.
4. Review `reports/alerts.jsonl`.
5. Record decisions in `reports/decisions.md`.

The key weekly numbers are:

- 1946-1987 usable records;
- verified/probable share;
- temporal-bin coverage;
- city coverage;
- 1987-2015 usable records;
- ownership matching rate;
- negative-search effort.

## Working Principle

Do not wait for perfect coverage to write. Start writing sections whose evidence gates are satisfied, and explicitly label sections that remain exploratory. The project is strongest when its claims are calibrated to its corpus health.

