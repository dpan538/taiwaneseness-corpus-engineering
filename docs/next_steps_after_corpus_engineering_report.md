# Next Steps After the Corpus Engineering Report

## Position

The report confirms that the project is still in evidence-building mode. The current corpus can support method design and source-gap diagnosis, but it cannot support quantitative historical claims about diffusion, regional comparison, ownership shift, or consumer reinterpretation.

The next stage should stop prioritizing hand-curated examples and instead build a reproducible evidence warehouse:

1. source registry;
2. search logs, including negative searches;
3. raw capture manifests;
4. extracted candidate windows;
5. deduped attestations;
6. ownership/capital events;
7. merchant/review platform records;
8. corpus-health audit and claim-permission flags.

## What the Report Adds

The strongest additions are:

- It keeps `dish_marker` and `taiwan_marker` separate and treats their attachment as the object of measurement.
- It separates historical archive evidence from post-2015 platform evidence at ingest time.
- It requires negative-search logging for Korea, Vietnam, Latin America, and other thin corridors.
- It introduces a source-first warehouse with raw artifacts and capture manifests.
- It gives a clear health rubric: the current project is Grade D until the main phases reach at least Grade C.
- It proposes separate historical and platform binding indices, which prevents platform-era data from contaminating long-run historical claims.

## Immediate Repo Gap

The current repo already has useful pilot scripts:

- `scripts/merge_attestation_tables.py`
- `scripts/audit_macro_coverage.py`
- `scripts/audit_formation_quota_1946_1987.py`
- `scripts/harvest_tcmb_1946_1987.py`
- `scripts/score_taiwaneseness.py`
- `scripts/analyze_geo_historical_semantics.py`

But the current templates are too thin for the report's warehouse model. The next implementation should create canonical tables rather than continuing to append ad hoc batch files.

## Phase 1: Standardize the Warehouse

Goal: make every future record traceable from source to search to raw artifact to extracted attestation.

Create or replace these canonical files:

- `configs/source_seeds.yml`
- `configs/keywords.yml`
- `configs/search_matrix.csv`
- `configs/corridors.yml`
- `configs/geo_aliases.csv`
- `data/source_registry.csv`
- `data/archive_search_log.csv`
- `data/negative_searches.csv`
- `data/attestations.csv`
- `raw/manifests/raw_capture_manifest.jsonl`

First scripts to implement:

1. `scripts/build_source_registry.py`
2. `scripts/audit_corpus_health.py`
3. `scripts/dedupe_attestations.py`
4. `scripts/extract_attestations.py`

Why these first: without source IDs, health gates, and dedupe rules, more scraping will only make the corpus larger but not healthier.

## Phase 2: Convert Existing Evidence

Goal: preserve our current work but move it into the stricter schema.

Tasks:

- Map all current harvested CSV files into `data/attestations.csv`.
- Generate deterministic `source_id`, `search_id`, and `dedupe_key` values.
- Mark rows without a search log as `legacy_manual_harvest`.
- Create `negative_searches.csv` rows for documented failed/zero-yield searches, especially TCMB and under-covered overseas corridors.
- Re-run the health audit.

Expected result: the corpus will still grade low, but it will become auditable.

## Phase 3: Build High-Yield Historical Adapters

Priority order:

1. Taiwan newspaper and archive layer:
   - UDNData, China Times/TBMC, NTL holdings, Taiwan Memory, TCMB, Taiwan Historica, NAA.
   - This is the fastest path to filling 1946-1987 Taiwan-side quotas.

2. NewspaperSG:
   - Continue systematic searches for `Taiwan porridge`, `Taiwanese porridge`, `Taiwan restaurant`, `Formosa restaurant`.
   - Singapore is already comparatively healthy, but can provide a strong overseas comparison if deduped correctly.

3. Japan:
   - NDL, NDL Search, WARP, Tokyo Archive, ADEAC.
   - Search `台湾料理`, `ルーローハン`, `魯肉飯`, and separate `台湾ラーメン` as a translation/control category.

4. Mainland 1987-2015:
   - People's Daily, local press where accessible, GSXT, CNIPA, franchise/chain portals.
   - Start with Shanghai/YRD, Fujian/southeast, PRD, Beijing/North, inland.

5. Platform corpus:
   - Dianping/Meituan merchant panel for 10 cities.
   - Keep this as a separate 2015-2025 corpus with platform-bias flags.

## Phase 4: Ownership and Capital Layer

Ownership work should not wait until the end. For every mainland or platform-era brand, collect:

- operating company;
- registration year;
- trademark class 29/30/43 records where available;
- founder or capital-origin evidence;
- franchise language;
- first observed mainland city;
- whether Taiwan origin is verified, probable, themed, or unknown.

Claims about Taiwan capital vs mainland Taiwan-themed operation remain forbidden until ownership completeness exceeds 60%.

## Phase 5: Corpus Health Gates

Adopt the report's gate logic:

- Grade A: inference-ready.
- Grade B: limited inference-ready.
- Grade C: pilot/statistical exploration only.
- Grade D: evidence-building only.
- Grade F: unusable.

Machine flags to emit:

- `can_make_macro_historical_claims`
- `can_compare_regions`
- `can_compare_periods`
- `can_analyze_ownership_shift`
- `can_analyze_platformization`
- `can_publish_quantitative_tables`

Current expected status:

```json
{
  "can_make_macro_historical_claims": false,
  "can_compare_regions": false,
  "can_compare_periods": false,
  "can_analyze_ownership_shift": false,
  "can_analyze_platformization": false,
  "can_publish_quantitative_tables": false
}
```

Additional experimental-design gates:

- Without `control_same_dish_no_taiwan` and `control_taiwan_other_dish` groups, do not claim Taiwan markers are specific to Taiwanese lu rou fan.
- Without consumer stance categories, do not claim consumers reproduce, transform, or reject merchant-produced Taiwaneseness.
- Without repeated captures, do not claim platform labels are stable over time.
- Without ownership attempts, do not claim a merchant's Taiwaneseness is Taiwan-capital, mainland-themed, or franchise-driven.

## Immediate 7-Day Plan

Day 1:
- Build `configs/keywords.yml`, `configs/corridors.yml`, and `configs/source_seeds.yml`.
- Implement `scripts/build_source_registry.py`.

Day 2:
- Create canonical `data/source_registry.csv`.
- Implement `scripts/audit_corpus_health.py` with the report's score and hard gates.

Day 3:
- Implement conversion from current harvested CSVs into canonical `data/attestations.csv`.
- Generate `source_id`, `search_id`, and `dedupe_key`.

Day 4:
- Implement `scripts/dedupe_attestations.py`.
- Label duplicate ads, repeated pages, legacy manual batches, and candidate-only rows.

Day 5:
- Implement `scripts/extract_attestations.py` for raw text windows.
- Add unit-testable skeletons for `scripts/ocr_enhanced.py` and `scripts/platform_capture_wrapper.py`.
- Keep platform capture compliant: no proxy-rotation evasion, CAPTCHA bypass, or mass extraction behind prohibited login walls.
- Add `scripts/control_group_sampler.py` to create target and control merchant samples from already captured platform records.

Day 6:
- Build a dry-run search matrix for Taiwan archives, NewspaperSG, NDL/Japan, People's Daily, and Latin America/Korea/Vietnam negative-search targets.
- Add dry-run checks for `scripts/detect_translation_drift.py` and `scripts/align_trademark_vs_menu.py`.
- Add dry-run checks for `scripts/consumer_stance_classifier.py`, `scripts/longitudinal_diff.py`, and `scripts/ownership_heuristic_classifier.py`.

Day 7:
- Run the health audit.
- Produce `reports/corpus_health.md`.
- Add drift-coverage, trademark-alignment coverage, platform-capture health, and ownership-classifier trace-rate checks.
- Decide which adapters deserve live harvesting first.

## Decision

The next technical milestone should be:

> Convert the project from a batch-harvested seed corpus into a canonical, auditable evidence warehouse with health gates.

Only after that should we resume large-scale scraping. Otherwise, reaching 700 rows may create volume without research credibility.
