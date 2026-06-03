# Spatial-Temporal Diffusion Design

## Why This Module Matters

The claim that Taiwaneseness is commodified and reinterpreted on mainland platforms is plausible, but by itself it risks being too expected. A stronger empirical contribution asks where this commodified Taiwaneseness travels, through which urban corridors, and whether its meaning changes as it moves.

This module reframes the project around spatial-temporal diffusion:

> How does "Taiwanese lu rou fan" diffuse across mainland China, and does its geography follow Yangtze River Delta urban circuits, broader coastal/cross-strait cultural corridors, or inland fast-casual platform expansion?

## Core Research Questions

1. Does Taiwanese lu rou fan in mainland China concentrate first in Shanghai and the Yangtze River Delta?
2. Is the category more broadly coastal, especially in cities with stronger Taiwan/Hong Kong/Fujian/Guangdong food-culture links?
3. Does recent expansion show inland penetration through shopping-mall, chain, and platform fast-food formats?
4. Does the semantic profile of Taiwaneseness change by region?

## Spatial Hypotheses

### H-GEO1: Yangtze River Delta Gateway Hypothesis

Taiwanese lu rou fan first becomes visible as a scalable mainland commercial category through Shanghai and nearby Yangtze River Delta cities such as Nanjing, Suzhou, Wuxi, Hangzhou, Ningbo, and Changzhou.

Expected evidence:

- early opening years or first attestations in Shanghai/YRD;
- high store counts in Shanghai, Jiangsu, and Zhejiang;
- strong mall/office-lunch platformization;
- merchant language mixing Taiwan authenticity with fast-casual value.

### H-GEO2: Coastal-Corridor Hypothesis

The category is not only YRD-centered but also follows coastal and cross-strait cultural/economic corridors: Fujian, Guangdong, Shenzhen, Xiamen, Fuzhou, and possibly Guangzhou.

Expected evidence:

- meaningful presence in coastal cities outside the YRD;
- stronger geographic/authenticity Taiwaneseness;
- more references to Taiwan proximity, Taiwanese founders, or cross-strait food culture.

### H-GEO3: Inland Platformization Hypothesis

Recent expansion into inland cities is driven less by geographic proximity to Taiwan and more by standardized fast-casual, mall-based, delivery-friendly formats.

Expected evidence:

- later first-observed dates in inland cities;
- high share of planned or mall-based stores;
- stronger platform fast-food domain scores;
- weaker geographic or authenticity scores relative to coastal/YRD cases.

### H-GEO4: Semantic Dilution / Translation Hypothesis

As the category moves inland, Taiwaneseness may shift from origin/authenticity to format/value: "Taiwan" becomes less a place of culinary authenticity and more a label for a standardized rice-bowl product.

Expected evidence:

- declining geographic/authenticity scores by distance or by inland status;
- increasing platform_fast_food scores in inland and lower-tier expansion contexts;
- consumer reviews emphasizing value, portion, and convenience over Taiwan.

## Data Structure

### City Metadata

Each city receives stable metadata:

- province
- macro region
- corridor label
- coastal or inland
- approximate latitude/longitude
- distance to Taipei or Xiamen, if useful
- city tier, if using a documented classification

### Brand-City Presence

Each observation records a brand's presence in a city or province:

- brand
- city
- province
- observation date
- first observed year
- open store count
- planned store count
- source URL
- source type
- confidence

The first stage can use city-level observations. Later stages can move to store-level observations with address geocoding.

## Suggested Data Sources

### Stronger Sources

- official brand store locator pages;
- archived brand pages;
- public restaurant listing pages;
- industry reports with dated store counts;
- business-registration databases, if access and licensing permit;
- source-logged manual platform searches.

### Weaker / Contextual Sources

- lifestyle media;
- food blogs;
- social media posts;
- consumer screenshots;
- opaque platform rankings.

These can support interpretation but should not be the primary quantitative backbone.

## Metrics

### City Presence

```text
city_presence = 1 if brand/category observed in city
```

### Store Count

```text
total_stores = open_store_count + planned_store_count
```

Keep open and planned stores separate. Planned stores indicate expansion intention, not realized consumer presence.

### Corridor Share

```text
corridor_share = corridor_store_count / total_store_count
```

Calculate separately for open, planned, and total stores.

### Inland Penetration Index

```text
inland_penetration = inland_store_count / total_store_count
```

Track this by observation date or first observed year.

### YRD Concentration Index

```text
yrd_concentration = yrd_store_count / total_store_count
```

If high at early observations but declining over time, this supports a gateway-then-diffusion model.

### Semantic-Regional Profile

Merge spatial data with Taiwaneseness scores:

```text
mean_domain_score(region, domain)
```

Domains:

- geographic
- nostalgia
- night_market
- authenticity
- platform_fast_food

## Interpretation Rules

1. Do not infer opening year from a current store-list page unless the page explicitly gives the year.
2. Treat "planned" stores separately from "open" stores.
3. Treat media-reported counts as claims from a source, not ground truth.
4. Distinguish brand diffusion from category diffusion. 阿元来了 may diffuse differently from the broader "Taiwanese lu rou fan" category.
5. A spatial pattern is meaningful only when source coverage bias is addressed.

## Paper Contribution

This module can turn the project from a general semiotic/platform argument into a historical-geographic argument:

> Taiwanese lu rou fan in mainland China is not merely a commodified Taiwan sign. Its commodification has a geography. The dish-label appears to move through specific urban circuits, especially Shanghai/YRD commercial corridors, broader coastal food-culture channels, and later inland mall/platform expansion. As it moves, Taiwaneseness may shift from origin and authenticity to value, standardization, and fast-casual convenience.

