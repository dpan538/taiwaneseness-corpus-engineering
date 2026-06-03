# Script Addendum from User Notes

## Purpose

This addendum incorporates the four implementation directions proposed after reading the corpus-engineering report:

1. platform collection wrapper and crawl health monitoring;
2. enhanced OCR for historical newspapers and PDFs;
3. translation-drift detection for overseas corridors;
4. trademark/menu timeline alignment, consumer reproduction rate, and finer ownership classification.

These additions are valuable because they turn the main hypotheses into executable modules:

- H2/H3: ownership and trademark timing versus menu/attestation timing;
- H4: consumer reproduction of merchant-provided Taiwan markers;
- H7: overseas translation drift and false binding;
- platform phase: post-2015 merchant/review corpus with explicit health and bias controls.

## Compliance Adjustment

The platform-crawling proposal should be implemented as a compliant capture wrapper, not as an anti-bot evasion tool.

Allowed:

- user-provided logged-in browser contexts when the user has access rights;
- slow rate limits and randomized pauses for load reduction;
- dry-run mode;
- crawl-status logging: `captured`, `partial`, `blocked`, `login_required`, `terms_blocked`, `manual_only`;
- platform terms/robots notes in `source_registry.csv`;
- manual capture and screenshots where automation is not permitted;
- official APIs or merchant exports when available.

Not allowed for the research pipeline:

- proxy rotation for evasion;
- CAPTCHA bypass;
- stealth plugins intended to defeat platform detection;
- mass scraping behind login walls when terms prohibit automated extraction;
- treating blocked pages as absence.

The correct research behavior is to log blocked or manual-only sources and preserve the bias as metadata.

## New Script Priority

### 0. `scripts/control_group_sampler.py`

Responsibilities:

- sample the main target group: Taiwan-marked lu rou fan merchants;
- sample same-dish/no-Taiwan controls;
- sample same-Taiwan/different-dish controls;
- output balanced city-by-group samples;
- report whether a city lacks enough cases for comparison.

Interpretive rule:

- If this script cannot produce control groups, Taiwan-marker specificity claims are forbidden.

### 1. `scripts/platform_capture_wrapper.py`

Renamed from `platform_crawl_wrapper.py` to emphasize compliant capture rather than evasion.

Responsibilities:

- accept platform, city list, keyword list, page limit, and output path;
- support dry-run mode;
- load user-provided cookies only from a local path excluded from version control;
- capture merchant cards only where access is permitted;
- write merchant rows to `data/merchant_platform_records.csv`;
- write failures to `reports/platform_capture_health.csv`;
- never silently drop failures.

Minimum CLI:

```bash
python scripts/platform_capture_wrapper.py \
  --platform dianping \
  --cities Shanghai,Shenzhen,Beijing \
  --keywords "台湾卤肉饭,台式卤肉饭" \
  --page-limit 3 \
  --out data/merchant_platform_records.csv \
  --health reports/platform_capture_health.csv \
  --dry-run
```

Required health fields:

- `run_id`
- `platform`
- `city`
- `keyword`
- `page_num`
- `status`
- `http_status`
- `records_found`
- `error_class`
- `error_message`
- `capture_time`
- `terms_notes`

### 2. `scripts/ocr_enhanced.py`

Responsibilities:

- process files listed in `raw/manifests/raw_capture_manifest.jsonl`;
- try embedded text first;
- use layout-aware OCR for scanned pages;
- store page-level OCR confidence;
- output a schema-compatible `raw/ocr/ocr_pages.jsonl`.

Preferred engines:

- PaddleOCR or EasyOCR for Chinese/Japanese newspaper scans when installed;
- Tesseract as fallback;
- native PDF text via `pdfplumber` before OCR.

Required output fields:

- `capture_id`
- `source_id`
- `page_num`
- `engine`
- `ocr_text`
- `ocr_confidence_mean`
- `layout_notes`
- `status`

### 3. `scripts/detect_translation_drift.py`

Responsibilities:

- inspect non-Chinese attestations and reviews;
- detect whether a Taiwan marker is attached to lu rou fan, another Taiwanese dish, a restaurant category, or an unrelated travel/news context;
- output `reports/translation_drift_report.csv`.

Avoid overreliance on online translation APIs. The first version should use marker dictionaries and multilingual sentence embeddings. Back-translation can be optional because it introduces external dependency, cost, instability, and privacy concerns.

Required classification labels:

- `no_drift`
- `dish_shift`
- `category_shift`
- `travel_context`
- `restaurant_only`
- `uncertain`

### 4. `scripts/align_trademark_vs_menu.py`

Responsibilities:

- join `data/trademarks.csv`, `data/attestations.csv`, and optionally `data/ownership_capital_events.csv`;
- find earliest menu/ad/platform attestation per brand;
- compare first menu evidence with trademark filing/registration date;
- output `reports/timeline_misalignment.csv`.

Core labels:

- `menu_before_trademark`
- `trademark_before_menu`
- `same_year`
- `no_menu_found`
- `no_trademark_found`
- `insufficient_date`

Interpretive use:

- `menu_before_trademark` may suggest cultural/restaurant usage before formal capital protection;
- `trademark_before_menu` may suggest capital/franchise preparation before visible menu diffusion;
- neither label proves causality without source corroboration.

### 5. `scripts/consumer_reproduction_rate.py`

Responsibilities:

- extract merchant-side Taiwan markers from `shop_name`, `platform_tags`, `menu_item_names`, and `merchant_description`;
- measure whether reviews reproduce the same markers;
- output `reports/consumer_reproduction_rates.csv`.

Recommended metrics:

- `merchant_marker_count`
- `review_count`
- `reviews_with_any_merchant_marker`
- `reproduction_rate`
- `avg_marker_mentions_per_review`
- `dish_marker_review_rate`
- `taiwan_marker_review_rate`
- `consumer_reinterpretation_gap`

### 5b. `scripts/consumer_stance_classifier.py`

Responsibilities:

- classify reviews into five stance categories:
  - `0 = no Taiwan mention`;
  - `1 = reproduces merchant Taiwan markers`;
  - `2 = adds new Taiwan markers`;
  - `3 = shifts Taiwan markers to non-food attributes`;
  - `4 = rejects or contests Taiwan authenticity`;
- output review-level classifications and merchant-level rates:
  - no-mention rate;
  - reproduction rate;
  - transformation rate;
  - rejection rate.

Interpretive rule:

- The older overlap-only Consumer Reinterpretation Gap should be treated as a coarse pilot metric. Publication-facing claims should use stance categories.

### 5c. `scripts/longitudinal_diff.py`

Responsibilities:

- compare repeated captures for the same merchant;
- detect changes in shop name, descriptions, platform tags, menu items, recommended dishes, and Taiwan marker density;
- output marker deltas by capture pair.

Interpretive rule:

- If a merchant has only one capture point, claims about platform-label stability are forbidden.

### 6. `scripts/ownership_heuristic_classifier.py`

Responsibilities:

- classify ownership category using registry, trademark, shareholder, founder, and address evidence;
- produce a category plus confidence and rule trace.

Important correction:

Do not use common Chinese surnames as evidence of Taiwan capital. Surnames such as Chen, Lin, Huang, Zhang, Li, Wang, Wu, and Cai are not discriminative enough and would create serious false positives.

Better signals:

- official Taiwan registration address or Taiwan company applicant;
- founder biography explicitly tied to Taiwan;
- trademark applicant based in Taiwan;
- cross-strait joint venture documents;
- franchise text claiming Taiwan-headquartered operation;
- Hong Kong/BVI/Cayman as a weak intermediary clue only when corroborated.

Output fields:

- `brand`
- `operating_company`
- `ownership_category`
- `confidence`
- `rules_fired`
- `evidence_text`
- `source_id`

## Health Audit Additions

Add these components to `scripts/audit_corpus_health.py`, but do not over-weight platform crawl success in the historical corpus grade.

New metrics:

- `translation_drift_coverage`
  - share of non-Chinese/non-Taiwan-side records checked by drift detector.

- `trademark_alignment_coverage`
  - share of brands with either a trademark record, a negative trademark search, or an explicit not-applicable label.

- `platform_capture_success_rate`
  - successful capture runs divided by attempted platform runs, reported only for the 2015-2025 platform corpus.

- `platform_blocked_rate`
  - blocked or login-required runs divided by attempted platform runs.

- `ownership_classifier_trace_rate`
  - share of ownership classifications with machine-readable `rules_fired`.

Hard gates:

- If translation-drift coverage is below 70% for overseas records, overseas semantic comparison is forbidden.
- If trademark-alignment coverage is below 60% for mainland/platform brands, H2/H3 claims are forbidden.
- If consumer reproduction coverage is below 50 reviews per city or below 10 merchants per city, H4 city comparison is forbidden.
- If platform blocked rate exceeds 30%, platform findings must be labeled partial and non-representative.

## Revised 7-Day Plan

Day 1:
- Build canonical configs and `source_registry.csv`.
- Implement `scripts/build_source_registry.py`.

Day 2:
- Implement base `scripts/audit_corpus_health.py`.
- Add health flags before further scraping.

Day 3:
- Convert current harvested CSVs into canonical `data/attestations.csv`.
- Generate `source_id`, `search_id`, and `dedupe_key`.

Day 4:
- Implement `scripts/dedupe_attestations.py`.
- Label duplicate ads, repeated pages, legacy batches, and candidate-only rows.

Day 5:
- Implement unit-testable skeletons for:
  - `scripts/ocr_enhanced.py`;
  - `scripts/platform_capture_wrapper.py`.
- Implement `scripts/control_group_sampler.py`.

Day 6:
- Implement dry-run versions of:
  - `scripts/detect_translation_drift.py`;
  - `scripts/align_trademark_vs_menu.py`.
- Test `scripts/consumer_stance_classifier.py`, `scripts/longitudinal_diff.py`, and `scripts/ownership_heuristic_classifier.py` on sample CSVs.

Day 7:
- Extend health audit with:
  - drift coverage;
  - trademark alignment coverage;
  - platform capture health;
  - ownership classifier trace rate.
- Produce `reports/corpus_health.md` and claim-permission flags.

## Implementation Order

The order should be:

1. health audit;
2. canonical conversion;
3. dedupe;
4. OCR and extraction;
5. platform capture wrapper;
6. trademark/menu alignment;
7. consumer reproduction rate;
8. translation drift;
9. ownership classifier refinement.

Reason: if health gates and dedupe are delayed, later scripts will generate volume before the project knows whether the volume is usable.
