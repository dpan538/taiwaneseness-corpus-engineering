# Long-Run 1940-2020 Mining Memo

## Purpose

This memo records the first deeper mining pass for the 1940-2020 cycle. The goal is to shift the project away from a recent wanghong-only story and toward a long-run geo-historical account:

```text
Taiwan-side lu rou fan as stall/market popular food
-> Taiwan-side brand formalization
-> cross-strait Taiwan-capital food mobility
-> Shanghai/YRD Taiwan-flavor visibility
-> pre-wanghong platform and retail commodification
```

## New Files

- `data/source_targets_1940_2020.csv`
- `data/historical_geo_attestations_1940_2020_seed.csv`
- `data/processed/historical_geo_attestations_1940_2020_scored.csv`
- `outputs/geo_historical_1940_2020/period_semantic_summary.csv`
- `outputs/geo_historical_1940_2020/period_corridor_semantic_summary.csv`
- `outputs/ownership_1940_2020/historical_attestations_with_ownership.csv`
- `outputs/ownership_1940_2020/period_corridor_ownership_summary.csv`

## Current Seed Size

The current expanded seed contains 25 records:

- 4 records for 1950-1978 Taiwan-side popular food.
- 3 records for 1979-1987 brand formalization / reopening.
- 4 records for 1988-2001 cross-strait mobility.
- 8 records for 2002-2013 Taiwan-capital gateway.
- 6 records for 2014-2020 pre-wanghong platformization.

There are no validated 1940-1949 attestations yet. That gap should not be filled by inference; it requires archive searches.

This is still far below the required corpus size. The current file should be treated as a seed and pipeline test only. The project now uses a 200-attestation minimum, documented in `docs/evidence_scaling_plan.md`.

## First Pattern

### 1950-1978: Taiwan-Side Popular Food

The seed is anchored by 鬍鬚張, 阿義魯肉飯, and UDN retrospective material around Taipei food districts. Lu rou fan appears as a Taiwan-side stall, market, and popular-food object.

Current signal:

- binding rate: 1.0
- main geography: Taipei / Taiwan-side
- semantic profile: lu rou fan + Taipei/Taiwan markers, with some night-market/stall cues

### 1979-1987: Brand Formalization

The key transition is not mainland diffusion yet; it is Taiwan-side formalization. 鬍鬚張 opens a first branch and registers brand/service marks; 台菜 restaurants such as 阿才的店 show local Taiwanese cuisine becoming restaurantized.

Current signal:

- lu rou fan remains Taiwan-side
- brand/branch formation begins before mainland entry
- 台菜 and lu rou fan should be kept analytically related but not collapsed

### 1988-2001: Cross-Strait Mobility

The sample shows cross-strait and mainland market mobility through Taiwan-style chains and Taiwan-capital food enterprises rather than lu rou fan itself.

Current signal:

- Taiwan-capital / Taiwan-style chain forms become mobile
- lu rou fan remains strongly Taiwan-side in the seed
- mainland side shows Taiwan-style food/drink and Taiwan-capital fast-casual formats

### 2002-2013: Taiwan-Capital Gateway

This is the first strong mainland gateway period. 一茶一坐 enters Shanghai/Xintiandi; Expo 2010 gives public visibility to "台味" and includes 台式卤肉饭 as one item among broader Taiwan-themed food offerings.

Current signal:

- Shanghai/YRD becomes important.
- Taiwaneseness is still broader than lu rou fan.
- ownership/capital layer is crucial: 一茶一坐 is coded as Taiwan-mainland joint venture; Expo is coded as mixed event platform.

### 2014-2020: Pre-Wanghong Platformization

This period is the bridge into the later boom. Evidence includes a 2015 Shanghai Taiwan-restaurant lu rou fan image, 2018 Shanghai "台湾古早味" lu rou fan media, Taiwan-side delivery/digitalization of 鬍鬚張, and a 2020 Shanghai retail product turning "Taiwan lu rou fan flavor" into a bun.

Current signal:

- mainland Shanghai lu rou fan visibility exists before the 2024-2025 boom.
- Taiwan flavor begins to detach from restaurant ownership and become retail/flavor format.
- this period is the precondition for later wanghong acceleration, not the same as the later boom.

## Ownership / Capital Signal

The ownership-joined seed currently shows:

- pre-2014 records are mostly Taiwan-side/Taiwan-capital or Taiwan-mainland joint venture;
- 2010 Expo is mixed event/platform visibility;
- 2018 Shanghai "台湾古早味" lu rou fan is coded as likely mainland Taiwan-themed, pending registry verification;
- 2020 大润发台湾风味卤肉大包 is coded as retail-platform commodification, not Taiwan capital.

This supports a more precise capital hypothesis:

> Before the platform era, mobility is often carried by Taiwan-side brands, Taiwan capital, or Taiwan-mainland joint ventures. By 2014-2020, Taiwaneseness begins to appear as a detachable flavor/style label within mainland restaurant and retail formats.

## Important Archive Gap

The 1940-1949 and 1950s layers remain under-mined. The current open web is insufficient. The project needs systematic searches in:

- 臺灣日日新報 / Taiwan Nichinichi Shinbun
- 臺灣新生報
- 聯合知識庫
- 中國時報 archive
- 公論報
- 自立晚報
- National Culture Memory Bank
- Airiti

Search terms:

- 魯肉飯
- 滷肉飯
- 肉燥飯
- 肉臊飯
- 滷肉
- 魯肉
- 台菜 / 臺菜
- 小吃
- 路邊攤
- 圓環
- 雙連
- 華西街
- 寧夏

The key methodological rule is that absence matters only after documented search. Do not claim "lu rou fan was absent" in a period unless the archive search log records terms, dates, databases, and result counts.

## Next Research Step

Build two new tables:

1. `archive_search_log_1940_1980.csv`
   - database
   - search term
   - date range
   - result count
   - earliest hit
   - notes

2. `attestations_from_archives.csv`
   - each dated newspaper/cookbook/menu attestation
   - exact title/source/date
   - original phrase
   - page or archive ID
   - region/city
   - dish marker
   - Taiwan marker

This will turn the early historical layer from interpretive background into data.
