# Literature Review and Publication Strategy

## Purpose

This document organizes the literature and publication strategy for the paper tentatively titled:

> Taiwaneseness as a Consumable Sign: A Multi-Layer Corpus Analysis of Platform-Mediated and Historical Food Discourse

The document is designed for the writing stage. It links each literature cluster to the project's hypotheses, corpus design, and methodological choices.

Important note: bibliographic details, journal metrics, and publisher guidance must be verified again before thesis submission or journal submission. This file records the current intellectual map, not a final formatted bibliography.

## Core Positioning

The project is not asking what Taiwanese lu rou fan "really is." It asks how dish markers and Taiwan markers become attached across different historical periods, evidence systems, ownership regimes, and consumer interfaces.

The central methodological choice is therefore:

- store `dish_marker` and `taiwan_marker` separately;
- measure when, where, and by whom they become bound;
- keep historical archive evidence, cross-strait mobility evidence, and post-2015 platform evidence in separate layers;
- allow each layer to support only the claims that its corpus health permits.

## Literature Cluster 1: Taiwanese Cuisine, National Cuisine, and Everyday Nationalism

### Chen Yu-Jen. The Cultural History of "Taiwanese Cuisine"

Suggested reference:

Chen, Yu-Jen. 2020. *The Cultural History of "Taiwanese Cuisine": The Embodiment of the Nation in Food Consumption*. Linking Publishing. Verify exact English title and citation format before submission.

Use in the paper:

Chen's work provides the theoretical starting point for asking how the "nationality" of a dish is produced. The project extends that question computationally: instead of treating Taiwanese lu rou fan as a stable object, it measures the historical attachment between a dish marker and a Taiwan marker.

Possible argument:

Chen asks how the "nationality" of a dish comes into being. This project turns that question into a corpus operation: `dish_marker` and `taiwan_marker` are stored separately and only later measured as a binding relation.

Best location:

- Introduction.
- Literature review section on Taiwanese food and national identity.
- Method section explaining why markers are separated.

### Chen Yu-Jen on Authenticity in Tokyo Taiwanese Restaurants

Suggested reference:

Chen, Yu-Jen. "The Construction of Authenticity: The Production, Representation and Transformation of Taiwanese Cuisine in Tokyo." Verify exact title, year, journal title, issue, and page numbers.

Use in the paper:

This work supports the project's producer-consumer tension. Chen's Tokyo case shows that authenticity is negotiated between producers' historical trajectories and consumers' touristic/media experiences. The current project asks how this negotiation changes when merchant self-description and consumer review language appear together inside digital platforms.

Connection to the project:

- Supports H4: consumer reviews may reproduce, transform, ignore, or reject merchant-produced Taiwan markers.
- Motivates `consumer_stance_classifier.py`.
- Justifies separating merchant-provided, platform-generated, and consumer-generated fields.

Best location:

- Literature review section on authenticity and consumer reinterpretation.
- Platform layer methodology.

### Chen Yu-Jen. "Bodily Memory and Sensibility"

Suggested reference:

Chen, Yu-Jen. 2010. "Bodily Memory and Sensibility: Culinary Preferences and National Consciousness in the Case of 'Taiwanese Cuisine'." Verify journal, volume, issue, and pages.

Use in the paper:

This source supports a caution: Taiwanese cuisine does not mean the same thing to all consumers, and preference for Taiwanese cuisine cannot be reduced to national consciousness. This helps prevent the project from over-reading every Taiwan marker as direct nationalist sentiment.

Connection to the project:

- Supports the need for consumer stance categories.
- Helps interpret no-mention and transformation categories as meaningful, not simply as "failed" Taiwaneseness.

### Chen Yu-Jen. "Ethnic Politics in the Framing of National Cuisine"

Suggested reference:

Chen, Yu-Jen. 2015. "Ethnic Politics in the Framing of National Cuisine: A Case Study of Taiwan." *Food and Foodways* 23(3): 163-180. Verify final citation.

Use in the paper:

This article supports the claim that Taiwanese cuisine is historically and politically framed rather than naturally given. It is also useful because it appeared in a likely target journal.

Connection to the project:

- Supports the 1987-2015 mobility/diffusion layer.
- Helps explain why post-1980s Taiwanese cuisine may become more legible as a category.

### Fu Yen-Chen on Taiwanese Cuisine Since the 1980s

Suggested reference:

Fu, Yen-Chen. 2015. "The Making of Taiwanese Cuisine since 1980s: The Rise of Minnan and Hakka Ethnic Food." *Asia Review* 5(1): 123-138. Verify citation.

Use in the paper:

Fu's argument that Taiwanese cuisine rose alongside democratization and increasing Taiwanese national consciousness supports the project's periodization. It is especially relevant to the 1987 boundary.

Connection to the project:

- Supports treating 1987 as a key transition point.
- Prevents interpreting low pre-1980s Taiwan-marker binding as simple absence.
- Supports the idea that the binding relation itself changes across political-historical conditions.

### Billig. Banal Nationalism

Suggested reference:

Billig, Michael. 1995. *Banal Nationalism*. London: Sage.

Use in the paper:

Billig provides the theoretical vocabulary for understanding everyday food labels as quiet national-symbolic cues. The paper should use this carefully: the project is not claiming every menu label is nationalism, but that food discourse can operate as a mundane site where national/place signs are repeatedly flagged.

Connection to the project:

- Supports the interpretation of Taiwan markers as everyday symbolic flags.
- Works especially well when paired with Chen Yu-Jen's use of Billig in food-history analysis.

## Literature Cluster 2: Historical and Corpus-Based Taiwanese Food Studies

### Hsu Yu-Chun on the History and Culture of Taiwanese Cuisine

Suggested reference:

Hsu, Yu-Chun. 2013. "A Study on the History and Culture of Taiwanese Cuisine." Master's thesis, Department of History, Tamkang University. Verify citation.

Use in the paper:

This work supports the claim that Taiwanese cuisine has no single stable definition and that its content shifts under different political regimes and culinary influences.

Connection to the project:

- Provides a historical background for treating Taiwaneseness as variable.
- Helps justify longitudinal corpus design.

### Tang Pei-Chun on Text Mining and Changhua Kong Rou Fan

Suggested reference:

Tang, Pei-Chun. 2019. "Using Text Mining to Explore Local Identification and Sustainable Management of Changhua Kong Rou Fan." Master's thesis, Chienkuo Technology University. Verify citation.

Use in the paper:

This is a useful methodological neighbor: it applies text mining to Taiwanese local food identity. The current project differs because it studies cross-regional/national symbolic mobility rather than local identity anchored in one place.

Connection to the project:

- Supports the food-text-mining precedent.
- Helps distinguish local food identity from mobile Taiwaneseness as a cross-context sign.

## Literature Cluster 3: Digital Humanities, Corpus Linguistics, and Distant Reading

### McGillivray and Toth

Suggested reference:

McGillivray, Barbara, and Gabor Mihaly Toth. 2020. *Applying Language Technology in Humanities Research: Design, Application, and the Underlying Logic*. Cham: Palgrave Macmillan.

Use in the paper:

This should be one of the core methods references. It supports the idea that computational humanities work is not just code; it is research design, transparency, and explicit limits of interpretation.

Connection to the project:

- Supports source registry, raw manifest, derived outputs, and health audit.
- Supports the distinction between computational output and researcher interpretation.

### Moretti. Distant Reading

Suggested reference:

Moretti, Franco. 2013. *Distant Reading*. London: Verso.

Use in the paper:

Moretti provides the classic distant-reading frame. The project combines distant reading with close verification: binding indices reveal macro-patterns, while `verification_level` and source windows preserve close-reading accountability.

Connection to the project:

- Supports lexical and historical binding indices.
- Helps describe the loop between automated extraction and human verification.

### FoodImagine Corpus Methodology

Suggested reference:

FoodImagine Project. "Corpus." https://foodimagine.org/corpus-2-2/. Verify current URL and access date.

Use in the paper:

FoodImagine is a useful parallel case for combining close reading and distant reading in food-related textual analysis.

Connection to the project:

- Supports the project's combined method: automated pattern detection plus source-window verification.

### Xu Tongyang and Wang Xia on Corpus Linguistics and Digital Humanities

Suggested reference:

Xu, Tongyang, and Wang, Xia. 2021. "Data-Driven Digital Humanities Research from the Perspective of Corpus Linguistics: A Case Study of Digital Humanities Quarterly." *Library Tribune*. Verify Chinese title, issue, and pages.

Use in the paper:

This source supports the project's corpus-driven posture: pilot observations generate hypotheses, which are then tested through systematic corpus expansion.

Connection to the project:

- Supports H1-H7 as a hypothesis-generation and hypothesis-testing cycle.
- Helps define the project as data-driven rather than purely theory-driven.

### Huang Shuiqing and Wang Dongbo on Corpus Research

Suggested reference:

Huang, Shuiqing, and Wang, Dongbo. 2021. "A Review of Corpus Research in China." *Journal of Information Resources Management* 11(3): 4-17. Verify citation.

Use in the paper:

This source supports deep annotation and quality control as part of corpus construction.

Connection to the project:

- Supports `verification_level`, dedupe keys, health grading, and source traceability.
- Helps frame the project as a deeply annotated knowledge resource, not a simple word-frequency table.

### Quantitative Intertextuality

Suggested references:

Forstall, C. W., and Scheirer, W. J. 2019. "What is Quantitative Intertextuality?" In *Quantitative Intertextuality: A Computational Approach to Literary Analysis*. Springer. Verify full details.

Duan, Siyu. 2025. "Quantitative Intertextuality from the Digital Humanities Perspective: A Survey." arXiv. Verify status and whether it should be cited as peer-reviewed or preprint.

Use in the paper:

These works can provide theoretical language for cross-textual similarity without direct quotation or borrowing. The project is not tracing direct citation. It is measuring whether Taiwan-associated lexical patterns appear across different textual systems.

Connection to the project:

- Supports lexical proximity and cross-system semantic binding.
- Useful for the section on semantic attachment and cross-context textual flow.

## Literature Cluster 4: Digital Food Studies and Platform Food Discourse

### Leer and Krogager. Research Methods in Digital Food Studies

Suggested reference:

Leer, Jonatan, and Stinne Gunder Strom Krogager, eds. 2021. *Research Methods in Digital Food Studies*. Routledge. Verify exact publisher details.

Use in the paper:

This book positions the platform layer within digital food studies. It is useful for justifying restaurant-review analysis, platform text analysis, and the need to account for platform bias.

Connection to the project:

- Supports merchant/review separation.
- Supports platform-generated field labeling.
- Helps explain why platform evidence must be phase-separated from archival evidence.

### Lin, Huang, and Chen on Ethnic Congruence

Suggested reference:

Lin, C. H., Huang, Y. C., and Chen, M. F. 2024. "How ethnic congruence affects authenticity and perceived taste of traditional foods." *British Food Journal*. Verify volume, issue, pages, and exact title before citation.

Use in the paper:

This study supports the behavioral plausibility of ethnic/region markers affecting perceived authenticity and taste. It should be used as motivation, not as direct proof of platform behavior.

Connection to the project:

- Supports H4 and consumer stance analysis.
- Motivates testing whether consumers reproduce merchant Taiwan markers.

### Lin Pei-Yin on Bubble Tea in Vietnam

Suggested reference:

Lin, Pei-Yin. 2022. "Food Nationalism beyond Tradition: Bubble Tea and the Politics of Cross-border Mobility between Taiwan and Vietnam." *Asian Journal of Social Science*. Verify volume, issue, and pages.

Use in the paper:

This article provides a strong comparative frame: Taiwanese food symbols can be mobile materially while remaining symbolically anchored to Taiwan.

Connection to the project:

- Supports H7 and overseas translation layers.
- Helps compare mainland, Vietnam, and broader cross-border cases.

### Johnston and Baumann. Foodies

Suggested reference:

Johnston, Josee, and Shyon Baumann. 2015. *Foodies: Democracy and Distinction in the Gourmet Foodscape*. 2nd ed. Routledge.

Use in the paper:

This source supports the role of authenticity as a cultural distinction device. It can help theorize why "authentic," "old taste," or "night market" language may function as a consumer-facing value signal.

Connection to the project:

- Supports authenticity and nostalgia marker domains.
- Useful in discussion rather than core methods.

### Platform Visibility and Algorithmic Mediation

Suggested reference:

Chang, A. Y. 2025. "Food as Soft Power: Taiwanese Gastrodiplomacy on Social Media and Algorithmic Suppression." arXiv:2511.05729. Verify existence, authorship, and suitability before citation.

Use in the paper:

If verified, this source may support the claim that Taiwan-related food visibility can be platform-mediated and algorithmically shaped. It should be treated as platform-method context, not historical evidence.

Connection to the project:

- Supports separating post-2015 platform data from archival evidence.
- Supports platform-bias audit and sensitivity analysis.

## Self-Positioning Paragraph Draft

The existing literature identifies three related but still insufficiently connected research spaces. First, studies of Taiwanese cuisine have shown that "Taiwanese cuisine" is historically constructed rather than naturally given, and that authenticity is negotiated between producers, consumers, and political-cultural contexts. Second, digital humanities and corpus linguistics provide tools for distant reading, deep annotation, and reproducible text analysis, but these methods have rarely been applied to the long-run semantic formation of food-place markers. Third, digital food studies and consumer research show that platform interfaces and ethnic markers shape food perception, yet they often focus on contemporary platform or experimental settings rather than the historical formation of the markers themselves. This study connects these spaces by treating Taiwaneseness not as an assumed property of a dish, but as a measurable relation between `dish_marker` and `taiwan_marker` across historical archives, mobility records, ownership events, platform merchant texts, and consumer reviews.

## Target Journal Strategy

### First-Tier Targets

#### Food and Foodways

Fit:

- Strong fit for food, culture, identity, national cuisine, and historical-cultural interpretation.
- Especially appropriate if the empirical paper emphasizes Taiwanese cuisine, cross-strait food signs, and social-cultural interpretation.

Submission strategy:

- Emphasize historical-cultural contribution.
- Cite Chen Yu-Jen's work in the journal where relevant.
- Keep methods transparent but do not let code architecture dominate the narrative.

Before submission:

- Verify current aims and scope.
- Verify article length, formatting, open access options, and review workflow.

#### Asian Journal of Social Science

Fit:

- Strong fit for regional Asian social and cultural analysis.
- Appropriate if the paper foregrounds cross-border symbolic mobility, China-Taiwan cultural circulation, and platform-mediated consumer discourse.

Submission strategy:

- Emphasize regional theory and cross-context comparison.
- Keep the computational apparatus readable for a broader social science audience.

Before submission:

- Verify publisher, submission portal, article length, and recent related publications.

#### International Journal of Humanities and Arts Computing

Fit:

- Strong fit for the methodology paper.
- Appropriate if the first paper focuses on corpus engineering, binding indices, audit gates, source traceability, and historical food semantics.

Submission strategy:

- Emphasize reproducible corpus architecture.
- Frame the case study as a humanities computing problem with substantive food-history payoff.

Before submission:

- Verify article length and technical expectations.

### Additional Targets

- *Digital Humanities Quarterly*: good for the corpus engineering and audit-gate paper.
- *Digital Scholarship in the Humanities*: higher-competition digital humanities target.
- *Discourse Studies*: possible if consumer stance and platform discourse become central.
- *Gastronomica*: possible for a more essayistic cultural-food version.
- *Computational Culture*: possible if computational/platform mediation becomes the theoretical center.

## Conference Strategy

Possible venues:

- Asia-Pacific Digital Humanities Conference.
- Association for Asian Studies or regional Asian studies conferences.
- Cultural studies conferences with food/media panels.
- Digital humanities conferences where reproducibility and corpus construction are valued.

Use conferences to test:

- whether the marker-binding concept is clear;
- whether the health-audit logic is persuasive;
- whether reviewers see the work as food studies, Asian studies, or digital humanities.

## Publication Split Strategy

### Paper 1: Methodology / Corpus Engineering

Possible title:

> Auditing Historical Food Semantics: A Corpus Engineering Framework for Measuring Taiwaneseness in Food Discourse

Best targets:

- International Journal of Humanities and Arts Computing.
- Digital Humanities Quarterly.
- Digital Scholarship in the Humanities.

Core contribution:

- source registry;
- raw manifest;
- negative-search logs;
- verification levels;
- temporal and geographic health gates;
- marker-binding indices.

### Paper 2: Empirical Cultural Analysis

Possible title:

> Taiwaneseness as a Consumable Sign: Lu Rou Fan, Cross-Strait Food Mobility, and Platform-Mediated Authenticity

Best targets:

- Food and Foodways.
- Asian Journal of Social Science.
- Discourse Studies, if platform reviews become central.

Core contribution:

- historical binding patterns;
- post-1987 mobility;
- ownership/capital interpretation;
- consumer stance and platform mediation.

## Data Ethics and Reproducibility Statement

The project should include:

- a public code repository when the thesis/paper is ready;
- a codebook explaining every generated field;
- anonymization for consumer review data;
- platform-terms and access-method statement;
- source-access limitations for restricted archives;
- public release of only legally shareable data slices;
- FAIR-inspired documentation, while recognizing that some historical sources are restricted or subscription-based.

## Research Plan Paragraph

This study is designed with journal publication as a target output. Based on the thematic scope of food studies, digital humanities, and Asian cultural studies journals, the project may generate two separable contributions: first, a methodology-focused paper on corpus health auditing and marker-binding measurement for historical food semantics; second, an empirical paper on Taiwaneseness as a cross-border consumable sign in food discourse. To ensure replicability and transparency, the corpus pipeline records source registries, search logs, raw capture manifests, deduplicated attestations, and claim-permission flags. Platform-derived merchant and review data are phase-separated from historical archive evidence, and only anonymized, legally shareable data slices will be released publicly.

