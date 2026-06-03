# Spatial Seed Memo

## Purpose

This memo records the first spatial seed test for the project. The goal is to see whether the geography of Taiwanese lu rou fan in mainland China may produce a stronger and less obvious argument than a general commodification claim.

## Data Added

Files:

- `data/city_metadata.csv`
- `data/brand_city_presence_seed.csv`
- `scripts/analyze_spatial_diffusion.py`
- `outputs/spatial_official/city_presence_enriched.csv`
- `outputs/spatial_official/corridor_summary.csv`
- `outputs/spatial_official/coastal_status_summary.csv`

The current seed uses 阿元来了 as a first brand-level test case because its official store locator lists open and planned mainland stores by city.

## First Official-Only Snapshot

Using city-level official store-locator data only:

- Yangtze River Delta: 18 open stores, 35 planned stores, 53 total, 64.6% of open+planned city-level presence.
- Coastal cities: 11 open stores, 31 planned stores, 42 total, 51.2% of city-level presence.
- Inland-Yangtze cities: 8 open stores, 12 planned stores, 20 total, 24.4%.
- Inland cities outside the YRD: 3 open stores, 17 planned stores, 20 total, 24.4%.

## Preliminary Interpretation

The seed snapshot supports a tentative **Yangtze River Delta Gateway Hypothesis**. 阿元来了's official mainland expansion is heavily concentrated in Shanghai and the YRD, especially when open and planned stores are combined.

The same data also shows a second-stage pattern: inland expansion appears mainly as planned stores rather than established open stores. This is compatible with an **Inland Platformization Hypothesis**, where the category moves inland through malls and standardized chain formats after gaining visibility in Shanghai/YRD.

## Why This Is More Interesting Than the Original Claim

The original claim that Taiwaneseness is commodified and reinterpreted is plausible but broad. The spatial result asks a sharper question:

> Does the commodification of Taiwaneseness have a geography?

This allows the paper to connect semiotics, platform commerce, and geo-cultural diffusion.

## Cautions

1. This seed is brand-specific, not category-wide.
2. Official store-locator pages mix open and planned stores; these must remain separate.
3. Third-party counts should not be merged with official store-locator rows without deduplication.
4. Opening years are not yet known. The current `first_observed_year` records observation, not actual first opening, unless a source explicitly gives an opening date.

## Next Data Target

Build a multi-brand, multi-source spatial corpus:

- 阿元来了
- 捡角台湾食堂
- 叁店·台湾滷肉饭
- 家里没煮
- 隆莱呷·台湾省滷肉饭
- 廟口·魯肉饭

For each brand/category case, collect city presence by:

- official store locator;
- public restaurant listings;
- industry reports;
- archived pages;
- source-logged manual searches.

