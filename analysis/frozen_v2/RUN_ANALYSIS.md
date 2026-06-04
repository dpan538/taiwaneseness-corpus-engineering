# Running the Frozen V2 Analysis

Use the live-code notebook for interactive analysis. The generated SVG pack is
only a convenient export layer.

## Project Environment

This project has a local virtual environment:

```bash
.venv/bin/python
```

It has been registered as a Jupyter kernel:

```text
Taiwaneseness Analysis (.venv)
```

In VS Code, choose this kernel for notebooks. Do **not** use `MSSQL`.

The code-first notebook is:

```text
analysis/semantic_propagation_code_workbook.ipynb
```

It imports reusable functions from:

```text
scripts/semantic_propagation_analysis.py
```

That notebook computes DataFrames and plots live with pandas, matplotlib, and seaborn.

## Reliable Route for Exported Tables/Figures

From the repository root, run:

```bash
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/build_frozen_analysis_pack.py \
  --attestations frozen_data_v2/attestations_frozen.csv \
  --target-analysis frozen_data_v2/target_binding_analysis_frozen.csv \
  --out-dir analysis/frozen_v2 \
  --fig-dir reports/figures/frozen_v2 \
  --table-dir reports/tables/frozen_v2
```

This regenerates all thesis tables and SVG figures without relying on the VS Code notebook kernel.

## VS Code Notebook Route

Only use **Run All** if the notebook kernel is Python.

In VS Code:

1. Look at the top-right or bottom-right kernel indicator.
2. If it says `MSSQL`, SQL Server, or asks for a SQL connection profile, it is the wrong environment.
3. Click the kernel selector and choose `Taiwaneseness Analysis (.venv)`.
4. If no Python kernel appears, do not use Run All. Use the reliable route above.

The notebook cells are marked as Python, but VS Code can still run them as SQL if the active notebook kernel is MSSQL.

## Main Output Groups

- `reports/tables/frozen_v2/26_semantic_propagation_time_geo_cube.csv`
  combines period, 5-year bin, corridor, semantic family, Taiwan-marker frame, and discourse frame.
- `reports/tables/frozen_v2/27_semantic_family_by_corridor.csv`
  shows how semantic forms distribute by geography.
- `reports/tables/frozen_v2/28_semantic_family_by_time.csv`
  shows how semantic forms distribute over time.
- `reports/tables/frozen_v2/29_semantic_first_appearance_by_corridor.csv`
  gives first observed years for semantic families by corridor.
- `reports/figures/frozen_v2/16_semantic_family_by_corridor_heatmap.svg`
  visualizes semantic geography.
- `reports/figures/frozen_v2/17_semantic_family_time_share.svg`
  visualizes semantic change over time.
- `reports/figures/frozen_v2/18_taiwan_marker_frame_by_corridor.svg`
  visualizes how Taiwan markers are framed geographically.
- `reports/figures/frozen_v2/19_discourse_semantic_heatmap.svg`
  visualizes which discourse systems carry which semantic families.
