# Platform Sample Size and Phase Rebalance

## Core Decision

The modern platform layer should be downgraded from the center of the paper to a contemporary reference layer. It remains useful for testing merchant/consumer interpretation, platform bias, and control groups, but it should not carry the historical argument.

The historical layers remain the bottleneck:

- 1946-1987: target 700 usable historical attestations.
- 1987-2015: target 700+ usable mobility/diffusion attestations.
- 2015-2025: exploratory platform/capital reference corpus.

Recommended time allocation:

- 80% historical/archive work.
- 20% platform/control/consumer work.

## Platform Sample Size Logic

A journal-level modern-platform design could target a medium-small effect size:

- Cohen's d = 0.4
- alpha = 0.05
- power = 0.80
- two-tailed independent comparison

This implies about 100 merchants per group per key comparison.

Full modern design:

- Target group: Taiwan-marked lu rou fan, 120 merchants per city x 4 cities = 480.
- Control A: lu rou fan without Taiwan markers, 80 per city x 4 = 320.
- Control B: other Taiwan-marked dishes, 80 per city x 4 = 320.
- Total: about 1,120 merchants.

Reduced exploratory design:

- 2-3 cities.
- 30-50 target merchants per city.
- 20-30 merchants per control group per city.
- Total platform merchants <= 200.
- Total reviews <= 2,000.

The reduced design should be described as exploratory and should not support strong significance claims.

## Matching Requirements

Control groups should be matched where possible on:

- average rating;
- review count;
- average price;
- district or centrality;
- platform;
- capture date.

If perfect matching is impossible, these variables should enter regression models as controls.

## Longitudinal Minimum

Minimum longitudinal sub-sample:

- 20% of target-group merchants;
- two captures;
- six-month interval.

Track:

- merchant-provided Taiwan marker count;
- platform-generated tag changes;
- consumer stance distribution changes;
- review count/rating changes.

## Modern-Layer Analyses

Descriptive:

- Taiwan marker density by city/group;
- consumer stance distribution;
- nostalgia versus wanghong/platform marker prevalence.

Inferential only if sample health permits:

- chi-square tests for marker presence by city/group;
- ANOVA for marker-strength differences;
- regression of rating on Taiwan marker strength, group, city, price, review count, platform-generated marker share, and ownership category;
- logistic regression for selected marker families such as authenticity or nostalgia.

Robustness:

- exclude merchants with fewer than 10 reviews;
- rerun with high-confidence Taiwan markers only;
- include city fixed effects;
- exclude merchants where platform-generated Taiwan markers exceed 50%.

## Historical Priority

The next historical work should prioritize:

1. UDNData, China Times, TBMC, and Taiwan newspaper images.
2. Taiwan Memory, TCMB, Taiwan Historica, NAA, municipal/local archives.
3. NewspaperSG as an overseas comparison baseline.
4. Japan NDL/ADEAC/WARP for translation-layer evidence.
5. Mainland 1987-2015 newspaper, registry, trademark, and franchise sources.

The goal is not a bigger pile of examples. The goal is a healthy, auditable, phase-separated corpus that permits historical claims.

