# Experimental Design Upgrade: Controls, Consumer Stance, Time, and Platform Bias

## Why This Matters

The current design can measure Taiwan markers inside Taiwan-labeled lu rou fan cases, but that is not enough to show specificity. Without controls, a high Taiwaneseness score may simply reflect generic platform food branding, nostalgia language, or the broader popularity of Taiwan-themed foods.

The design should therefore add negative and positive controls, finer consumer-stance coding, longitudinal captures, and platform-source separation.

## Control Groups

### Target Group

Taiwan-marked lu rou fan:

- `台湾卤肉饭`
- `台式卤肉饭`
- `台灣滷肉飯`
- `Taiwanese braised pork rice`

### Control Group A: Same Dish, No Taiwan Marker

Mainland/local lu rou fan without Taiwan markers:

- `卤肉饭`
- `老上海卤肉饭`
- `本帮卤肉饭`
- `江南卤肉饭`
- `砂锅卤肉饭`

Purpose:

Measure whether authenticity, nostalgia, night-market, and platform-fast-food markers are specific to Taiwan-labeled lu rou fan or common to lu rou fan generally.

### Control Group B: Same Taiwan Marker, Different Dish

Taiwan-marked non-lu-rou-fan dishes:

- `台湾牛肉面`
- `台湾香肠`
- `台湾奶茶`
- `台湾鸡排`
- `台湾小吃`

Purpose:

Test whether Taiwaneseness binding is dish-specific or travels across a broader Taiwan-food brand ecology.

## Sampling Recommendation

For a pilot:

- 20-30 merchants per city per group.
- Cities: Shanghai, Beijing, Chengdu as the minimal comparison.
- Groups: target, same-dish/no-Taiwan control, Taiwan-other-dish control.

For statistical comparison:

- 80-100 merchants per city per group.
- The pilot should not use significance testing unless the corpus reaches this scale and passes the health audit.

## Consumer Stance Categories

Replace a simple merchant-marker/review-marker overlap with rule-assisted stance categories.

```text
0 = no Taiwan mention
1 = reproduces merchant's Taiwan markers
2 = adds new Taiwan markers
3 = shifts Taiwan marker to non-food attributes
4 = rejects or contests Taiwan authenticity
```

Examples:

- 0: "卤肉饭很好吃，米饭够软。"
- 1: merchant says `台式`; review says "台式味道不错。"
- 2: merchant says `台湾`; review adds "像士林夜市。"
- 3: "老板说话很台湾，服务很温柔。"
- 4: "根本不是台湾味，就是普通盖饭。"

Metrics:

- `reproduction_rate = stance_1 / total_reviews`
- `transformation_rate = (stance_2 + stance_3) / total_reviews`
- `rejection_rate = stance_4 / total_reviews`
- `no_mention_rate = stance_0 / total_reviews`

## Longitudinal Design

Static platform snapshots are risky because shop descriptions, recommended dishes, tags, rankings, and promotional content change.

Pilot longitudinal panel:

- 10 merchants.
- Monthly capture for 3 months.
- Record merchant description, platform tags, recommended dishes, menu names, review-marker frequency, and rating/review-count changes.

Preferred longer design:

- two captures at least six months apart;
- one pre/post event comparison if a relevant platform campaign, food festival, or public controversy appears.

## Platform Algorithm Separation

Each captured field should be labeled by provenance:

- `merchant_provided`: shop name, merchant description, uploaded menu item names where identifiable.
- `platform_generated`: recommended dishes, hot tags, ranking labels, "guess you like",榜单, promotion modules.
- `consumer_generated`: reviews, review tags, user-uploaded captions.
- `unknown_or_mixed`: when provenance cannot be determined.

Recommended new fields:

- `field_source`
- `is_ad`
- `is_ranking`
- `is_platform_generated`
- `capture_module`

Platform-generated markers should not be treated as pure merchant self-representation.

## Ownership Layer

Every platform merchant in the main analytical sample should receive an ownership attempt:

- operating company;
- registered capital;
- legal representative;
- shareholder structure;
- registered address;
- trademark applicant if available;
- franchise/brand headquarters claim;
- ownership category:
  - `Taiwan_capital`
  - `Taiwan_mainland_joint`
  - `HK_intermediary`
  - `mainland_Taiwan_themed`
  - `franchise_capital`
  - `unknown`

Do not classify Taiwan capital from surnames. Use registry, trademark, founder biography, company address, or official brand evidence.

## New Analysis Modules

| Module | Purpose | Output |
|---|---|---|
| control-group sampler | create target/control samples | `data/control_group_sample.csv` |
| consumer stance classifier | classify review stance toward Taiwan markers | `outputs/consumer_stance_classified.csv` |
| longitudinal diff | compare merchant/platform marker changes over time | `outputs/longitudinal_marker_diff.csv` |
| ownership heuristic classifier | classify capital/ownership with rule traces | `outputs/ownership_heuristic_classified.csv` |

## Claim Rules

- Without control groups, do not claim Taiwan markers are specific to Taiwan lu rou fan.
- Without stance categories, do not claim consumers reproduce or reject merchant Taiwaneseness.
- Without longitudinal captures, do not claim platform markers are stable.
- Without ownership attempts, do not claim Taiwaneseness is capital-led, mainland-themed, or franchise-driven.

