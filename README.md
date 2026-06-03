# Taiwaneseness Corpus Engineering

This repository hosts the data pipeline, corpus schemas, and audit tools for the research project:

**"Taiwaneseness as a Consumed Cultural Sign: A Geo-Historical Semantic Analysis of Lu Rou Fan across Publication Systems, Ownership Regimes, and Platform Logics (1940-2025)."**

## Research Object

This project does not ask whether any bowl of lu rou fan is "truly" Taiwanese. It studies when, where, and by whom **Taiwan markers** become attached to **dish markers** such as lu rou fan, rouzao rice, and braised pork rice.

The central premise is methodological:

> `dish_marker` and `taiwan_marker` must be stored separately before their attachment can be measured.

## Core Design Principles

- **Separate `dish_marker` and `taiwan_marker`**: their attachment is the object of measurement, not an assumption.
- **Phase-segregated evidence layers**:
  - `1940-1945`: contextual archive layer
  - `1946-1987`: historical attestation layer
  - `1987-2015`: mobility/diffusion layer
  - `2015-2025`: platform/capital layer
- **Negative-search logging**: absent corridors such as Vietnam, Korea, and Latin America must be explicitly searched and logged, not silently omitted.
- **Auditable warehouse**: every attestation should trace back to a source record, a search log, and, where permitted, a raw artifact or archive reference.
- **Derived tables never overwrite originals**: normalization, verification, deduplication, and scoring create new columns or output tables.
- **Health-based gatekeeping**: corpus health scores and claim flags decide which inferences are permitted at each stage.
- **Platform evidence is phase-separated**: post-2015 platform visibility is treated as platform-mediated evidence, not directly comparable to pre-internet archives.

## Repository Structure

```text
config/      Lexicons, period definitions, and alert thresholds
data/        Seed tables, templates, harvested working CSVs, and registries
docs/        Research design, corpus protocol, stop rules, and publication strategy
outputs/     Earlier pilot outputs and exploratory summaries
reports/     Current health audits, claim flags, alerts, and writing milestones
scripts/     Harvesting, extraction, scoring, audit, and monitoring scripts
```

Raw captures, OCR output, platform cookies, and private Word drafts are intentionally excluded from version control.

## Key Tables

- `data/source_registry_template.csv`: source registry template for archives, APIs, platforms, and access metadata.
- `data/harvested/combined_attestations_working.csv`: current working attestation table.
- `data/formation_1946_1987_quota_plan.csv`: detailed quota plan for the first historical phase.
- `data/macro_collection_plan.csv`: macro phase targets.
- `data/literature_registry.csv`: literature-review tracking table.
- `data/journal_targets.csv`: publication-target tracking table.

Expected canonical tables for the next collection phase:

- `data/source_registry.csv`
- `data/archive_search_log.csv`
- `data/negative_searches.csv`
- `data/attestations.csv`
- `data/ownership_capital_events.csv`
- `data/merchant_platform_records.csv`
- `data/consumer_reviews.csv`

## Key Outputs

- `reports/corpus_health.md`: current corpus health report.
- `reports/claim_flags.json`: machine-readable claim-permission flags.
- `reports/corpus_temporal_distribution.csv`: internal time-bin distribution.
- `reports/negative_search_effort.csv`: documented negative-search coverage.
- `reports/writing_milestones.md`: which thesis/article sections are currently write-ready.
- `reports/binding/historical_binding_index.csv`: historical binding-index output.

## Scripts

Harvesting and collection planning:

- `scripts/harvest_taiwan_newspapers.py`: generate manual search/download instructions for restricted Taiwan newspaper archives.
- `scripts/harvest_tcmb_1946_1987.py`: harvest public TCMB open-data candidates.
- `scripts/harvest_tcmb_archive.py`: generic TCMB-style JSON manifesting wrapper.
- `scripts/negative_search_logger.py`: append documented zero-yield searches.

OCR and extraction:

- `scripts/ocr_newspaper_pdfs.py`: native PDF text extraction with optional PaddleOCR fallback.
- `scripts/extract_historical_attestations.py`: extract candidate windows from OCR/native text.
- `scripts/normalize_text.py`: normalize text for scoring.

Analysis and audit:

- `scripts/score_taiwaneseness.py`: lexicon scoring for merchant/review texts.
- `scripts/score_historical_binding.py`: compute lexical, branding, ownership, and historical binding indices.
- `scripts/audit_corpus_health.py`: health score, audit tables, alerts, and claim flags.
- `scripts/check_writing_milestones.py`: map corpus status to thesis/article writing readiness.
- `scripts/watch_pipeline.py`: print unresolved pipeline alerts.

Experimental design support:

- `scripts/control_group_sampler.py`: sample target and control merchant groups.
- `scripts/consumer_stance_classifier.py`: classify review stance toward Taiwan markers.
- `scripts/longitudinal_diff.py`: compare repeated platform captures.
- `scripts/ownership_heuristic_classifier.py`: rule-based ownership triage with evidence traces.

## Quick Start

Run the current health audit:

```bash
python3 scripts/audit_corpus_health.py \
  --attestations data/harvested/combined_attestations_working.csv \
  --negative data/negative_searches.csv \
  --ownership data/capital_event_seed_2015_2025.csv \
  --out-csv reports/corpus_health.csv \
  --out-md reports/corpus_health.md \
  --out-flags reports/claim_flags.json
```

Check writing milestones:

```bash
python3 scripts/check_writing_milestones.py \
  --attestations data/harvested/combined_attestations_working.csv \
  --out-csv reports/writing_milestones.csv \
  --out-md reports/writing_milestones.md
```

Check unresolved alerts:

```bash
python3 scripts/watch_pipeline.py --alerts reports/alerts.jsonl
```

Generate manual archive search instructions:

```bash
python3 scripts/harvest_taiwan_newspapers.py \
  --year-start 1946 \
  --year-end 1987 \
  --keywords "魯肉飯,滷肉飯,肉燥飯,肉臊飯"
```

## Current Corpus Status

The current corpus is a methods-and-design baseline, not an inference-ready historical corpus.

At the latest audit:

- `1946-1987` coverage remains below the exploratory threshold.
- `1987-2015` and `2015-2025` are not yet analysis-ready.
- all major claim flags remain `false`.

This is intentional: the project uses explicit health gates to prevent premature claims.

## Writing and Publication Strategy

The project is designed to support a master's thesis and, if corpus health permits, one or more journal submissions.

Potential outputs:

1. A methodology paper on corpus engineering, health auditing, and marker-binding measurement for historical food semantics.
2. An empirical cultural-analysis paper on Taiwaneseness as a cross-border consumable sign in food discourse.

Potential target venues include *Food and Foodways*, *Asian Journal of Social Science*, *International Journal of Humanities and Arts Computing*, and digital humanities venues. See `docs/literature_review_and_publication_strategy.md`.

## Data Ethics and Access

Some sources are restricted, subscription-based, or platform-governed. This repository does not include private cookies, login credentials, restricted raw captures, or prohibited platform exports.

For platform or review data:

- store only what access terms permit;
- anonymize consumer identifiers before publication;
- separate merchant-provided, platform-generated, and consumer-generated fields;
- report capture dates, access methods, and platform-bias limits.

## License

Recommended licensing model:

- Code: MIT License.
- Documentation and shareable metadata: CC BY-NC 4.0.
- Raw copyrighted source captures: not redistributed.

Final licensing should be confirmed before public release of any full corpus snapshot.

## Citation

If you use this corpus design or pipeline, please cite:

> Pan, D. *Corpus Engineering for the Geo-Historical Semantics of Taiwaneseness*. GitHub repository, 2026. https://github.com/dpan538/taiwaneseness-corpus-engineering

