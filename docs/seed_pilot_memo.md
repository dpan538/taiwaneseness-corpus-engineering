# Seed Pilot Memo

## Purpose

This seed pilot tests whether the computational pipeline can turn public merchant and consumer-facing text into measurable Taiwaneseness indicators. It is not yet a representative sample. Its purpose is to stress-test the data structure, lexicon, scoring script, and Consumer Reinterpretation Gap calculation before scaling.

## Seed Corpus

Files:

- `data/seed_merchants.csv`
- `data/seed_reviews.csv`
- `data/seed_source_log.csv`
- `data/processed/seed_merchants_scored.csv`
- `data/processed/seed_reviews_scored.csv`
- `outputs/seed_consumer_reinterpretation_gap.csv`

Seed size:

- 9 merchant/media records
- 5 consumer-facing review/blog records

Current source types:

- brand page
- restaurant listing
- food blog
- media report
- industry report

## First-Pass Result

The seed scorer successfully detects binding between dish markers and Taiwan markers in 8 of 9 merchant records before English expansion, and 9 of 9 after English expansion. The one initially missed case was an English-language source for Sandian using terms such as "Taiwanese," "luroufan," and "great value." This showed that the lexicon needed cross-lingual expansion rather than only Chinese terms.

After lexicon expansion, the Sandian source is detected as:

- dish markers: `luroufan`, `Taiwanese braised pork rice`
- Taiwan markers: `Taiwanese`
- domain signal: geographic, night-market/street-food, and platform fast-food/canteen value

## Emerging Pattern

The seed data already suggests a usable hypothesis:

> Merchant and media discourse often stages Taiwaneseness through geographic origin, night-market imagery, authenticity, and script/style cues, while consumer-facing review language often shifts toward value, queueing, convenience, portion, and fast lunch use.

This is visible most clearly in the Trip.com seed data for 捡角台湾食堂:

- merchant/listing text contains Taiwan-category, traditional-script, night-market, and authenticity cues;
- review examples contain some Taiwan references, but also emphasize price, queueing, value, and practical consumption.

## Methodological Lessons

### 1. CSV Must Be Quoted Carefully

Long prose fields often contain commas. The scripts now preserve overflow fields as `_extra_fields`, but future collection should either:

- quote all prose fields correctly in CSV; or
- move collection records to JSONL and export clean CSV only for analysis.

### 2. The Lexicon Must Be Cross-Lingual

English-language sources can be analytically useful, especially for Shanghai food blogs and international restaurant listings. The lexicon now includes:

- `Taiwanese`
- `Taiwan`
- `Formosa`
- `luroufan`
- `Taiwanese braised pork rice`
- `street food`
- `night market`
- `canteen`
- `great value`

### 3. Script Is Both Signal and Noise

Traditional script improves detection of Taiwan-staging, but it cannot be treated as automatically Taiwanese. It should remain a separate cue and be interpreted with lexical and visual context.

### 4. Human Coding Should Be an Audit, Not the Main Measurement

The next validation step should not replace the automated scoring. Instead, it should audit false positives, false negatives, and ambiguous cases in the lexicon.

## Next Scaling Step

The next real step should be a structured 30-case Shanghai seed expansion:

1. 10 direct merchant or brand pages.
2. 10 public restaurant listing pages.
3. 10 media/blog/industry report records.

For each case, record:

- source URL
- capture date
- source type
- shop/brand name
- city
- merchant description or listing text
- menu item names
- recommended dishes
- script/visual notes

Then run:

```bash
python3 scripts/score_taiwaneseness.py \
  --input data/seed_merchants.csv \
  --output data/processed/seed_merchants_scored.csv \
  --text-fields shop_name,platform_tags,merchant_description,menu_item_names,recommended_dishes,script_cue,visual_cue,notes

python3 scripts/score_taiwaneseness.py \
  --input data/seed_reviews.csv \
  --output data/processed/seed_reviews_scored.csv \
  --text-fields review_text,notes

python3 scripts/calculate_gap.py \
  --merchants data/processed/seed_merchants_scored.csv \
  --reviews data/processed/seed_reviews_scored.csv \
  --output outputs/seed_consumer_reinterpretation_gap.csv
```

