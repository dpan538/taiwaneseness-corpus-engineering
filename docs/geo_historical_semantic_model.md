# Geo-Historical Semantic Model

## Core Idea

The project should not treat geography and history as separate background variables. The stronger model is progressive:

> The geography of diffusion shapes the historical transformation of meaning.

In other words, "Taiwanese lu rou fan" may not carry the same Taiwaneseness in every place or period. Its meaning changes as it moves through specific urban circuits: early Shanghai/YRD Taiwanese dining, coastal/cross-strait food-culture corridors, and later inland mall/platform expansion.

## Two Analytical Layers

### Layer 1: Geographical Diffusion

This layer asks where the category appears and spreads.

Variables:

- city
- province
- corridor
- coastal/inland status
- brand/category presence
- open stores
- planned stores
- source confidence

Main question:

> Is Taiwanese lu rou fan primarily a Shanghai/YRD phenomenon, a broader coastal/cross-strait phenomenon, or a nationally platformized fast-casual format?

### Layer 2: Historical Semantic Regime

This layer asks what Taiwaneseness means in each period.

Possible regimes:

1. **Separated Food-Memory Regime, 1950-1978**: lu rou fan develops mainly in Taiwan-side memory, migration, recipe, and local-food discourse, while mainland circulation is structurally limited.
2. **Reopening / Latent Contact Regime, 1979-1987**: mainland reform and opening begin, but everyday cross-strait food commerce remains limited.
3. **Cross-Strait Mobility Regime, 1988-2001**: travel, investment, and media contact make Taiwan food more legible, but lu rou fan is not yet a dominant mainland platform commodity.
4. **Taiwan-Capital Casual-Dining Gateway Regime, 2002-2013**: Taiwan-linked restaurant chains enter through Shanghai/YRD and major commercial districts.
5. **Hong Kong/Taiwan Authenticity Regime, 2014-2020**: Taiwaneseness is staged through founder/chef origin stories, night-market food, and authenticity claims.
6. **Mainland Platform Transition Regime, 2021-2023**: mainland-origin Taiwan-themed brands narrow Taiwanese cuisine into rice bowls, snacks, and chainable lunch formats.
7. **Lu Rou Fan Wanghong Boom Regime, 2024-2025**: lu rou fan becomes a specialized rice-bowl category shaped by value pricing, mall expansion, platform visibility, award authority, and prepared-food standardization tensions.

Main question:

> How does the semantic profile of Taiwaneseness change as the category moves from gateway cities to coastal corridors and inland platforms?

## Progressive Relationship

The relationship between the two layers can be stated as:

```text
historical period -> dominant geography -> commercial format -> semantic regime
```

Example:

```text
1950-1978 -> Taiwan-side food memory -> no mainland platform commodity
-> lu rou fan as local Taiwanese dish and memory object
```

```text
2002-2013 -> Shanghai/YRD gateway -> Taiwan-linked casual dining chain
-> Taiwaneseness as modern urban leisure and brandable Taiwanese cuisine
```

```text
2024-2025 -> Shanghai/YRD + wanghong/mall expansion
-> lu rou fan specialty chains and affordable rice-bowl formats
-> Taiwaneseness as authenticity claim plus platform fast-food value
```

## Research Hypotheses

### H1: Longue-Duree Semantic Narrowing

From 1950 to 2025, the relevant sign shifts from Taiwan-side lu rou fan/local-food discourse, to broad Taiwanese cuisine in mainland urban chains, to a narrower lu rou fan specialty commodity.

### H2: Gateway Sequencing

Taiwanese food categories enter mainland commercial discourse first through Shanghai and the Yangtze River Delta, where Taiwaneseness is framed as modern urban dining, leisure consumption, and scalable chain management.

### H3: Capital-Origin Shift

The capital and operator structure changes over time: early mainland diffusion is more closely tied to Taiwan-linked capital and joint ventures; recent lu rou fan expansion is more likely to involve Hong Kong intermediary branding, mainland-origin Taiwan-themed operators, commercial real estate, and platform/wanghong economics.

### H4: Category Narrowing

Over time, the broader category of "Taiwanese cuisine" narrows into more specific platform-friendly items such as lu rou fan, salt-crispy chicken, night-market snacks, and Taiwanese bento/rice-bowl formats.

### H5: Semantic Shift by Geography

YRD/coastal cases are more likely to preserve geographic, authenticity, and night-market Taiwaneseness, while inland expansion cases are more likely to emphasize platform fast-food value, mall presence, speed, price, and standardization.

### H6: Authenticity Tension

As lu rou fan becomes a chainable mainland product, authenticity rhetoric may intensify at the same time that operational standardization increases. The result is not the disappearance of authenticity but a new tension between "authentic Taiwan flavor" and prepared/scalable chain production.

### H7: Planned Inland Expansion as Future Semantics

Planned stores in inland cities should not be treated as realized consumer diffusion, but they are evidence of commercial intention. They can be used to identify where the category is expected to travel next and what semantic packaging accompanies that expansion.

## Measures

### Historical Attestation

Earliest dated source for a brand/category/city combination.

```text
first_attestation_year(city, brand/category)
```

### Corridor-Period Presence

Presence count by corridor and historical period.

```text
presence_count(period, corridor)
```

### Corridor-Period Store Count

Open and planned stores aggregated by corridor and period.

```text
open_store_count(period, corridor)
planned_store_count(period, corridor)
```

### Semantic Domain by Corridor and Period

Mean Taiwaneseness domain score by corridor and period.

```text
mean_domain_score(period, corridor, domain)
```

Domains:

- geographic
- nostalgia
- night_market
- authenticity
- platform_fast_food

### Semantic Transition

Difference in mean domain score between periods.

```text
semantic_transition(domain) = mean_score(period_2, domain) - mean_score(period_1, domain)
```

## Interpretation

The model does not assume that Taiwaneseness simply weakens over distance. A more interesting possibility is that it changes form:

- in gateway cities, Taiwaneseness may appear as culinary novelty, modern chain dining, or authenticity;
- in coastal/cross-strait corridors, it may retain stronger geographic and cultural-proximity meanings;
- in inland cities, it may become a mall/platform format whose Taiwanese label organizes value, convenience, and standardized taste.

This is the key theoretical payoff: **spatial movement produces semantic translation**.
