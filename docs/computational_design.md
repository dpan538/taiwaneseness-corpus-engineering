# Computational-First Research Design

## Position

This project should be computational-first. The main empirical claims should come from scripted collection, scripted normalization, scripted lexicon scoring, and reproducible gap calculation. Human interpretation remains necessary, but it should be used mainly for validation, error analysis, and close reading of selected cases, not as the primary measurement engine.

The strongest publishable design is therefore:

```text
public sources -> source log -> text extraction -> normalization -> lexicon scoring
-> binding/gap metrics -> validation audit -> close reading
```

## What Should Be Automated

### 1. Source Logging

Every collected page or record should have:

- source URL or archive reference
- platform/source type
- city
- query term
- capture date/time
- access method
- robots/permission note when relevant
- raw or extracted text location

### 2. Text Normalization

Normalization should be scripted and minimal:

- Unicode NFKC normalization
- whitespace normalization
- lowercasing for English
- preservation of original script and original text

Full traditional/simplified conversion should not be automatic at the first stage because script choice is part of the Taiwaneseness signal.

### 3. Lexicon Scoring

The lexicon should live in a versioned machine-readable file:

- `config/taiwaneseness_lexicon.json`

The scoring script should calculate:

- dish marker count
- Taiwan marker count
- binding presence
- five Taiwaneseness domain counts
- five Taiwaneseness domain density scores
- traditional-script cue presence

### 4. Consumer Reinterpretation Gap

Gap calculation should be fully scripted:

```text
Gap(domain) = merchant_domain_score - mean(consumer_domain_score)
```

The gap should be calculated by merchant first, then aggregated by brand, city, or platform.

## What Should Not Be Fully Automated

### 1. Validation

A publishable computational paper still needs validation. The goal is not to make human coding the main experiment. The goal is to test whether the automated measures behave reliably.

Use a small audit set:

- 50-100 merchant text units
- 200-300 reviews

For each unit, record whether the automated domain labels are:

- true positive
- false positive
- false negative
- ambiguous

This produces precision/recall-style evidence for the lexicon.

### 2. Interpretation

The scripts can measure association, density, and divergence. They cannot prove motive, authenticity, or causation. The paper should describe computational outputs as evidence of:

- visibility
- lexical association
- semantic density
- merchant-consumer divergence
- platform-mediated reinterpretation

Avoid claiming that scripts reveal what consumers "really think."

## Data Acquisition Strategy

Use a tiered acquisition model.

### Tier 1: Most Reproducible

- official brand websites
- franchise pages
- public media reports
- archived webpages
- platform pages that are publicly accessible and allowed by robots/terms

### Tier 2: Usable With Caution

- manually collected Dianping shop metadata
- manually sampled public reviews
- exported screenshots or page text with source logs

This tier is useful but should be described transparently because platform access can change.

### Tier 3: Exploratory Only

- WeChat Index
- Xiaohongshu search visibility
- opaque platform rankings

These can generate hypotheses but should not be the quantitative backbone unless the collection method is transparent and repeatable.

## Script Inventory

### `scripts/normalize_text.py`

Adds `normalized_<field>` columns to a CSV.

Example:

```bash
python3 scripts/normalize_text.py \
  --input data/merchant_sample_template.csv \
  --output data/processed/merchants_normalized.csv \
  --fields shop_name,merchant_description,menu_item_names,recommended_dishes,platform_tags
```

### `scripts/score_taiwaneseness.py`

Scores selected text fields with the Taiwaneseness lexicon.

Example:

```bash
python3 scripts/score_taiwaneseness.py \
  --input data/merchant_sample_template.csv \
  --output data/processed/merchants_scored.csv \
  --text-fields shop_name,merchant_description,menu_item_names,recommended_dishes,platform_tags
```

### `scripts/calculate_gap.py`

Calculates merchant-review Consumer Reinterpretation Gap.

Example:

```bash
python3 scripts/calculate_gap.py \
  --merchants data/processed/merchants_scored.csv \
  --reviews data/processed/reviews_scored.csv \
  --output outputs/consumer_reinterpretation_gap.csv
```

### `scripts/fetch_sources.py`

Fetches public URLs only when robots checks allow access. It does not bypass login, captcha, or anti-bot mechanisms.

Example:

```bash
python3 scripts/fetch_sources.py \
  --sources data/data_log_template.csv \
  --output-dir data/raw/fetched_pages \
  --log data/data_log_fetches.csv
```

## Publication-Ready Methods Wording

The study uses a computational-first mixed-method design. Merchant and consumer texts are collected into source-logged CSV files, normalized with a scripted pipeline, and scored with a versioned Taiwaneseness lexicon. The lexicon measures five semantic domains: geographic origin, nostalgia, night-market imagery, authenticity, and platform fast-food value. Merchant and review scores are then compared through a Consumer Reinterpretation Gap, defined as the difference between merchant domain density and the mean review-domain density for the same merchant. A small validation audit is used not as the primary measurement procedure but to estimate false positives, false negatives, and ambiguous cases in the automated lexicon.

