#!/usr/bin/env python3
"""
Change-point, violin, and authority-novelty surface analysis.

This script avoids optional heavy dependencies. It uses pandas, numpy,
matplotlib, and seaborn only, and writes real PNG figures plus CSV tables.

Interpretation note:
authority_weight and novelty_score are inputs to the weighting formula, so the
surface plots are diagnostics of the weighting regime, not causal estimates.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
_mpl_cache = ROOT / ".cache" / "matplotlib"
_mpl_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_cache))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import pandas as pd
import seaborn as sns


MAIN_CORRIDORS = [
    "Taiwan-side",
    "Singapore",
    "Japan",
    "North America",
    "Yangtze River Delta",
    "Mainland China",
    "Korea",
]


def load_semantic_module():
    module_path = ROOT / "scripts" / "semantic_propagation_analysis.py"
    spec = importlib.util.spec_from_file_location("semantic_propagation_analysis", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def period_bin(year: float) -> str:
    if year <= 1987:
        return "1946-1987"
    if year <= 2001:
        return "1988-2001"
    if year <= 2015:
        return "2002-2015"
    return "2016-2025"


def complete_year_series(rows: pd.DataFrame, value_col: str) -> pd.DataFrame:
    if rows.empty:
        return rows
    min_year = int(rows["year"].min())
    max_year = int(rows["year"].max())
    full = pd.DataFrame({"year": np.arange(min_year, max_year + 1)})
    out = full.merge(rows[["year", value_col]], on="year", how="left")
    out[value_col] = out[value_col].interpolate(limit_direction="both").fillna(0)
    return out


def sliding_change_points(series: np.ndarray, years: np.ndarray, window: int = 5, top_n: int = 4) -> pd.DataFrame:
    """Simple dependency-free change score: mean shift + variance shift."""
    rows = []
    if len(series) < (window * 2 + 1):
        return pd.DataFrame(columns=["year", "change_score", "left_mean", "right_mean", "left_var", "right_var"])
    for i in range(window, len(series) - window):
        left = series[i - window : i]
        right = series[i : i + window]
        mean_shift = abs(float(np.mean(right) - np.mean(left)))
        var_shift = abs(float(np.var(right) - np.var(left)))
        pooled = float(np.std(series)) or 1.0
        score = mean_shift / pooled + var_shift / (pooled * pooled)
        rows.append(
            {
                "year": int(years[i]),
                "change_score": score,
                "left_mean": float(np.mean(left)),
                "right_mean": float(np.mean(right)),
                "left_var": float(np.var(left)),
                "right_var": float(np.var(right)),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    # Keep local maxima first, then strongest remaining changes.
    out["is_local_peak"] = False
    scores = out["change_score"].to_numpy()
    for i in range(1, len(scores) - 1):
        if scores[i] >= scores[i - 1] and scores[i] >= scores[i + 1]:
            out.loc[out.index[i], "is_local_peak"] = True
    peaks = out[out["is_local_peak"]].sort_values("change_score", ascending=False).head(top_n)
    if len(peaks) < top_n:
        peaks = pd.concat([peaks, out.sort_values("change_score", ascending=False).head(top_n - len(peaks))])
    return peaks.drop_duplicates("year").sort_values("year")


def yearly_source_structure(df: pd.DataFrame, corridor: str) -> pd.DataFrame:
    sub = df[df["corridor"] == corridor].copy()
    rows = []
    for year, group in sub.groupby("year"):
        rows.append(
            {
                "corridor": corridor,
                "year": int(year),
                "rows": int(len(group)),
                "tertiary_ratio": float((group["authority_level"] == "tertiary").mean()),
                "primary_ratio": float((group["authority_level"] == "primary").mean()),
                "official_tourism_ratio": float(group["source_type"].str.contains("tourism|municipal|itinerary|route", case=False).mean()),
                "newspaper_ratio": float(group["source_type"].str.contains("newspaper|archive|issue", case=False).mean()),
                "binding_index": float(group["weighted_historical_binding"].sum() / max(group["analysis_weight"].sum(), 1e-9)),
            }
        )
    return pd.DataFrame(rows).sort_values("year")


def run_change_points(df: pd.DataFrame, out_dir: Path, fig_dir: Path) -> dict[str, Any]:
    rows = []
    for corridor in MAIN_CORRIDORS:
        yearly = yearly_source_structure(df, corridor)
        if len(yearly) < 8:
            continue
        for metric in ["tertiary_ratio", "primary_ratio", "official_tourism_ratio", "newspaper_ratio", "binding_index"]:
            series_df = complete_year_series(yearly[["year", metric]].rename(columns={metric: "value"}), "value")
            cps = sliding_change_points(series_df["value"].to_numpy(), series_df["year"].to_numpy(), window=5, top_n=3)
            for _, cp in cps.iterrows():
                rows.append(
                    {
                        "corridor": corridor,
                        "metric": metric,
                        "change_year": int(cp["year"]),
                        "change_score": float(cp["change_score"]),
                        "left_mean": float(cp["left_mean"]),
                        "right_mean": float(cp["right_mean"]),
                    }
                )
    change_points = pd.DataFrame(rows).sort_values(["corridor", "metric", "change_score"], ascending=[True, True, False])
    change_points.to_csv(out_dir / "change_point_candidates.csv", index=False)

    # Focused Taiwan-side plot: source-structure change, not saturated binding.
    taiwan = yearly_source_structure(df, "Taiwan-side")
    if not taiwan.empty:
        plt.figure(figsize=(12, 5.8))
        for metric, label in [
            ("tertiary_ratio", "tertiary source ratio"),
            ("official_tourism_ratio", "tourism/municipal source ratio"),
            ("newspaper_ratio", "newspaper/archive source ratio"),
            ("primary_ratio", "primary source ratio"),
        ]:
            plt.plot(taiwan["year"], taiwan[metric], marker="o", linewidth=1.8, label=label)
        top_taiwan = change_points[
            (change_points["corridor"] == "Taiwan-side")
            & (change_points["metric"].isin(["tertiary_ratio", "official_tourism_ratio", "newspaper_ratio", "primary_ratio"]))
        ].sort_values("change_score", ascending=False).head(5)
        for _, row in top_taiwan.iterrows():
            plt.axvline(row["change_year"], color="black", alpha=0.22, linestyle="--")
        plt.title("Taiwan-side source-structure change candidates")
        plt.xlabel("Year")
        plt.ylabel("Share within yearly records")
        plt.ylim(-0.05, 1.05)
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(fig_dir / "change_points_taiwan_source_structure.png", dpi=180)
        plt.close()

    # Multi-corridor change map.
    if not change_points.empty:
        top = change_points.sort_values("change_score", ascending=False).head(35).copy()
        top["label"] = top["corridor"] + " / " + top["metric"]
        plt.figure(figsize=(11, max(6, len(top) * 0.28)))
        sns.scatterplot(data=top, x="change_year", y="label", size="change_score", hue="metric", sizes=(60, 360), alpha=0.8)
        plt.title("Strongest candidate change points across corridors and metrics")
        plt.xlabel("Candidate change year")
        plt.ylabel("")
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(fig_dir / "change_point_candidate_map.png", dpi=180)
        plt.close()

    return {"change_point_rows": int(len(change_points))}


def run_violin(df: pd.DataFrame, out_dir: Path, fig_dir: Path) -> dict[str, Any]:
    plot_df = df[df["corridor"].isin(MAIN_CORRIDORS)].copy()
    plot_df["period_bin"] = plot_df["year"].apply(period_bin)
    plot_df["binding_bucket"] = pd.cut(
        plot_df["weighted_historical_binding"],
        bins=[-0.01, 0.001, 0.5, 0.8, 1.2],
        labels=["zero", "weak", "middle", "strong"],
    )
    plot_df.to_csv(out_dir / "violin_plot_rows.csv", index=False)

    plt.figure(figsize=(13, 6.4))
    sns.violinplot(
        data=plot_df,
        x="corridor",
        y="weighted_historical_binding",
        hue="period_bin",
        cut=0,
        inner="quartile",
        linewidth=0.9,
    )
    sns.stripplot(
        data=plot_df.sample(min(len(plot_df), 900), random_state=7),
        x="corridor",
        y="weighted_historical_binding",
        color="black",
        alpha=0.16,
        size=2,
    )
    plt.title("Binding distribution by corridor and broad period")
    plt.xlabel("Corridor")
    plt.ylabel("Weighted binding contribution")
    plt.xticks(rotation=20, ha="right")
    plt.legend(title="Period bin", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(fig_dir / "violin_binding_by_corridor_period.png", dpi=180)
    plt.close()

    bucket = (
        plot_df.groupby(["corridor", "period_bin", "binding_bucket"], observed=False)
        .size()
        .reset_index(name="rows")
    )
    totals = bucket.groupby(["corridor", "period_bin"])["rows"].transform("sum")
    bucket["share"] = bucket["rows"] / totals.replace(0, np.nan)
    bucket.to_csv(out_dir / "binding_bucket_by_corridor_period.csv", index=False)

    heat = bucket[bucket["binding_bucket"].isin(["zero", "weak"])].groupby(["corridor", "period_bin"])["share"].sum().reset_index()
    pivot = heat.pivot_table(index="corridor", columns="period_bin", values="share", fill_value=0)
    plt.figure(figsize=(9, 5.2))
    sns.heatmap(pivot, cmap="OrRd", annot=True, fmt=".2f", linewidths=0.5)
    plt.title("Share of zero/weak-binding records by corridor and period")
    plt.xlabel("Period")
    plt.ylabel("Corridor")
    plt.tight_layout()
    plt.savefig(fig_dir / "weak_binding_share_heatmap.png", dpi=180)
    plt.close()

    return {"violin_rows": int(len(plot_df))}


def polynomial_features(auth: np.ndarray, novelty: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [
            np.ones_like(auth),
            auth,
            novelty,
            auth * auth,
            auth * novelty,
            novelty * novelty,
        ]
    )


def fit_surface(sub: pd.DataFrame) -> tuple[np.ndarray, float]:
    x = sub["authority_weight"].to_numpy(dtype=float)
    n = sub["novelty_score"].to_numpy(dtype=float)
    y = sub["weighted_historical_binding"].to_numpy(dtype=float)
    X = polynomial_features(x, n)
    coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coefs
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return coefs, r2


def predict_surface(coefs: np.ndarray, auth: np.ndarray, novelty: np.ndarray) -> np.ndarray:
    return polynomial_features(auth.ravel(), novelty.ravel()) @ coefs


def run_authority_novelty(df: pd.DataFrame, out_dir: Path, fig_dir: Path) -> dict[str, Any]:
    sub = df[["attestation_id", "corridor", "period", "source_type", "authority_level", "authority_weight", "novelty_score", "analysis_weight", "historical_binding_raw", "weighted_historical_binding"]].copy()
    for col in ["authority_weight", "novelty_score", "analysis_weight", "historical_binding_raw", "weighted_historical_binding"]:
        sub[col] = pd.to_numeric(sub[col], errors="coerce")
    sub = sub.dropna(subset=["authority_weight", "novelty_score", "weighted_historical_binding"])
    sub = sub[(sub["authority_weight"].between(0, 1.5)) & (sub["novelty_score"].between(0, 1.05))]
    sub.to_csv(out_dir / "authority_novelty_surface_rows.csv", index=False)

    coefs, r2 = fit_surface(sub)
    coef_table = pd.DataFrame(
        {
            "term": ["intercept", "authority_weight", "novelty_score", "authority_weight^2", "authority_x_novelty", "novelty_score^2"],
            "coefficient": coefs,
        }
    )
    coef_table["r_squared_full_surface"] = r2
    coef_table.to_csv(out_dir / "authority_novelty_surface_coefficients.csv", index=False)

    auth_grid = np.linspace(sub["authority_weight"].min(), sub["authority_weight"].max(), 60)
    nov_grid = np.linspace(sub["novelty_score"].min(), sub["novelty_score"].max(), 60)
    AA, NN = np.meshgrid(auth_grid, nov_grid)
    ZZ = predict_surface(coefs, AA, NN).reshape(AA.shape)

    # Empirical binned surface: less smooth, more honest.
    sub["authority_bin"] = pd.cut(sub["authority_weight"], bins=8)
    sub["novelty_bin"] = pd.cut(sub["novelty_score"], bins=8)
    empirical = (
        sub.groupby(["authority_bin", "novelty_bin"], observed=True)
        .agg(
            rows=("attestation_id", "count"),
            mean_binding=("weighted_historical_binding", "mean"),
            mean_raw_binding=("historical_binding_raw", "mean"),
        )
        .reset_index()
    )
    empirical["authority_mid"] = empirical["authority_bin"].apply(lambda x: float(x.mid))
    empirical["novelty_mid"] = empirical["novelty_bin"].apply(lambda x: float(x.mid))
    empirical.to_csv(out_dir / "authority_novelty_empirical_bins.csv", index=False)

    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(111, projection="3d")
    scatter = ax.scatter(
        sub["authority_weight"],
        sub["novelty_score"],
        sub["weighted_historical_binding"],
        c=sub["weighted_historical_binding"],
        cmap="viridis",
        s=np.clip(sub["analysis_weight"] * 35, 8, 55),
        alpha=0.42,
    )
    ax.plot_surface(AA, NN, ZZ, cmap="plasma", alpha=0.36, linewidth=0, antialiased=True)
    ax.set_title(f"Authority-novelty weighting surface (diagnostic, R2={r2:.2f})")
    ax.set_xlabel("Authority weight")
    ax.set_ylabel("Novelty score")
    ax.set_zlabel("Weighted binding")
    fig.colorbar(scatter, ax=ax, shrink=0.65, pad=0.08, label="Weighted binding")
    plt.tight_layout()
    plt.savefig(fig_dir / "authority_novelty_3d_surface.png", dpi=180)
    plt.close()

    plt.figure(figsize=(9, 6.6))
    contour = plt.contourf(AA, NN, ZZ, levels=14, cmap="plasma")
    plt.scatter(
        sub["authority_weight"],
        sub["novelty_score"],
        c=sub["weighted_historical_binding"],
        cmap="viridis",
        s=np.clip(sub["analysis_weight"] * 18, 5, 34),
        edgecolors="none",
        alpha=0.45,
    )
    plt.colorbar(contour, label="Predicted weighted binding")
    plt.title("Authority-novelty contour surface (diagnostic)")
    plt.xlabel("Authority weight")
    plt.ylabel("Novelty score")
    plt.tight_layout()
    plt.savefig(fig_dir / "authority_novelty_contour.png", dpi=180)
    plt.close()

    plt.figure(figsize=(9.5, 6.2))
    pivot = empirical.pivot_table(index="novelty_mid", columns="authority_mid", values="mean_binding", fill_value=np.nan)
    sns.heatmap(pivot.sort_index(ascending=False), cmap="YlGnBu", annot=True, fmt=".2f", linewidths=0.5)
    plt.title("Empirical mean binding by authority and novelty bins")
    plt.xlabel("Authority weight bin midpoint")
    plt.ylabel("Novelty score bin midpoint")
    plt.tight_layout()
    plt.savefig(fig_dir / "authority_novelty_empirical_heatmap.png", dpi=180)
    plt.close()

    # Corridor contours as small multiples, not overplotted spaghetti.
    corridor_rows = []
    selected = [c for c in MAIN_CORRIDORS if len(sub[sub["corridor"] == c]) >= 20]
    ncols = 3
    nrows = int(np.ceil(len(selected) / ncols)) if selected else 1
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, max(4, 3.8 * nrows)), squeeze=False)
    for ax, corridor in zip(axes.ravel(), selected):
        csub = sub[sub["corridor"] == corridor]
        ccoef, cr2 = fit_surface(csub)
        czz = predict_surface(ccoef, AA, NN).reshape(AA.shape)
        ax.contourf(AA, NN, czz, levels=10, cmap="viridis")
        ax.scatter(csub["authority_weight"], csub["novelty_score"], s=8, color="black", alpha=0.25)
        ax.set_title(f"{corridor} (n={len(csub)}, R2={cr2:.2f})")
        ax.set_xlabel("Authority")
        ax.set_ylabel("Novelty")
        corridor_rows.append({"corridor": corridor, "rows": int(len(csub)), "r_squared": cr2, **dict(zip(coef_table["term"], ccoef))})
    for ax in axes.ravel()[len(selected) :]:
        ax.axis("off")
    fig.suptitle("Authority-novelty diagnostic surfaces by corridor", y=1.01)
    plt.tight_layout()
    plt.savefig(fig_dir / "authority_novelty_contours_by_corridor.png", dpi=180)
    plt.close()
    pd.DataFrame(corridor_rows).to_csv(out_dir / "authority_novelty_by_corridor_coefficients.csv", index=False)

    return {"surface_rows": int(len(sub)), "surface_r_squared": float(r2), "corridor_surfaces": int(len(selected))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Change point and authority-novelty diagnostic analysis")
    parser.add_argument("--attestations", default=str(ROOT / "frozen_data_v2" / "attestations_frozen.csv"))
    parser.add_argument("--out-dir", default=str(ROOT / "analysis" / "change_authority_novelty_outputs"))
    args = parser.parse_args()

    sns.set_theme(style="whitegrid", context="notebook")
    out_dir = Path(args.out_dir)
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    spa = load_semantic_module()
    df = spa.load_frozen_corpus(args.attestations)

    results = {
        "change_points": run_change_points(df, out_dir, fig_dir),
        "violin": run_violin(df, out_dir, fig_dir),
        "authority_novelty": run_authority_novelty(df, out_dir, fig_dir),
    }
    pd.DataFrame(
        [
            {"analysis": name, **values}
            for name, values in results.items()
        ]
    ).to_csv(out_dir / "analysis_summary.csv", index=False)
    print(results)
    print(out_dir)


if __name__ == "__main__":
    main()
