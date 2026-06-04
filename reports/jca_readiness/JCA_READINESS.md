# JCA Readiness Report

This local report turns existing outputs into a paper-oriented evidence chain.

## Counts

- Candidate figures inventoried: 32
- Tables/results inventoried: 89
- Sample-size gate rows: 493
- Main-text candidate figures: 9
- Anonymization risks found: 9

## Main-Text Figure Candidates

- `analysis/semantic_propagation_live_outputs/figures/change_point_candidate_map.png`: Corridor-specific source and semantic regime shifts; use to argue against a single global turning point.
- `analysis/semantic_propagation_live_outputs/figures/change_points_taiwan_source_structure.png`: Taiwan-side evidence visibility changes by source structure; use to show archive/source-system change.
- `analysis/semantic_propagation_live_outputs/figures/weak_binding_share_heatmap.png`: Where weak/no-binding cases cluster by period and corridor.
- `analysis/semantic_propagation_live_outputs/figures/low_binding_time_corridor_heatmap.png`: Weak-binding pockets across time and geography; use as control evidence, not noise.
- `analysis/semantic_propagation_live_outputs/figures/first_appearance_timeline.png`: First observed appearances by semantic family and corridor; exploratory timing evidence.
- `analysis/semantic_propagation_live_outputs/figures/leave_one_source_type_out.png`: Sensitivity to source regimes; use to show which evidence systems inflate or suppress binding.
- `analysis/semantic_propagation_live_outputs/figures/low_binding_pockets.png`: Largest period/corridor/source pockets where attachment is weak.
- `analysis/semantic_propagation_live_outputs/figures/semantic_family_by_corridor.png`: Different corridors assemble Taiwaneseness through different semantic families.
- `analysis/semantic_propagation_live_outputs/figures/semantic_family_over_time.png`: Shift from dish attestation toward cuisine/platform labels over time.

## Sample-Size Caution

- Sparse cells marked `do_not_infer`: 362
- Cautious/context cells: 105

Use `sample_size_gate.csv` before making any corridor/time/family claim. The default rule is:

- `main_text_ok`: n >= 30 and at least 5 unique sources when available.
- `main_text_cautious`: n >= 15 and at least 3 unique sources when available.
- `appendix_or_case_context`: n >= 5.
- `do_not_infer`: n < 5.

## Proposed Evidence Chain

1. Define the object as marker binding, not culinary authenticity.
2. Establish corpus/source regimes and evidence gates.
3. Show that shifts are corridor-specific rather than a single global event.
4. Use Taiwan-side source structure to show that evidence visibility changes.
5. Use semantic-family heatmaps to show different assemblies of Taiwaneseness by corridor.
6. Use low-binding controls to distinguish Taiwan-related discourse from attached dish signs.
7. Use source sensitivity and authority/novelty figures as robustness diagnostics.

## Immediate Manuscript Risk

For double-anonymous review, do not cite the public GitHub repository or include author-identifying paths. Build an anonymous replication package from the files listed here.
