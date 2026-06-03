# Geo-Historical Seed Memo

## Purpose

This memo records the first test of the two-layer model:

1. **Geographical diffusion**: where Taiwanese lu rou fan and adjacent Taiwanese-food formats appear.
2. **Historical semantic regime**: how Taiwaneseness changes across periods.

The goal is to capture a progressive relationship:

> spatial movement produces semantic translation.

## Files

- `docs/geo_historical_semantic_model.md`
- `data/historical_geo_attestations_seed.csv`
- `config/semantic_periods.json`
- `scripts/analyze_geo_historical_semantics.py`
- `data/processed/historical_geo_attestations_scored.csv`
- `outputs/geo_historical/period_semantic_summary.csv`
- `outputs/geo_historical/period_corridor_semantic_summary.csv`

## Seed Periods

### 2002-2013: Taiwanese Casual-Dining Gateway Regime

Early evidence centers on 一茶一坐 and broader Taiwanese casual dining. The key geography is Shanghai/YRD, with expansion outward to major cities. In this period, Taiwaneseness is visible, but lu rou fan is not yet the central binding object.

Seed result:

- Taiwan markers present.
- Lu rou fan binding absent in the current seed.
- Semantic profile emphasizes chain/casual-dining format rather than night-market or authenticity lu rou fan.

### 2014-2020: Night-Market / Authenticity Regime

阿元来了's origin story links Hong Kong, a Taiwanese chef, Taiwanese street food, and lu rou fan. This is the moment where lu rou fan begins to appear as a strongly branded Taiwan object, but before the major mainland boom.

Seed result:

- lu rou fan binding present.
- geographic and authenticity cues are visible.
- night-market/street-food cues begin to matter.

### 2021-2023: Platform Transition Regime

捡角台湾食堂 appears as a Shanghai street-side / YRD expansion case. The semantic object narrows from general Taiwanese cuisine toward Taiwanese rice bowls, snacks, and chainable small-store formats.

Seed result:

- lu rou fan binding present.
- geographic score is high.
- night-market / street-side cues increase.
- platform/chain cue appears.

### 2024-2026: Lu Rou Fan Specialty Boom Regime

The seed data suggests a distinct recent boom: 家里没煮, 阿元来了, and other lu rou fan-centered cases are framed through price, value, consumer downgrade, Michelin/award authority, standardization tension, and mall-based expansion.

Seed result:

- lu rou fan binding is consistently present.
- YRD remains the main corridor in the current seed.
- Central China / Zhengzhou appears as an inland mall-commercial expansion case.
- platform/value language becomes more visible.

## Current Quantitative Signal

The corrected seed aggregation shows:

- 2002-2013 gateway period: Taiwan markers without lu rou fan binding.
- 2014 onward: lu rou fan binding appears.
- 2024-2026: platform/value language becomes stronger than in the night-market/authenticity origin stage.

This supports a tentative progression:

```text
broad Taiwanese cuisine in Shanghai/YRD
-> branded night-market lu rou fan
-> Shanghai/YRD platform-food boom
-> planned inland mall/platform expansion
```

## Why This Matters

This is stronger than simply saying Taiwaneseness is commodified. The project can now ask:

> Which geography produces which Taiwaneseness?

For example:

- Shanghai/YRD may produce Taiwaneseness as modern chain dining first, then affordable platform rice-bowl culture.
- Coastal/cross-strait cities may preserve stronger geographic/cultural-proximity meanings.
- Inland expansion may translate Taiwaneseness into mall, chain, value, and standardized fast-casual language.

## Next Step

The seed is too small to prove the model. The next step is to build a fuller attestation table with at least:

- 30 records for 2002-2013 broad Taiwanese dining and early Taiwan food chains;
- 30 records for 2014-2020 night-market/authenticity Taiwan-food brands;
- 50 records for 2021-2026 lu rou fan specialty and platform-food cases;
- city and corridor metadata for every record.

Then compare:

- binding rate by period;
- domain scores by period;
- domain scores by corridor;
- domain scores by period-corridor interaction.

