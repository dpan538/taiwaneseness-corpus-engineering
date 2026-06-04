# %%
"""
Semantic Propagation Live Analysis
==================================

Run this file as Python cells in VS Code. This is the code-first version: it
computes tables and plots live instead of embedding pre-rendered SVG reports.
"""

import importlib
import importlib.util
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd()
if not (ROOT / "scripts" / "semantic_propagation_analysis.py").exists():
    ROOT = Path.cwd()

_mpl_cache = ROOT / ".cache" / "matplotlib"
_mpl_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_cache))
os.environ.setdefault("MPLBACKEND", "Agg")
pd = importlib.import_module("pandas")
plt = importlib.import_module("matplotlib.pyplot")
sns = importlib.import_module("seaborn")

_module_path = ROOT / "scripts" / "semantic_propagation_analysis.py"
_spec = importlib.util.spec_from_file_location("semantic_propagation_analysis", _module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load semantic_propagation_analysis from {_module_path}")
_spa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_spa)

KEY_CORRIDORS = _spa.KEY_CORRIDORS
load_frozen_corpus = _spa.load_frozen_corpus
semantic_propagation_cube = _spa.semantic_propagation_cube
semantic_family_by_corridor = _spa.semantic_family_by_corridor
semantic_family_by_time = _spa.semantic_family_by_time
semantic_first_appearance = _spa.semantic_first_appearance
corridor_time_summary = _spa.corridor_time_summary
low_binding_pockets = _spa.low_binding_pockets
leave_one_source_type_out = _spa.leave_one_source_type_out
plot_semantic_family_by_corridor = _spa.plot_semantic_family_by_corridor
plot_semantic_family_over_time = _spa.plot_semantic_family_over_time
plot_semantic_stack_for_corridor = _spa.plot_semantic_stack_for_corridor
plot_discourse_stack_for_corridor = _spa.plot_discourse_stack_for_corridor
plot_corridor_time_heatmap = _spa.plot_corridor_time_heatmap
plot_semantic_entropy = _spa.plot_semantic_entropy
plot_first_appearance_timeline = _spa.plot_first_appearance_timeline
plot_low_binding_pockets = _spa.plot_low_binding_pockets
plot_leave_one_source_type_out = _spa.plot_leave_one_source_type_out

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.dpi"] = 130
pd.set_option("display.max_columns", 80)
pd.set_option("display.width", 160)

FIG_OUT = ROOT / "analysis" / "semantic_propagation_live_outputs" / "figures"


def render_current_figure(name: str) -> None:
    """Show in notebooks/interactive mode; save and close in plain script mode."""
    if hasattr(sys, "ps1"):
        plt.show()
        return
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIG_OUT / f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close()

# %%
# Load data and inspect enriched semantic columns.


df = load_frozen_corpus(ROOT / "frozen_data_v2" / "attestations_frozen.csv")
print(df.shape)
df[
    [
        "year",
        "period",
        "corridor",
        "semantic_family",
        "taiwan_marker_frame",
        "discourse_frame",
        "weighted_historical_binding",
        "analysis_weight",
    ]
].head(10)

# %%
# Main table: time x geography x semantic family x Taiwan marker frame x discourse frame.
cube = semantic_propagation_cube(df)
print(cube.shape)
cube.head(20)

# %%
# Early diffusion subset: this is usually more analytically useful than the saturated all-corpus trend.
early = cube[
    (cube["five_year_bin"] <= 2000)
    & (cube["corridor"].isin(["Singapore", "Japan", "North America", "Mainland China", "Taiwan-side"]))
]
early.sort_values(["five_year_bin", "corridor", "row_count"], ascending=[True, True, False]).head(40)

# %%
# Corridor x time summary: use this for visible ups and downs.
summary = corridor_time_summary(df)
summary.sort_values(["five_year_bin", "corridor"]).head(40)

# %%
ax = plot_corridor_time_heatmap(df, value="row_count")
plt.tight_layout()
render_current_figure("corridor_time_record_volume")

# %%
ax = plot_corridor_time_heatmap(df, value="primary_share")
plt.tight_layout()
render_current_figure("corridor_time_primary_share")

# %%
ax = plot_semantic_entropy(df, corridors=["Taiwan-side", "Singapore", "Japan", "North America", "Yangtze River Delta", "Mainland China"])
plt.tight_layout()
render_current_figure("semantic_entropy_by_corridor")

# %%
ax = plot_first_appearance_timeline(df, min_rows=2)
plt.tight_layout()
render_current_figure("first_appearance_timeline")

# %%
# Semantic geography: which semantic families dominate in which corridors?
geo = semantic_family_by_corridor(df)
geo[geo["corridor"].isin(KEY_CORRIDORS)].sort_values(["corridor", "row_count"], ascending=[True, False]).head(60)

# %%
ax = plot_semantic_family_by_corridor(df, corridors=KEY_CORRIDORS)
plt.tight_layout()
render_current_figure("semantic_family_by_corridor")

# %%
# Semantic change over time.
time = semantic_family_by_time(df)
time.sort_values(["five_year_bin", "row_count"], ascending=[True, False]).head(50)

# %%
ax = plot_semantic_family_over_time(df, top_n=7)
plt.tight_layout()
render_current_figure("semantic_family_over_time")

# %%
# Stacked semantic composition by corridor. These usually show more variation than binding index lines.
for corridor in ["Taiwan-side", "Singapore", "Japan", "North America", "Yangtze River Delta"]:
    try:
        ax = plot_semantic_stack_for_corridor(df, corridor=corridor, top_n=5)
        plt.tight_layout()
        render_current_figure(f"semantic_stack_{corridor.replace(' ', '_').replace('-', '_')}")
    except ValueError as exc:
        print(exc)

# %%
# Stacked discourse-frame composition by corridor.
for corridor in ["Taiwan-side", "Singapore", "Japan", "North America", "Yangtze River Delta"]:
    try:
        ax = plot_discourse_stack_for_corridor(df, corridor=corridor)
        plt.tight_layout()
        render_current_figure(f"discourse_stack_{corridor.replace(' ', '_').replace('-', '_')}")
    except ValueError as exc:
        print(exc)

# %%
# First appearance table: use this for diffusion narrative and "unique link" discussion.
first = semantic_first_appearance(df)
first.sort_values(["first_year", "corridor", "semantic_family"]).head(60)

# %%
# Low-binding pockets: where the obvious story breaks down.
pockets = low_binding_pockets(df)
pockets.head(30)

# %%
ax = plot_low_binding_pockets(df, n=15)
plt.tight_layout()
render_current_figure("low_binding_pockets")

# %%
# Source-type sensitivity: whether one source type is doing too much work.
sensitivity = leave_one_source_type_out(df)
sensitivity.sort_values("delta_from_full_index").head(30)

# %%
ax = plot_leave_one_source_type_out(df, n=15)
plt.tight_layout()
render_current_figure("leave_one_source_type_out")

# %%
# Save live-code outputs if desired.
out = ROOT / "analysis" / "semantic_propagation_live_outputs"
out.mkdir(parents=True, exist_ok=True)
cube.to_csv(out / "semantic_propagation_cube.csv", index=False)
geo.to_csv(out / "semantic_family_by_corridor.csv", index=False)
time.to_csv(out / "semantic_family_by_time.csv", index=False)
first.to_csv(out / "semantic_first_appearance.csv", index=False)
pockets.to_csv(out / "low_binding_pockets.csv", index=False)
sensitivity.to_csv(out / "leave_one_source_type_out.csv", index=False)
summary.to_csv(out / "corridor_time_summary.csv", index=False)
print(out)
