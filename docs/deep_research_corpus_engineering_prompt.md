# Deep Research Prompt: Corpus Engineering for the Geo-Historical Semantics of Taiwaneseness

## Role

You are a computational humanities research engineer and food-history research assistant. Your task is not to write a literary interpretation. Your task is to design a reproducible, source-grounded, script-first research pipeline for studying how "Taiwaneseness" becomes attached to lu rou fan / rouzao rice / braised pork rice across Taiwan, mainland China, and overseas Sinophone/diaspora food systems from the postwar period to the platform era.

The project is English-first. All final research design, schemas, scripts, and methodological language should be written in English, while preserving Chinese/Japanese/Korean/Vietnamese source terms exactly where needed.

## Central Thesis Under Test

In mainland China, "Taiwanese braised pork rice" does not simply reproduce a Taiwanese dish. Rather, it transforms "Taiwaneseness" into a consumable cultural sign through menu language, visual branding, platform representation, capital/ownership structures, and consumer interpretation.

This thesis is plausible but not yet quantitatively supported. The current corpus is too small and uneven. Your job is to design a scalable corpus-building method that can decide whether the thesis survives larger evidence.

## Current Corpus Problem

The current working corpus has only about 100 usable 1946-1987 records against a target of 700+ for the first historical phase. This is not enough for statistical inference. The next stage must move from manual web-search harvesting to systematic corpus engineering.

Do not offer only a conceptual plan. Produce a concrete implementation plan with source targets, data schemas, crawler/search scripts, deduplication rules, audit metrics, and health-rating standards.

## Core Motifs / Research Mother-Themes

Design the data model around these motifs. Do not collapse them into one vague "Taiwanese food" category.

1. Taiwan-side local-food formation
   - Lu rou fan / rouzao rice as stall food, market food, breakfast/lunch rice, night-market food, and everyday popular food.
   - Variants: 魯肉飯, 滷肉飯, 肉燥飯, 肉臊飯, 卤肉饭, braised pork rice, minced pork rice.
   - Important contexts: Shuanglian, Ningxia, Taipei Roundabout, Wanhua, Tainan, Kaohsiung, Changhua, Hsinchu, local markets, military-village food, southern rouzao rice ecology.

2. Semantic binding between dish markers and Taiwan markers
   - When does a dish marker appear without Taiwan?
   - When does it become "Taiwanese," "Taiwan-style," "old taste," "night market," "Formosa," "Bao Dao," "Taiwan snack," or "Taiwan cuisine"?
   - Measure binding rather than assume identity.

3. Geo-historical diffusion
   - Track whether mainland diffusion is mainly Shanghai/Yangtze River Delta, Fujian/southeast coastal, Pearl River Delta, Beijing/North China, inland/Chengdu-Chongqing-Wuhan-Xi'an, or nationwide platform/franchise expansion.
   - Separate Taiwan-side formation from mainland representation.

4. Capital and ownership
   - Distinguish Taiwan capital, Taiwan-mainland joint ventures, Hong Kong intermediaries, mainland Taiwan-themed operators, franchise capital, mall/platform capital, and post-2015 wanghong/platform contamination.
   - The question is not only where Taiwan-themed food appears, but who funds, owns, franchises, and platformizes it.

5. Restaurantization and brand formalization
   - Track movement from stall/market food to branded shops, chain stores, registered trademarks, official timelines, franchising, mall stores, delivery platforms, and retail packaged goods.

6. Diaspora and overseas translation
   - Singapore: "Taiwan porridge" / "Taiwanese porridge" in hotel and newspaper contexts.
   - Japan: 台湾料理 / 台湾ラーメン / Taiwanese restaurant branding.
   - North America: Taiwanese restaurant ecologies in Flushing, Monterey Park, San Gabriel Valley, and Taiwan-origin regional Chinese restaurant labor.
   - Vietnam/Korea/Latin America: currently under-covered; identify whether absence is real or a source-access problem.

7. Platformization and wanghong contamination
   - 2015-2025 evidence must be treated differently because SEO, Dianping/Meituan ranking, Xiaohongshu virality, franchise pages, and influencer content distort visibility.
   - Platform data should be used, but must not be mixed naively with pre-internet sources.

8. Consumer reinterpretation
   - Compare merchant-produced Taiwaneseness with consumer-language Taiwaneseness.
   - Consumers may reproduce, ignore, localize, parody, reject, or detach Taiwan markers from the dish.

## Required Research Window

Design for the full period 1940-2025, but use different evidence logic by phase.

- 1940-1945: late colonial and immediate pre/post transition layer. Use as contextual layer if source access permits.
- 1946-1987: Taiwan-side formation and overseas/diaspora translation before martial-law lifting. Target at least 700 verified/probable attestations.
- 1987-2015: cross-strait mobility and pre-wanghong diffusion. Target at least 700 verified/probable attestations.
- 2015-2025: platform, capital, franchise, and wanghong layer. Target at least 300 records, but treat these as a separate platform/capital corpus rather than a direct continuation of archival evidence.

## Required Source Families

For each source family, provide:

- exact archives/sites/databases to search;
- access method: API, static HTML, search URL, PDF/OCR, manual archive, institutional login, web cache;
- candidate search terms in original language;
- expected fields to extract;
- likely bias;
- whether it can support verified, probable, or candidate evidence.

Minimum source families:

1. Taiwan historical newspapers and archives
   - 臺灣新生報
   - 聯合報 / 聯合知識庫
   - 中國時報 archive
   - 公論報
   - 自立晚報
   - 國家文化記憶庫 / National Culture Memory Bank
   - Taiwan Memory / NCL resources
   - municipal cultural archives
   - oral-history PDFs and local-history monographs

2. Taiwan government / municipal food tourism / local culture
   - Taipei, New Taipei, Taichung, Tainan, Kaohsiung, Changhua, Hsinchu, Chiayi, Pingtung.
   - Old-shop lists, night-market pages, local-history PDFs, food festival records.

3. Mainland newspapers and official/industry sources
   - People's Daily full-text sources.
   - Local newspapers by province if accessible.
   - Government open-data pages.
   - Business registry sources for restaurant operators and franchise companies.
   - Food industry reports and franchise portals.

4. Mainland platform / merchant sources
   - Dianping / Meituan pages.
   - Baidu Baike / Qichacha / Tianyancha for ownership and company timelines.
   - Brand websites and franchise recruitment pages.
   - Xiaohongshu / Douyin only for 2015-2025 platform layer, with strong bias controls.

5. Overseas archives
   - NewspaperSG.
   - Japanese municipal archives, restaurant histories, media pages for 台湾料理.
   - US/Canada newspapers, local food press, digitized menus, diaspora community sources.
   - Korean and Vietnamese sources, especially where Taiwanese restaurants appear after Taiwanese capital or manufacturing migration.
   - Latin America Chinese/Taiwanese diaspora sources, even if only negative-search logs are produced.

6. Books and academic sources
   - Food history books.
   - Chinese food globalization studies.
   - Taiwan cuisine and nationalism studies.
   - Diaspora restaurant history.
   - Use these for context and source discovery, not as a substitute for primary attestations.

## Required Output Data Model

Propose CSV/JSONL schemas for at least these tables:

1. `source_registry.csv`
   - `source_id`
   - `source_family`
   - `source_name`
   - `source_url_or_archive_ref`
   - `access_method`
   - `access_date`
   - `date_range`
   - `country_or_area`
   - `language`
   - `source_type`
   - `bias_notes`
   - `robots_or_terms_notes`
   - `status`

2. `archive_search_log.csv`
   - `search_id`
   - `source_id`
   - `query_terms`
   - `date_start`
   - `date_end`
   - `filters`
   - `result_count`
   - `earliest_hit_date`
   - `latest_hit_date`
   - `sample_hit_ids`
   - `search_url_or_command`
   - `notes`

3. `attestations.csv`
   - `attestation_id`
   - `source_id`
   - `year`
   - `date`
   - `period`
   - `country_or_area`
   - `region`
   - `province`
   - `city`
   - `corridor`
   - `brand_or_category`
   - `dish_marker`
   - `taiwan_marker`
   - `original_text`
   - `normalized_text`
   - `attestation_type`
   - `source_type`
   - `verification_level`
   - `confidence`
   - `dedupe_key`
   - `notes`

4. `ownership_capital_events.csv`
   - `event_id`
   - `brand`
   - `operating_company`
   - `event_year`
   - `event_date`
   - `event_type`
   - `founder_origin`
   - `ownership_category`
   - `capital_origin`
   - `mainland_entry_city`
   - `registry_source`
   - `evidence_text`
   - `verification_level`

5. `merchant_platform_records.csv`
   - `merchant_id`
   - `platform`
   - `capture_date`
   - `city`
   - `shop_name`
   - `branch_name`
   - `platform_tags`
   - `menu_item_names`
   - `recommended_dishes`
   - `merchant_description`
   - `visual_branding_text`
   - `rating`
   - `review_count`
   - `source_url`
   - `crawl_status`

6. `consumer_reviews.csv`
   - `review_id`
   - `merchant_id`
   - `platform`
   - `review_date`
   - `rating`
   - `review_text`
   - `likes_or_votes`
   - `capture_date`
   - `source_url`
   - `cleaning_status`

## Required Script Implementation Plan

Provide concrete script designs. For each script, specify:

- filename;
- command-line interface;
- input files;
- output files;
- libraries;
- pseudocode or executable code skeleton;
- expected failure modes;
- tests or validation checks.

Minimum scripts:

1. `scripts/build_source_registry.py`
   - Reads a seed list of source families.
   - Outputs a normalized source registry.

2. `scripts/run_archive_searches.py`
   - Runs scripted search queries where legal/technically possible.
   - Logs query, date range, result count, earliest hit, and sample IDs.
   - Must support dry-run mode.

3. `scripts/harvest_static_pages.py`
   - Fetches static official pages, municipal pages, brand pages, and public archives.
   - Stores raw HTML/PDF references and extraction metadata.

4. `scripts/ocr_pdf_sources.py`
   - Processes PDFs with OCR when source text is not extractable.
   - Must store OCR confidence and page numbers.

5. `scripts/extract_attestations.py`
   - Extracts candidate attestations from raw text using keyword windows.
   - Supports multilingual keyword lists.
   - Outputs candidate rows with source windows and dedupe keys.

6. `scripts/normalize_multilingual_text.py`
   - Normalizes simplified/traditional variants, Japanese/Korean/Vietnamese text where possible, and romanizations.
   - Does not destroy original text.

7. `scripts/geocode_and_classify_corridors.py`
   - Maps city/province/country to corridors:
     Taiwan-side, Mainland-YRD, Mainland-southeast, Mainland-PRD, Mainland-North, Mainland-inland, Japan, Singapore, Korea, Vietnam, North America, Latin America, other.

8. `scripts/classify_verification_level.py`
   - Applies transparent rules for verified/probable/candidate/rejected.
   - Human review allowed only as an audit layer, not as the primary method.

9. `scripts/dedupe_attestations.py`
   - Detects duplicate source/date/brand/text records.
   - Must distinguish source duplicates from valid multiple attestations within one source.

10. `scripts/score_taiwaneseness_binding.py`
   - Computes dish-marker presence, Taiwan-marker presence, authenticity markers, nostalgia markers, platform markers, ownership markers.
   - Produces binding indices by period, source type, region, and corridor.

11. `scripts/audit_corpus_health.py`
   - Implements the coverage/health rubric below.
   - Outputs CSV summary and a Markdown audit report.

12. `scripts/build_research_dashboard.py`
   - Optional but recommended.
   - Generates tables/plots for period coverage, source-type coverage, geographic coverage, verification mix, duplication rate, and semantic binding.

## Required Corpus Health / Coverage Rating Scheme

Design and implement a rating system. Use both a numeric score and letter grade. The grade must prevent the researcher from making claims from an unhealthy corpus.

### Core Metrics

1. Total usable record coverage
   - `usable_records = verified + probable`
   - score by phase against target.

2. Unique source coverage
   - number of unique `source_id` values.
   - penalize over-reliance on one page, one brand, one newspaper, or one search engine.

3. Temporal coverage
   - each phase must have minimum records by decade/subperiod.
   - identify thin decades explicitly.

4. Geographic coverage
   - Taiwan-side regional spread.
   - Mainland corridor spread.
   - Overseas corridor spread.
   - no Shanghai-only, Singapore-only, or Taipei-only inference.

5. Source-type diversity
   - newspapers/archive, official/municipal, brand/restaurant, business registry, platform/merchant, review/consumer, academic/context.
   - compute source-type entropy or at least proportional caps.

6. Verification quality
   - verified/probable/candidate/rejected proportions.
   - require candidate rows to be excluded from analysis.

7. Duplication and inflation control
   - duplicate rate by source/date/brand/text.
   - no count inflation from repeated ads or repeated platform listings unless each is analytically justified.

8. Ownership completeness
   - for mainland and 2015-2025 records, percentage with known or inferable ownership/capital origin.

9. Reproducibility
   - percentage of rows with source URL/archive ref, access date, query/search ID, and extraction method.

10. Platform-bias control
   - for post-2015 records, flag SEO/wanghong/platform/review-ranking bias.
   - do not compare platform records directly to newspaper archive records without phase adjustment.

### Suggested Letter Grades

Grade A: Inference-ready
- each major phase reaches at least 90% of target;
- unique-source coverage reaches at least 70% of source target;
- no major corridor is empty unless negative-search logs document absence;
- verified/probable share is at least 85%;
- duplicate inflation below 10%;
- ownership completeness above 75% for mainland/platform records;
- all rows have source refs and reproducible search/extraction metadata.

Grade B: Limited inference-ready
- each major phase reaches at least 70% of target;
- unique-source coverage reaches at least 55%;
- no more than one minor corridor is empty;
- verified/probable share at least 75%;
- duplicate inflation below 15%;
- ownership completeness above 60%;
- suitable for cautious descriptive statistics, not strong causal claims.

Grade C: Pilot only
- each major phase reaches at least 40% of target;
- some corridors or decades remain thin;
- verified/probable share at least 60%;
- duplicate inflation below 25%;
- suitable for method testing and exploratory figures only.

Grade D: Evidence-building only
- any major phase below 40% of target;
- multiple empty corridors;
- heavy source concentration;
- suitable only for identifying gaps and refining search strategy.

Grade F: Not usable
- no reproducible source refs;
- candidate-heavy or duplicate-heavy;
- platform-only corpus used for historical claims;
- no defensible audit trail.

### Claim Permission Rules

Implement these as machine-readable audit flags:

- `can_make_macro_historical_claims`
- `can_compare_regions`
- `can_compare_periods`
- `can_analyze_ownership_shift`
- `can_analyze_platformization`
- `can_publish_quantitative_tables`

Rules:

- If any phase is below Grade C, macro historical claims are forbidden.
- If a corridor has fewer than 30 usable records, region-to-region comparison involving that corridor is forbidden.
- If a decade has fewer than 20 usable records, decade-level trend claims are forbidden.
- If ownership completeness is below 60% for mainland records, capital-origin claims are forbidden.
- If source-type diversity is dominated by one source type above 60%, semantic claims must be source-type qualified.
- If post-2015 platform records are mixed with archive records without phase labeling, platformization claims are invalid.

## Required Search Strategy

Produce a search matrix, not just a source list.

For each phase and region, provide:

- source family;
- language;
- exact keywords;
- date range;
- expected output;
- scriptability;
- priority score;
- estimated yield;
- likely false positives.

Include keyword variants:

Chinese:
- 魯肉飯
- 滷肉飯
- 卤肉饭
- 肉燥飯
- 肉燥饭
- 肉臊飯
- 台式
- 台灣小吃
- 台湾小吃
- 台菜
- 臺菜
- 古早味
- 寶島
- 宝岛
- 夜市
- 眷村

English:
- lu rou fan
- luroufan
- braised pork rice
- minced pork rice
- Taiwanese pork rice
- Taiwanese restaurant
- Taiwanese cuisine
- Taiwan porridge

Japanese:
- 台湾料理
- 台湾小吃
- ルーローハン
- 魯肉飯
- 台湾ラーメン

Korean:
- 대만 음식
- 대만 요리
- 루러우판
- 대만식

Vietnamese:
- món Đài Loan
- ẩm thực Đài Loan
- cơm thịt kho Đài Loan
- nhà hàng Đài Loan

Spanish/Portuguese for Latin America:
- restaurante taiwanés
- comida taiwanesa
- arroz con cerdo taiwanés
- culinária taiwanesa
- restaurante taiwanês

## Required Deliverables

Your final answer must include:

1. A source-family map with at least 40 concrete source targets.
2. A phase-region quota plan that can reach:
   - 700+ records for 1946-1987;
   - 700+ records for 1987-2015;
   - 300+ records for 2015-2025.
3. Exact data schemas.
4. A script implementation plan with commands and code skeletons.
5. A health-rating rubric and machine-readable audit flags.
6. A deduplication and verification protocol.
7. A list of high-yield searches to run first.
8. A warning section identifying which claims are currently forbidden until corpus health improves.

## Non-Negotiable Constraints

- Do not rely on blind human coding or taste-panel interpretation.
- Do not treat recent platform visibility as historical frequency.
- Do not count repeated advertisements or duplicated pages as independent evidence unless the purpose is explicitly advertising frequency.
- Do not treat "Taiwanese cuisine" and "lu rou fan" as identical categories.
- Do not infer absence from lack of open-web results. Absence requires documented negative searches.
- Do not produce findings-level claims until the health audit permits them.
- Do not provide a vague literature review. The answer must be operational and implementable.

## Preferred Final Form

Write the response as a research engineering blueprint with headings:

1. Research Object and Hypotheses
2. Corpus Architecture
3. Source Map
4. Search Matrix
5. Data Schemas
6. Script Plan
7. Coverage and Health Rating
8. Deduplication and Verification
9. First 30 Days of Collection
10. Claims Allowed vs. Claims Forbidden

