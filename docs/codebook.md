# Taiwaneseness Codebook

## Coding Units

### Merchant Texts

A merchant coding unit may be:

- shop name
- branch name
- merchant description
- menu item name
- recommended dish name
- platform tag
- paragraph from a brand website or franchise page

### Consumer Texts

A consumer coding unit is usually one review. Do not split a review into smaller fragments unless the memo explains why the review contains multiple analytically distinct claims.

## Coding Principles

1. One text may belong to multiple Taiwaneseness domains.
2. Code the presence of a domain, not whether the claim is factually authentic.
3. Preserve negation and irony. For example, "this is not Taiwanese at all" still counts as Taiwaneseness being invoked, but the interpretation direction is rejection.
4. Visual cues such as traditional script, vertical text, maps of Taiwan, night-market imagery, or Taiwan landmarks should be recorded separately from lexical cues.
5. Always preserve `original_text`. Use `normalized_text` only for search, matching, and counting.

## Domain 1: Geographic Taiwaneseness

Definition: the text links the dish, shop, brand, founder, ingredient, or flavor explicitly to Taiwan as a place or source.

Positive examples:

- 台湾卤肉饭
- 台式卤肉饭
- 来自台湾
- 台湾老板
- 宝岛风味
- 台湾小吃
- 台湾夜市美食

Boundary cases:

- Code "台式" as geographic in the first pass, but mark an uncertainty note if it appears to function as a generalized style label.
- "台味" may be coded as geographic and nostalgia if both meanings are active.

## Domain 2: Nostalgic Taiwaneseness

Definition: the text frames Taiwaneseness through old taste, childhood, home cooking, memory, or affective return.

Positive examples:

- 古早味卤肉饭
- 小时候的味道
- 阿嬷的味道
- 老台湾味
- 传统家常味

Boundary cases:

- "家常" is not automatically Taiwanese. Code it only when it appears in a Taiwan / Taiwanese-style / lu rou fan context.
- "古早味" may be a generic commercial nostalgia term. Mark uncertainty when its Taiwan-specific force is unclear.

## Domain 3: Night-Market Taiwaneseness

Definition: the text frames Taiwaneseness through night markets, snacks, street food, Shilin, or tourism-style food bundles.

Positive examples:

- 台湾夜市
- 夜市小吃
- 士林风味
- 大肠包小肠 plus lu rou fan set meals
- salted crispy chicken, oyster omelet, or bubble tea bundled with lu rou fan

Boundary cases:

- Do not code "fast food" as night-market Taiwaneseness unless night market, street snack, or tourist-snack cues are present.

## Domain 4: Authenticity Taiwaneseness

Definition: the text produces authenticity through words such as authentic, traditional, original, handmade, old method, origin, Taiwanese chef/founder, traditional script, vertical text, or a Taiwan-related origin story.

Positive examples:

- 正宗台湾卤肉饭
- 原汁原味台式风味
- 台湾师傅
- 古法慢炖
- 手工熬制
- traditional script used to intensify a Taiwanese style

Boundary cases:

- "正宗" is not automatically Taiwaneseness. Code it only when it modifies Taiwan, Taiwanese style, lu rou fan, or another relevant object.
- Traditional script is not automatically Taiwaneseness. Record it as a script cue and assess it in context.

## Domain 5: Platform Fast-Food Taiwaneseness

Definition: Taiwaneseness is packaged as a platformized, standardized, affordable, delivery-friendly, or fast-casual meal format.

Positive examples:

- 一人食卤肉饭
- 台式便当
- 9.9 卤肉饭
- 出餐快
- 高性价比
- 外卖爆款
- 连锁加盟台湾卤肉饭

Boundary cases:

- "cheap," "fast," or "convenient" is not Taiwaneseness by itself. Code this domain only when those terms are attached to Taiwan / Taiwanese style / lu rou fan in the sample.

## Consumer Interpretation Codes

In addition to the five domains, consumer reviews should receive an interpretation-direction code.

### accept

The consumer repeats or endorses merchant-produced Taiwaneseness.

Example: "It tastes like authentic Taiwanese flavor."

### transform

The consumer translates Taiwaneseness into another consumption logic, such as value, convenience, portion size, or ordinary lunch.

Example: "It says Taiwanese lu rou fan, but for me it is mostly a cheap and filling weekday lunch."

### ignore

The consumer evaluates taste, price, service, portion, or convenience without mentioning Taiwaneseness.

### reject

The consumer explicitly denies or questions the Taiwanese claim.

Example: "This does not taste like the lu rou fan I had in Taiwan."

### compare

The consumer compares the shop with Taiwan, another city, another brand, or a travel memory.

Example: "It is different from what I ate at a Taipei night market, but still acceptable."

## Recommended Columns

Merchant table:

```text
merchant_id, city, platform, shop_name, source_url, capture_date,
geographic, nostalgia, night_market, authenticity, platform_fast_food,
script_cue, visual_cue, uncertainty_note
```

Review table:

```text
review_id, merchant_id, review_date, rating, review_text, capture_date,
geographic, nostalgia, night_market, authenticity, platform_fast_food,
consumer_interpretation, uncertainty_note
```

Use binary 0/1 domain coding for the pilot. Consider intensity scores only after the codebook becomes reliable.

