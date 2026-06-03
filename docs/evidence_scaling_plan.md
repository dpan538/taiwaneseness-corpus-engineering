# Evidence Scaling Plan: 200 Verified Attestations

## Why the Current Seed Is Not Enough

The current 1940-2020 seed is a pipeline test, not a research corpus. It is too small and unevenly distributed to support historical inference. It can show whether the method works, but it cannot yet support claims about diffusion, semantic shift, capital origin, or regional coverage.

The next research threshold is:

> minimum 200 verified attestations or source-grounded examples before interpretive claims are treated as findings.

## Unit of Evidence

The project should distinguish **sources** from **attestations**.

### Source

A source is a document, webpage, newspaper article, archive item, brand page, menu, platform listing, review page, image record, business-registry record, or scholarly text.

### Attestation

An attestation is one dated, source-grounded observation of a relevant term, dish, brand, ownership structure, city presence, menu item, or semantic framing.

One source may produce multiple attestations, but they must be separately justified. For example, an official brand timeline may provide one attestation for 1960 founding, another for 1979 first branch, and another for 2018 platform delivery.

## Superseding Macro Corpus Target

The project now uses a heavier three-phase target:

- 1946-1987: at least 120 verified/probable attestations.
- 1987-2015: at least 120 verified/probable attestations.
- 2015-2025: a separate capital/platform event corpus, currently target 80 records, because internet-era textual visibility is distorted by platform ranking, SEO, franchise portals, and wanghong media.

This design is documented in `docs/three_phase_corpus_design.md`.

Run the macro audit:

```bash
python3 scripts/audit_macro_coverage.py \
  --attestations data/historical_geo_attestations_1940_2020_seed.csv \
  --capital-events data/capital_event_seed_2015_2025.csv \
  --plan data/macro_collection_plan.csv \
  --output-dir outputs/macro_audit_seed
```

If `macro_inference_ready` is `0`, the project remains in evidence-building mode.

## Earlier Minimum Corpus Target

Target:

- 200 verified attestations.
- At least 100 unique sources if possible.
- At least 40 archive/newspaper attestations.
- At least 30 ownership/capital attestations.
- At least 30 merchant/menu/platform attestations.
- At least 30 Taiwan-side pre-mainland attestations.

## Period Quotas

| Period | Minimum Attestations | Purpose |
|---|---:|---|
| 1940-1945 late colonial | 15 | Establish whether relevant terms appear in late-colonial food/market discourse. |
| 1946-1949 postwar transition | 15 | Track postwar restructuring of Taiwan food discourse. |
| 1950-1978 Taiwan-side popular food | 35 | Build evidence for lu rou fan as stall/market/local food. |
| 1979-1987 brand formalization | 20 | Track branch formation, trademarks, restaurantization, and Taiwan-side brand development. |
| 1988-2001 cross-strait mobility | 30 | Track Taiwan food/capital movement into mainland and broader Sinophone markets. |
| 2002-2013 Taiwan-capital gateway | 40 | Track Shanghai/YRD and major-city Taiwan-food visibility before mobile-platform dominance. |
| 2014-2020 pre-wanghong platformization | 50 | Track mainland lu rou fan visibility before the 2021+ wanghong boom. |

This totals 210, giving a small buffer above the 200 minimum.

## Regional Quotas

At minimum:

- Taiwan-side: 60 attestations.
- Shanghai/Yangtze River Delta: 50 attestations.
- North China / Beijing-Tianjin: 20 attestations.
- South / Pearl River Delta: 20 attestations.
- Fujian / cross-strait southeast: 15 attestations.
- Central / inland China: 15 attestations.
- Other or national-level sources: 20 attestations.

These are not equal because the expected historical signal is not evenly distributed. But they prevent the corpus from becoming a Shanghai-only story.

## Source-Type Quotas

At minimum:

- Newspaper/archive articles: 40.
- Brand timelines / official histories: 20.
- Business registry / capital records: 30.
- Menus / platform listings / restaurant pages: 30.
- Reviews / consumer-facing platform discourse: 30.
- Media / industry reports: 30.
- Academic or official cultural sources: 20.

## Verification Levels

### verified

The source gives a date, place, and relevant textual evidence directly.

### probable

The source is credible but retrospective, or date/place is inferred from a reliable context.

### candidate

The source appears relevant but has not yet been checked enough to use.

### rejected

The source is irrelevant, unverifiable, duplicate, misleading, or outside scope.

Only `verified` and carefully marked `probable` records should enter analysis. Candidate records are for collection management, not findings.

## Stop/Go Rules

Do not make findings-level claims until:

1. total verified/probable attestations >= 200;
2. every period has at least half of its quota;
3. 1940-1978 has at least 40 verified/probable attestations;
4. 2014-2020 has at least 35 verified/probable attestations;
5. ownership/capital records cover at least 30 brands/cases;
6. the corpus has been audited for source duplication and source-type imbalance.

## Inference Rules

- If a period has fewer than 10 attestations, describe it only as an evidence gap.
- If a region has fewer than 10 attestations, do not compare its semantic score to other regions.
- If ownership is unknown for more than 40% of relevant mainland cases, do not claim a capital-origin shift.
- If a source is retrospective, use it for chronology only when corroborated or explicitly marked.
