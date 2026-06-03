# Reproducible Pilot Research Protocol

## 1. Research Position

This paper does not ask whether any given bowl of lu rou fan is "truly" Taiwanese. Its object is the long-run, geo-historical, and capital-mediated production of Taiwaneseness from 1940 to 2020. The central problem is how a dish label moves from Taiwan-side local-food discourse into mainland commercial geography, then becomes a place label, a brand label, and finally a pre-wanghong platform/retail sign whose meaning is shaped by ownership, capital origin, geography, and consumer interpretation.

The empirical design should be computational-first. Human coding should be used mainly for validation and error analysis, while the main measures should come from scripted data collection, scripted text normalization, scripted lexicon scoring, ownership/capital provenance coding, and reproducible period-region comparison.

Working thesis:

> In mainland China, "Taiwanese braised pork rice" does not simply reproduce a Taiwanese dish. Rather, it transforms Taiwaneseness into a consumable cultural sign through menu language, visual branding, platform representation, and consumer interpretation.

## 2. Pilot Scope

### Recommended Scope

- Cities: Shanghai, Beijing, and Chengdu.
- Period: 1940-2020 as the main analytical window; post-2020 sources should be used only as retrospective or contextual material.
- Platforms and sources: Dianping first; brand websites, franchise pages, media reports, and archived pages as supplementary merchant-side sources.
- Merchant sample: 20-30 shops or brand pages per city, for a total of 60-90 merchant cases.
- Review sample: up to 30 public reviews per merchant case, for a pilot corpus of roughly 1,800-2,700 reviews.

### Rationale

This scope is large enough to test whether the method works but small enough to finish. Shanghai preserves the strongest commercial and historical rationale; Beijing provides a high-visibility consumer market; Chengdu offers a non-Yangtze River Delta and non-coastal comparison case.

### Evidence Threshold

The current seed corpus is not large enough for inference. Findings-level claims require macro-phase coverage: at least 120 verified/probable records for 1946-1987, at least 120 verified/probable records for 1987-2015, and a separate 2015-2025 capital/platform event corpus. The scaling plan is documented in `docs/evidence_scaling_plan.md` and `docs/three_phase_corpus_design.md`.

Before any macro-level claim is treated as a finding, run:

```bash
python3 scripts/audit_macro_coverage.py \
  --attestations data/historical_geo_attestations_1940_2020_seed.csv \
  --capital-events data/capital_event_seed_2015_2025.csv \
  --plan data/macro_collection_plan.csv \
  --output-dir outputs/macro_audit_seed
```

If `outputs/macro_audit_seed/summary.csv` marks `macro_inference_ready` as `0`, the corpus is still in source-building mode.

## 3. Data Layers

### A. Spatial-Temporal Diffusion Layer

Goal: test whether mainland Taiwanese lu rou fan diffuses primarily through Shanghai/Yangtze River Delta circuits, broader coastal corridors, or inland platform expansion.

Suggested fields:

- `brand`
- `city`
- `province`
- `observation_date`
- `first_observed_year`
- `open_store_count`
- `planned_store_count`
- `source_url`
- `source_type`
- `status_basis`
- `confidence`

This layer is documented in `docs/spatial_diffusion_design.md`.

The current long-run mining pass is documented in `docs/longrun_1940_2020_mining_memo.md`.

### B. Capital and Ownership Layer

Goal: distinguish Taiwan capital, Taiwan-mainland joint ventures, Hong Kong intermediary branding, mainland Taiwan-themed operators, franchise/operator capital, and mall/platform wanghong economics.

Suggested fields:

- `brand`
- `operating_company`
- `founding_year`
- `founding_place`
- `founder_origin`
- `ownership_category`
- `capital_origin`
- `mainland_entry_year`
- `mainland_entry_city`
- `source_url`
- `evidence_text`
- `confidence`

This layer is documented in `docs/capital_ownership_design.md`.

### C. Historical-Semantic Layer

Goal: trace when and how Taiwan markers become attached to lu rou fan markers.

Suggested fields:

- `source_id`
- `source_type`: news / blog / recipe / academic / media_report / archive
- `date`
- `title`
- `url_or_archive_ref`
- `original_text`
- `normalized_text`
- `keyword_variant`
- `taiwan_marker_present`
- `lu_rou_fan_marker_present`

### D. Merchant-Staging Layer

Goal: analyze how merchants produce Taiwaneseness.

Suggested fields:

- `merchant_id`
- `city`
- `platform`
- `shop_name`
- `branch_name`
- `platform_tags`
- `merchant_description`
- `menu_item_names`
- `recommended_dishes`
- `visual_notes`: script, logo, color, night-market imagery, Taiwan map/landmark, vertical text
- `source_url`
- `capture_date`

### E. Consumer-Interpretation Layer

Goal: compare whether consumers reproduce, transform, ignore, or reject merchant-produced Taiwaneseness.

Suggested fields:

- `review_id`
- `merchant_id`
- `review_date`
- `rating`
- `review_text`
- `review_likes_or_votes`
- `platform`
- `capture_date`

## 4. Keyword Groups

### Dish Markers

- 卤肉饭
- 滷肉飯
- 魯肉飯
- 肉燥飯
- lu rou fan
- braised pork rice

### Taiwan Markers

- 台湾
- 台灣
- 台式
- 台味
- 宝岛
- 寶島
- 台湾小吃
- 台灣小吃
- 台湾夜市
- 台灣夜市
- 士林
- 眷村

### Authenticity Markers

- 正宗
- 地道
- 原汁原味
- 古法
- 手作
- 手工
- 老味道
- 传统
- 傳統

### Nostalgia Markers

- 古早味
- 小时候
- 童年
- 回忆
- 懷舊
- 老派
- 家常
- 妈妈味
- 阿嬷

### Platform Fast-Food Markers

- 一人食
- 套餐
- 性价比
- 便宜
- 实惠
- 出餐快
- 外卖
- 连锁
- 加盟
- 标准化

## 5. Indicators

### 5.1 Taiwan-Lu Rou Fan Binding Index

Purpose: measure the association between Taiwan markers and lu rou fan markers in a given time period, platform, city, or text collection.

Pilot version:

```text
Binding Index = number_of_texts_with_both_marker_types / number_of_texts_with_dish_marker
```

Possible expanded versions:

- pointwise mutual information
- log odds ratio
- collocation window analysis: whether a Taiwan marker appears within N tokens of a dish marker
- embedding-neighborhood similarity, only if the corpus becomes large enough

### 5.2 Taiwaneseness Lexicon Score

Purpose: measure the density of Taiwaneseness domains in a text.

```text
Taiwaneseness Score = weighted_count_of_taiwaneseness_terms / total_token_count
```

For the pilot, avoid overcomplicated weights. Start with domain-level density scores:

- `geographic_score`
- `nostalgia_score`
- `night_market_score`
- `authenticity_score`
- `platform_fast_food_score`

### 5.3 Consumer Reinterpretation Gap

Purpose: compare the semantic structure of merchant-produced Taiwaneseness with consumer-interpreted Taiwaneseness.

At the brand or shop level:

```text
Gap(domain) = merchant_domain_score - average_consumer_domain_score
```

Interpretation:

- Positive value: merchants emphasize this domain more than consumers do.
- Negative value: consumers emphasize this domain more than merchants do.
- Near zero: merchant staging and consumer interpretation are relatively aligned.

Keep the direction. Do not collapse the measure into absolute difference, because the direction is theoretically meaningful.

## 6. Automated Measurement and Validation

The core experiment should be automated:

1. collect source-logged merchant and review texts;
2. preserve original text and script;
3. normalize text with a documented script;
4. score texts with the versioned Taiwaneseness lexicon;
5. calculate binding and gap metrics with reproducible scripts.

The current script inventory is documented in `docs/computational_design.md`.

## 7. Human Validation Audit

### Gold Set

Code 10-15% of the corpus manually, but treat this as a validation audit rather than the main measurement procedure.

- Merchant texts: at least 60 units.
- Consumer reviews: at least 200 reviews.
- Ideally, each unit should be independently coded by two coders. If there is only one researcher, use two temporally separated coding rounds and record revisions.

### Validation Target

- Estimate false positives, false negatives, and ambiguous cases for each Taiwaneseness domain.
- If two coders are available, report Cohen's kappa or Krippendorff's alpha.
- If only one researcher is available, use two temporally separated audit rounds and report self-disagreement cases.
- Revise the lexicon only after documenting the first-round error profile.

### Required Ambiguity Log

Record ambiguous cases, especially:

- Whether "台式" is Taiwan-specific or a generalized style label.
- Whether "古早味" is specifically Taiwanese or a broader Sinitic nostalgia term.
- Whether traditional script marks Taiwaneseness or simply an aesthetic/premium style.
- Whether a consumer mention of Taiwan expresses acceptance, comparison, rejection, or casual reference.

## 8. Analysis Sequence

1. Build a sample list and maintain a data log.
2. Clean text while preserving `original_text`, `original_script`, and `normalized_text`.
3. Run keyword matching and calculate initial domain scores.
4. Manually code the gold set and revise the codebook.
5. Compare merchant texts with consumer reviews.
6. Calculate the Consumer Reinterpretation Gap.
7. Select 3-5 brands or shops for close reading.
8. Integrate quantitative indicators with close reading into the paper argument.

## 9. What Not to Do Too Early

- Do not start with large-scale scraping.
- Do not train word embeddings before you have a sufficiently large and clean corpus.
- Do not interpret search peaks as direct evidence of political causation.
- Do not treat platform ratings as a complete measure of consumer attitude.
- Do not define Taiwaneseness as a single stable essence. Treat it as a multi-domain sign structure that can be commercialized, stylized, circulated, and reinterpreted.

## 10. Two-Week Execution Plan

### Days 1-2

Finalize pilot cities and keywords. Create the data log. Manually collect 10 test cases to check whether the fields are sufficient.

### Days 3-5

Collect 20 merchant pages per city. Record shop names, platform tags, descriptions, menu items, recommended dishes, visual cues, and URLs.

### Days 6-8

Collect up to 30 public reviews per merchant. Build the review table. Do not collect unnecessary personal profile data.

### Days 9-10

Run the first manual coding round and record uncertain cases.

### Days 11-12

Revise the lexicon. Calculate the five Taiwaneseness domain scores and the Consumer Reinterpretation Gap.

### Days 13-14

Write a 2-3 page pilot memo covering sample construction, method, initial findings, failures, and whether the design should be scaled.
