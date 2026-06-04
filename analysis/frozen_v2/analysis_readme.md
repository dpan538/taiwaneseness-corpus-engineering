# Frozen V2 Macro Analysis Pack

## Core Status
- Records analysed: **1965**
- Overall weighted binding index: **0.963**
- Weighted positive rate: **96.3%**
- Source traceability: **100.0%**
- Authority distribution: `{'tertiary': 1230, 'primary': 467, 'secondary': 268}`

## Suggested Evidence Chain
1. Start with corpus structure and traceability, using `01_corpus_overview_metrics.csv` and Figures 01-03.
2. Treat Taiwan-side 1946-1987 as a saturation case, not as a statistically rising trend. Use `05_taiwan_historical_5year_saturation.csv` and Figure 04.
3. Move the empirical contrast to corridors and diffusion windows. Use `06_overseas_diffusion_5year_metrics.csv`, `07_corridor_first_appearance_and_binding.csv`, and Figures 05-06.
4. Use target positive/control records as a sensitivity layer, not as a full causal model. Use Tables 14-15 and Figure 11.
5. Use authority/source-type sensitivity to show why tourism and retrospective records are down-weighted. Use Tables 03-04 and Figure 07.
6. Use nostalgia marker tables as the bridge into the platform/commodity-sign chapter. Use Table 08 and Figure 08.
7. Because the positive trend is saturated, move the analysis from trend detection to exception analysis: low-binding pockets, weak controls, and leave-one-source-type-out sensitivity. Use Tables 19-25 and Figures 12-15.
8. For semantic propagation, combine time, geography, semantic family, Taiwan-marker frame, and discourse frame. Use Tables 26-31 and Figures 16-19.

## Important Method Note
`weighted_historical_binding` is already a weighted contribution. Aggregation should use `sum(weighted_historical_binding) / sum(analysis_weight)`, not multiply by `analysis_weight` again.
