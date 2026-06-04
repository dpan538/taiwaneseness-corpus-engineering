#!/usr/bin/env python3
"""
Producer-consumer marker transfer and outlier mining.

This is a code-first analysis script for thesis figures. It intentionally works
without Plotly: PNG and CSV outputs are always generated; optional Plotly HTML is
added only when Plotly is installed and platform data are available.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
_mpl_cache = ROOT / ".cache" / "matplotlib"
_mpl_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_cache))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


TAIWAN_MARKERS = [
    "台湾",
    "臺灣",
    "台灣",
    "台式",
    "台菜",
    "臺灣菜",
    "台湾菜",
    "古早味",
    "寶島",
    "宝岛",
    "夜市",
    "眷村",
    "Taiwan",
    "Taiwanese",
    "Formosa",
    "台北",
    "臺北",
    "Taipei",
]

TASTE_WORDS = ["好吃", "美味", "香", "Q弹", "軟糯", "软糯", "味道", "口味", "便宜", "套餐", "性价比", "性價比"]


def load_semantic_module():
    module_path = ROOT / "scripts" / "semantic_propagation_analysis.py"
    spec = importlib.util.spec_from_file_location("semantic_propagation_analysis", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def text_join(row: pd.Series, cols: list[str]) -> str:
    parts = []
    for col in cols:
        value = row.get(col, "")
        if pd.notna(value):
            parts.append(str(value))
    return " ".join(parts)


def find_markers(text: str) -> list[str]:
    found = []
    lower = text.lower()
    for marker in TAIWAN_MARKERS:
        if marker.lower() in lower:
            found.append(marker)
    return found


def producer_marker_category(row: pd.Series) -> str:
    text = text_join(row, ["merchant_description", "platform_tags", "shop_name", "menu_item_names", "recommended_dishes"])
    found = find_markers(text)
    if len(found) >= 2:
        return "multiple_taiwan_markers"
    if len(found) == 1:
        marker = found[0]
        if re.search(r"古早味|夜市|眷村", marker, flags=re.I):
            return "nostalgia_or_market_marker"
        if re.search(r"台式|台菜|臺灣菜|台湾菜|Taiwanese", marker, flags=re.I):
            return "cuisine_style_marker"
        return "explicit_taiwan_marker"
    return "no_taiwan_marker"


def review_response_category(row: pd.Series) -> str:
    text = str(row.get("review_text", ""))
    found = find_markers(text)
    merchant_category = str(row.get("merchant_category", "no_taiwan_marker"))
    if found:
        if merchant_category != "no_taiwan_marker":
            return "consumer_reproduces_taiwan_marker"
        return "consumer_adds_new_taiwan_marker"
    if any(word in text for word in TASTE_WORDS):
        return "converted_to_taste_value"
    return "ignored_or_unmarked"


def choose_platform_files(args: argparse.Namespace) -> tuple[Path | None, Path | None, str]:
    candidates = [
        (Path(args.merchants), Path(args.reviews), "configured"),
        (ROOT / "data" / "merchant_platform_records.csv", ROOT / "data" / "consumer_reviews.csv", "platform_records"),
        (ROOT / "data" / "seed_merchants.csv", ROOT / "data" / "seed_reviews.csv", "seed_platform_sample"),
    ]
    for merchants, reviews, label in candidates:
        if merchants.exists() and reviews.exists():
            return merchants, reviews, label
    return None, None, "missing"


def run_producer_consumer(args: argparse.Namespace, out_dir: Path, fig_dir: Path) -> dict[str, Any]:
    merchant_path, review_path, data_label = choose_platform_files(args)
    result: dict[str, Any] = {"status": "skipped", "data_label": data_label}
    if merchant_path is None or review_path is None:
        return result

    merchants = pd.read_csv(merchant_path)
    reviews = pd.read_csv(review_path)
    if "merchant_id" not in merchants.columns or "merchant_id" not in reviews.columns:
        result["reason"] = "merchant_id missing"
        return result

    merchants = merchants.copy()
    reviews = reviews.copy()
    merchants["merchant_category"] = merchants.apply(producer_marker_category, axis=1)
    merged = merchants[["merchant_id", "merchant_category"]].merge(reviews, on="merchant_id", how="inner")
    if merged.empty:
        result["reason"] = "no matched merchant-review pairs"
        return result

    merged["review_category"] = merged.apply(review_response_category, axis=1)
    flow = merged.groupby(["merchant_category", "review_category"], dropna=False).size().reset_index(name="count")
    flow.to_csv(out_dir / "producer_consumer_flow.csv", index=False)
    merged.to_csv(out_dir / "producer_consumer_classified_reviews.csv", index=False)

    pivot = flow.pivot_table(index="merchant_category", columns="review_category", values="count", fill_value=0)
    plt.figure(figsize=(10, max(4, 0.45 * len(pivot))))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5)
    plt.title("Producer-to-consumer Taiwan marker transfer")
    plt.xlabel("Consumer review response")
    plt.ylabel("Merchant marker category")
    plt.tight_layout()
    plt.savefig(fig_dir / "producer_consumer_flow_matrix.png", dpi=180)
    plt.close()

    total_merchants = len(merchants)
    marked_merchants = int((merchants["merchant_category"] != "no_taiwan_marker").sum())
    reviews_of_marked = int((merged["merchant_category"] != "no_taiwan_marker").sum())
    reproduced = int(
        ((merged["merchant_category"] != "no_taiwan_marker") & (merged["review_category"] == "consumer_reproduces_taiwan_marker")).sum()
    )
    funnel = pd.DataFrame(
        {
            "stage": ["merchant records", "merchant uses Taiwan marker", "reviews of marked merchants", "consumer reproduces marker"],
            "count": [total_merchants, marked_merchants, reviews_of_marked, reproduced],
        }
    )
    funnel.to_csv(out_dir / "producer_consumer_funnel.csv", index=False)
    plt.figure(figsize=(9, 4.8))
    sns.barplot(data=funnel, y="stage", x="count", color="#4C78A8")
    for idx, row in funnel.iterrows():
        plt.text(row["count"] + max(funnel["count"].max() * 0.02, 0.08), idx, str(row["count"]), va="center")
    plt.title("Marker transfer funnel: producer claim to consumer reproduction")
    plt.xlabel("Count")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(fig_dir / "producer_consumer_funnel.png", dpi=180)
    plt.close()

    try:
        import plotly.graph_objects as go  # type: ignore

        source_labels = list(flow["merchant_category"].drop_duplicates())
        target_labels = list(flow["review_category"].drop_duplicates())
        labels = source_labels + target_labels
        source_map = {label: i for i, label in enumerate(source_labels)}
        target_map = {label: i + len(source_labels) for i, label in enumerate(target_labels)}
        fig = go.Figure(
            data=[
                go.Sankey(
                    node={"label": labels, "pad": 15, "thickness": 18},
                    link={
                        "source": [source_map[v] for v in flow["merchant_category"]],
                        "target": [target_map[v] for v in flow["review_category"]],
                        "value": flow["count"].tolist(),
                    },
                )
            ]
        )
        fig.update_layout(title_text="Producer-to-consumer Taiwan marker transfer")
        fig.write_html(fig_dir / "producer_consumer_sankey.html")
        result["plotly_html"] = "producer_consumer_sankey.html"
    except Exception:
        result["plotly_html"] = None

    result.update(
        {
            "status": "ok",
            "merchant_file": str(merchant_path),
            "review_file": str(review_path),
            "merchant_rows": int(len(merchants)),
            "review_rows": int(len(reviews)),
            "matched_review_rows": int(len(merged)),
            "marked_merchants": marked_merchants,
            "consumer_reproduced_reviews": reproduced,
        }
    )
    return result


def choose_outlier_threshold(df: pd.DataFrame) -> float:
    values = pd.to_numeric(df["weighted_historical_binding"], errors="coerce").dropna()
    if values.empty:
        return 0.5
    q15 = float(values.quantile(0.15))
    # Keep the default strict. In this corpus 0.76 is a common tertiary weight,
    # not an analytic outlier; weak-binding cases are the zero and very-low
    # weighted positives.
    return min(0.5, q15)


def classify_outlier_reason(row: pd.Series, threshold: float) -> str:
    raw = float(row.get("historical_binding_raw", 0.0))
    binding = float(row.get("weighted_historical_binding", 0.0))
    if raw <= 0:
        if str(row.get("dish_marker", "")).strip() and not str(row.get("taiwan_marker", "")).strip():
            return "dish_without_taiwan_marker"
        if str(row.get("taiwan_marker", "")).strip() and not str(row.get("dish_marker", "")).strip():
            return "taiwan_context_without_target_dish"
        return "no_binding_control"
    if binding <= threshold:
        return "positive_but_low_weight"
    return "not_outlier"


def run_outliers(args: argparse.Namespace, out_dir: Path, fig_dir: Path) -> dict[str, Any]:
    spa = load_semantic_module()
    df = spa.load_frozen_corpus(args.attestations)
    threshold = args.threshold if args.threshold is not None else choose_outlier_threshold(df)
    df = df.copy()
    df["outlier_reason"] = df.apply(classify_outlier_reason, axis=1, threshold=threshold)
    outliers = df[df["outlier_reason"] != "not_outlier"].copy()
    outliers["binding_gap"] = 1.0 - outliers["weighted_historical_binding"]

    out_cols = [
        "attestation_id",
        "year",
        "period",
        "corridor",
        "source_type",
        "source_name",
        "authority_level",
        "brand_or_category",
        "dish_marker",
        "taiwan_marker",
        "semantic_family",
        "discourse_frame",
        "analysis_weight",
        "weighted_historical_binding",
        "outlier_reason",
        "source_ref",
        "original_text",
    ]
    outliers[out_cols].sort_values(["weighted_historical_binding", "year"]).to_csv(out_dir / "low_binding_outliers.csv", index=False)
    outliers[out_cols].sort_values(["weighted_historical_binding", "analysis_weight", "year"]).head(args.top_n).to_csv(
        out_dir / "low_binding_examples_for_close_reading.csv", index=False
    )

    plt.figure(figsize=(12, 6))
    plot_df = outliers.copy()
    if not plot_df.empty:
        plot_df["plot_weight"] = plot_df["analysis_weight"].clip(lower=0.05) * 80
        sns.scatterplot(
            data=plot_df,
            x="year",
            y="weighted_historical_binding",
            hue="corridor",
            style="outlier_reason",
            size="plot_weight",
            sizes=(30, 260),
            alpha=0.78,
        )
        plt.axhline(threshold, color="black", linestyle="--", linewidth=1, label=f"threshold={threshold:.2f}")
    plt.title("Low-binding and weak-binding records by time and corridor")
    plt.xlabel("Year")
    plt.ylabel("Weighted binding contribution")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(fig_dir / "low_binding_outliers_scatter.png", dpi=180)
    plt.close()

    heat = (
        outliers.groupby(["corridor", "five_year_bin"], dropna=False)
        .size()
        .reset_index(name="outlier_count")
        .pivot_table(index="corridor", columns="five_year_bin", values="outlier_count", fill_value=0)
    )
    plt.figure(figsize=(14, max(4.5, len(heat) * 0.45)))
    sns.heatmap(heat, annot=True, fmt=".0f", cmap="OrRd", linewidths=0.5)
    plt.title("Low-binding records: time x geography")
    plt.xlabel("Five-year bin")
    plt.ylabel("Corridor")
    plt.tight_layout()
    plt.savefig(fig_dir / "low_binding_time_corridor_heatmap.png", dpi=180)
    plt.close()

    source_counts = outliers["source_type"].value_counts().head(18).reset_index()
    source_counts.columns = ["source_type", "count"]
    source_counts.to_csv(out_dir / "low_binding_by_source_type.csv", index=False)
    plt.figure(figsize=(10, max(5, len(source_counts) * 0.35)))
    sns.barplot(data=source_counts, x="count", y="source_type", color="#E45756")
    plt.title("Low-binding records by source type")
    plt.xlabel("Outlier records")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(fig_dir / "low_binding_by_source_type.png", dpi=180)
    plt.close()

    reason_counts = outliers["outlier_reason"].value_counts().reset_index()
    reason_counts.columns = ["outlier_reason", "count"]
    reason_counts.to_csv(out_dir / "low_binding_by_reason.csv", index=False)
    plt.figure(figsize=(8, 4.5))
    sns.barplot(data=reason_counts, x="count", y="outlier_reason", color="#72B7B2")
    plt.title("Low-binding records by analytic reason")
    plt.xlabel("Records")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(fig_dir / "low_binding_by_reason.png", dpi=180)
    plt.close()

    return {
        "status": "ok",
        "total_records": int(len(df)),
        "threshold": float(threshold),
        "outlier_records": int(len(outliers)),
        "outlier_share": float(len(outliers) / len(df)) if len(df) else 0.0,
        "reason_counts": reason_counts.to_dict(orient="records"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Producer-consumer marker transfer and outlier analysis")
    parser.add_argument("--attestations", default=str(ROOT / "frozen_data_v2" / "attestations_frozen.csv"))
    parser.add_argument("--merchants", default=str(ROOT / "data" / "merchant_platform_records.csv"))
    parser.add_argument("--reviews", default=str(ROOT / "data" / "consumer_reviews.csv"))
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--top-n", type=int, default=40)
    parser.add_argument("--out-dir", default=str(ROOT / "analysis" / "producer_consumer_outliers_outputs"))
    args = parser.parse_args()

    sns.set_theme(style="whitegrid", context="notebook")
    out_dir = Path(args.out_dir)
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    producer_consumer = run_producer_consumer(args, out_dir, fig_dir)
    outliers = run_outliers(args, out_dir, fig_dir)
    summary = pd.DataFrame(
        [
            {"analysis": "producer_consumer", **producer_consumer},
            {"analysis": "outlier_mining", **outliers},
        ]
    )
    summary.to_csv(out_dir / "analysis_summary.csv", index=False)

    print("Producer-consumer:", producer_consumer)
    print("Outliers:", outliers)
    print(out_dir)


if __name__ == "__main__":
    main()
