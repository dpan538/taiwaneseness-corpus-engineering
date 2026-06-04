#!/usr/bin/env python3
"""
Code-first semantic propagation analysis for the frozen corpus.

This module is designed for notebooks and interactive work. It returns real
pandas DataFrames and matplotlib/seaborn figures instead of pre-rendered report
images. The central analysis is:

    time bin x geography x semantic family x Taiwan-marker frame x discourse frame
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


SEMANTIC_FAMILY_PATTERNS = [
    ("lurou_rouzao_core", r"滷肉|魯肉|卤肉|肉燥|肉臊|lu rou|lurou|rouzao|ルーロー|魯肉飯|滷肉飯"),
    ("taiwan_porridge", r"Taiwan porridge|Taiwanese porridge|臺灣粥|台湾粥"),
    ("taiwanese_cuisine_label", r"Taiwanese Cuisine|Taiwanese food|Taiwan cuisine|台湾料理|台灣料理|台菜|臺菜"),
    ("street_snack_xiaochi", r"小吃|snack|street food|夜市|night market"),
    ("rice_meal_general", r"飯|饭|rice|bento|便當|便当"),
    ("noodle_soup_general", r"麵|面|noodle|ramen|ラーメン"),
    ("tea_drink_breakfast", r"茶|紅茶|奶茶|breakfast|早餐|drink|beverage"),
]

TAIWAN_MARKER_FRAME_PATTERNS = [
    ("explicit_taiwan", r"台灣|臺灣|台湾|Taiwan|Taiwanese|台湾式|台式"),
    ("formosa_legacy", r"Formosa|フォルモサ"),
    ("taipei_metonym", r"台北|臺北|Taipei"),
    ("south_taiwan_place", r"台南|臺南|Tainan|高雄|Kaohsiung|府城"),
    ("other_taiwan_place", r"台中|臺中|Taichung|嘉義|Chiayi|屏東|Pingtung|宜蘭|Yilan"),
]


KEY_CORRIDORS = [
    "Taiwan-side",
    "Singapore",
    "Japan",
    "North America",
    "Yangtze River Delta",
    "Mainland China",
    "Korea",
    "Hong Kong",
]


def load_frozen_corpus(path: str | Path = "frozen_data_v2/attestations_frozen.csv") -> pd.DataFrame:
    """Load and normalize the frozen attestations CSV."""
    df = pd.read_csv(path)
    return enrich_semantic_columns(clean_columns(df))


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column types needed for analysis."""
    df = df.copy()
    numeric_defaults = {
        "year": np.nan,
        "analysis_weight": 1.0,
        "weighted_historical_binding": 0.0,
        "historical_binding_raw": 0.0,
        "novelty_score": 0.0,
        "authority_weight": 0.0,
    }
    for col, default in numeric_defaults.items():
        if col not in df.columns:
            df[col] = default
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)

    text_cols = [
        "attestation_id",
        "period",
        "corridor",
        "source_type",
        "source_name",
        "authority_level",
        "attestation_type",
        "brand_or_category",
        "dish_marker",
        "taiwan_marker",
        "source_url",
        "source_url_or_archive_ref",
        "original_text",
        "text_for_scoring",
        "notes",
    ]
    for col in text_cols:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
        df[col] = df[col].replace({"nan": "", "NaN": "", "None": "", "none": ""})

    for col in ["period", "corridor", "source_type", "authority_level", "attestation_type"]:
        df[col] = df[col].where(df[col].str.len().gt(0), "unknown")

    df["source_ref"] = df["source_url"].where(df["source_url"].str.len().gt(0), df["source_url_or_archive_ref"])
    df["is_positive"] = df["weighted_historical_binding"] > 0.00001
    df["five_year_bin"] = (df["year"].astype(int) // 5) * 5
    df["decade"] = (df["year"].astype(int) // 10) * 10
    return df


def _match_first(text: str, patterns: Iterable[tuple[str, str]], default: str) -> str:
    for label, pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            return label
    return default


def semantic_family(row: pd.Series) -> str:
    text = " ".join(
        [
            str(row.get("dish_marker", "")),
            str(row.get("taiwan_marker", "")),
            str(row.get("brand_or_category", "")),
            str(row.get("original_text", "")),
            str(row.get("text_for_scoring", "")),
        ]
    )
    if not str(row.get("dish_marker", "")).strip() and str(row.get("taiwan_marker", "")).strip():
        return "taiwan_context_without_target_dish"
    if str(row.get("dish_marker", "")).strip() and not str(row.get("taiwan_marker", "")).strip():
        return "dish_context_without_taiwan_marker"
    return _match_first(text, SEMANTIC_FAMILY_PATTERNS, "other_food_or_memory")


def taiwan_marker_frame(row: pd.Series) -> str:
    text = " ".join(
        [
            str(row.get("taiwan_marker", "")),
            str(row.get("brand_or_category", "")),
            str(row.get("original_text", "")),
            str(row.get("text_for_scoring", "")),
        ]
    )
    if not str(row.get("taiwan_marker", "")).strip():
        return "no_explicit_taiwan_marker"
    return _match_first(text, TAIWAN_MARKER_FRAME_PATTERNS, "other_taiwan_marker")


def discourse_frame(row: pd.Series) -> str:
    source_type = str(row.get("source_type", "")).lower()
    text = " ".join(
        [
            str(row.get("source_name", "")),
            str(row.get("attestation_type", "")),
            source_type,
            str(row.get("notes", "")),
            str(row.get("original_text", "")),
        ]
    ).lower()
    if any(x in source_type for x in ["newspaper", "advertisement", "archive", "issue"]):
        return "archival_ad_or_news"
    if any(x in source_type for x in ["tourism", "municipal", "itinerary", "route"]):
        return "official_tourism_memory"
    if any(x in source_type for x in ["open_data", "event_page", "activity", "competition"]):
        return "official_event_or_open_data"
    if any(x in text for x in ["review", "blog", "consumer", "ugc", "social"]):
        return "consumer_or_retrospective_web"
    if any(x in source_type for x in ["brand", "corporate", "prospectus", "listing"]):
        return "brand_or_platform_listing"
    return "other_discourse"


def enrich_semantic_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add semantic_family, taiwan_marker_frame, discourse_frame."""
    df = df.copy()
    df["semantic_family"] = df.apply(semantic_family, axis=1)
    df["taiwan_marker_frame"] = df.apply(taiwan_marker_frame, axis=1)
    df["discourse_frame"] = df.apply(discourse_frame, axis=1)
    return df


def weighted_binding_index(group: pd.DataFrame) -> float:
    """Use sum(weighted contribution) / sum(analysis weight)."""
    weight_sum = group["analysis_weight"].sum()
    if weight_sum <= 0:
        return 0.0
    return float(group["weighted_historical_binding"].sum() / weight_sum)


def weighted_positive_rate(group: pd.DataFrame) -> float:
    weight_sum = group["analysis_weight"].sum()
    if weight_sum <= 0:
        return 0.0
    return float(group.loc[group["is_positive"], "analysis_weight"].sum() / weight_sum)


def group_metrics(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """Aggregate row count, weight, binding, authority, and source diversity."""
    rows = []
    for keys, group in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row.update(
            {
                "row_count": int(len(group)),
                "weight_sum": float(group["analysis_weight"].sum()),
                "binding_index": weighted_binding_index(group),
                "positive_rate_weighted": weighted_positive_rate(group),
                "positive_rate_rows": float(group["is_positive"].mean()) if len(group) else 0.0,
                "primary_rows": int((group["authority_level"] == "primary").sum()),
                "secondary_rows": int((group["authority_level"] == "secondary").sum()),
                "tertiary_rows": int((group["authority_level"] == "tertiary").sum()),
                "unique_sources": int(group["source_ref"].replace("", pd.NA).dropna().nunique()),
                "first_year": int(group["year"].min()) if len(group) else None,
                "last_year": int(group["year"].max()) if len(group) else None,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def semantic_propagation_cube(df: pd.DataFrame) -> pd.DataFrame:
    """Full time x geography x semantics table."""
    return group_metrics(
        df,
        [
            "period",
            "five_year_bin",
            "corridor",
            "semantic_family",
            "taiwan_marker_frame",
            "discourse_frame",
        ],
    ).sort_values(["five_year_bin", "corridor", "semantic_family", "row_count"])


def semantic_family_by_corridor(df: pd.DataFrame) -> pd.DataFrame:
    out = group_metrics(df, ["corridor", "semantic_family"]).sort_values(["corridor", "row_count"], ascending=[True, False])
    totals = out.groupby("corridor")["row_count"].transform("sum")
    out["share_within_corridor"] = out["row_count"] / totals
    return out


def semantic_family_by_time(df: pd.DataFrame) -> pd.DataFrame:
    out = group_metrics(df, ["five_year_bin", "semantic_family"]).sort_values(["five_year_bin", "row_count"], ascending=[True, False])
    totals = out.groupby("five_year_bin")["row_count"].transform("sum")
    out["share_within_time_bin"] = out["row_count"] / totals
    return out


def semantic_family_by_corridor_time(df: pd.DataFrame) -> pd.DataFrame:
    """Semantic-family composition within each corridor and five-year bin."""
    out = group_metrics(df, ["corridor", "five_year_bin", "semantic_family"]).sort_values(
        ["corridor", "five_year_bin", "row_count"], ascending=[True, True, False]
    )
    totals = out.groupby(["corridor", "five_year_bin"])["row_count"].transform("sum")
    out["share_within_corridor_time"] = out["row_count"] / totals
    return out


def discourse_frame_by_corridor_time(df: pd.DataFrame) -> pd.DataFrame:
    """Discourse-frame composition within each corridor and five-year bin."""
    out = group_metrics(df, ["corridor", "five_year_bin", "discourse_frame"]).sort_values(
        ["corridor", "five_year_bin", "row_count"], ascending=[True, True, False]
    )
    totals = out.groupby(["corridor", "five_year_bin"])["row_count"].transform("sum")
    out["share_within_corridor_time"] = out["row_count"] / totals
    return out


def corridor_time_summary(df: pd.DataFrame) -> pd.DataFrame:
    """A compact timeline table: volume, binding, source mix, diversity."""
    rows = []
    for (corridor, bin_year), group in df.groupby(["corridor", "five_year_bin"]):
        family_counts = group["semantic_family"].value_counts()
        total = family_counts.sum()
        probs = family_counts / total if total else family_counts
        entropy = float(-(probs * np.log2(probs)).sum()) if total else 0.0
        normalized_entropy = entropy / np.log2(len(family_counts)) if len(family_counts) > 1 else 0.0
        top_family = family_counts.index[0] if len(family_counts) else "none"
        top_share = float(family_counts.iloc[0] / total) if total else 0.0
        rows.append(
            {
                "corridor": corridor,
                "five_year_bin": int(bin_year),
                "row_count": int(len(group)),
                "weight_sum": float(group["analysis_weight"].sum()),
                "binding_index": weighted_binding_index(group),
                "positive_rate_weighted": weighted_positive_rate(group),
                "primary_share": float((group["authority_level"] == "primary").mean()),
                "tertiary_share": float((group["authority_level"] == "tertiary").mean()),
                "unique_sources": int(group["source_ref"].replace("", pd.NA).dropna().nunique()),
                "semantic_entropy": entropy,
                "semantic_entropy_normalized": normalized_entropy,
                "dominant_semantic_family": top_family,
                "dominant_semantic_share": top_share,
            }
        )
    return pd.DataFrame(rows).sort_values(["corridor", "five_year_bin"])


def first_appearance_timeline(df: pd.DataFrame, min_rows: int = 1) -> pd.DataFrame:
    """First appearance of each semantic family in each corridor."""
    out = semantic_first_appearance(df)
    return out[out["rows"] >= min_rows].sort_values(["first_year", "corridor", "semantic_family"])


def semantic_first_appearance(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (corridor, family), group in df.groupby(["corridor", "semantic_family"]):
        positives = group[group["is_positive"]]
        rows.append(
            {
                "corridor": corridor,
                "semantic_family": family,
                "rows": int(len(group)),
                "first_year": int(group["year"].min()),
                "first_positive_year": int(positives["year"].min()) if len(positives) else np.nan,
                "last_year": int(group["year"].max()),
                "binding_index": weighted_binding_index(group),
                "positive_rate_weighted": weighted_positive_rate(group),
                "primary_rows": int((group["authority_level"] == "primary").sum()),
                "unique_sources": int(group["source_ref"].replace("", pd.NA).dropna().nunique()),
            }
        )
    return pd.DataFrame(rows).sort_values(["first_year", "corridor", "semantic_family"])


def low_binding_pockets(df: pd.DataFrame, min_rows: int = 3) -> pd.DataFrame:
    parts = []
    for cols in [["period", "corridor"], ["period", "corridor", "source_type"], ["corridor", "authority_level"]]:
        part = group_metrics(df, cols)
        part["grouping"] = " + ".join(cols)
        parts.append(part)
    out = pd.concat(parts, ignore_index=True)
    out["binding_gap"] = 1.0 - out["binding_index"]
    return out[(out["row_count"] >= min_rows) & (out["binding_gap"] > 0.02)].sort_values(
        ["binding_gap", "row_count"], ascending=[False, False]
    )


def leave_one_source_type_out(df: pd.DataFrame, min_rows: int = 5) -> pd.DataFrame:
    full_index = weighted_binding_index(df)
    rows = []
    for source_type, group in df.groupby("source_type"):
        if len(group) < min_rows:
            continue
        remaining = df[df["source_type"] != source_type]
        idx = weighted_binding_index(remaining)
        rows.append(
            {
                "excluded_source_type": source_type,
                "excluded_rows": int(len(group)),
                "excluded_share": len(group) / len(df),
                "binding_index_without_source_type": idx,
                "delta_from_full_index": idx - full_index,
            }
        )
    return pd.DataFrame(rows).sort_values("delta_from_full_index")


def plot_semantic_family_by_corridor(df: pd.DataFrame, corridors: list[str] | None = None, ax=None):
    """Heatmap: semantic-family shares inside each corridor."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    data = semantic_family_by_corridor(df)
    if corridors:
        data = data[data["corridor"].isin(corridors)]
    pivot = data.pivot_table(
        index="semantic_family",
        columns="corridor",
        values="share_within_corridor",
        fill_value=0,
    )
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(pivot, cmap="Blues", annot=True, fmt=".2f", linewidths=0.5, ax=ax)
    ax.set_title("Semantic family share by corridor")
    ax.set_xlabel("Corridor")
    ax.set_ylabel("Semantic family")
    return ax


def plot_semantic_family_over_time(df: pd.DataFrame, top_n: int = 6, ax=None):
    """Line plot: top semantic-family shares over five-year bins."""
    import matplotlib.pyplot as plt

    data = semantic_family_by_time(df)
    top = data.groupby("semantic_family")["row_count"].sum().sort_values(ascending=False).head(top_n).index
    data = data[data["semantic_family"].isin(top)]
    pivot = data.pivot_table(
        index="five_year_bin",
        columns="semantic_family",
        values="share_within_time_bin",
        fill_value=0,
    ).sort_index()
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(ax=ax, marker="o")
    ax.set_title("Semantic family share over time")
    ax.set_xlabel("Five-year bin")
    ax.set_ylabel("Share within time bin")
    ax.legend(title="Semantic family", bbox_to_anchor=(1.02, 1), loc="upper left")
    return ax


def plot_semantic_stack_for_corridor(df: pd.DataFrame, corridor: str, top_n: int = 5, ax=None):
    """Stacked area: semantic-family composition over time in one corridor."""
    import matplotlib.pyplot as plt

    data = semantic_family_by_corridor_time(df)
    data = data[data["corridor"] == corridor]
    if data.empty:
        raise ValueError(f"No records for corridor: {corridor}")
    top = data.groupby("semantic_family")["row_count"].sum().sort_values(ascending=False).head(top_n).index
    data = data.copy()
    data["family_plot"] = data["semantic_family"].where(data["semantic_family"].isin(top), "other")
    plot_data = (
        data.groupby(["five_year_bin", "family_plot"])["row_count"]
        .sum()
        .reset_index()
        .pivot_table(index="five_year_bin", columns="family_plot", values="row_count", fill_value=0)
        .sort_index()
    )
    plot_data = plot_data.div(plot_data.sum(axis=1), axis=0).fillna(0)
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))
    plot_data.plot.area(ax=ax, alpha=0.82)
    ax.set_title(f"Semantic composition over time: {corridor}")
    ax.set_xlabel("Five-year bin")
    ax.set_ylabel("Share within corridor-time bin")
    ax.legend(title="Semantic family", bbox_to_anchor=(1.02, 1), loc="upper left")
    return ax


def plot_discourse_stack_for_corridor(df: pd.DataFrame, corridor: str, ax=None):
    """Stacked area: discourse-frame composition over time in one corridor."""
    import matplotlib.pyplot as plt

    data = discourse_frame_by_corridor_time(df)
    data = data[data["corridor"] == corridor]
    if data.empty:
        raise ValueError(f"No records for corridor: {corridor}")
    plot_data = (
        data.groupby(["five_year_bin", "discourse_frame"])["row_count"]
        .sum()
        .reset_index()
        .pivot_table(index="five_year_bin", columns="discourse_frame", values="row_count", fill_value=0)
        .sort_index()
    )
    plot_data = plot_data.div(plot_data.sum(axis=1), axis=0).fillna(0)
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))
    plot_data.plot.area(ax=ax, alpha=0.82)
    ax.set_title(f"Discourse-frame composition over time: {corridor}")
    ax.set_xlabel("Five-year bin")
    ax.set_ylabel("Share within corridor-time bin")
    ax.legend(title="Discourse frame", bbox_to_anchor=(1.02, 1), loc="upper left")
    return ax


def plot_corridor_time_heatmap(df: pd.DataFrame, value: str = "row_count", ax=None):
    """Heatmap by corridor and five-year bin for volume, binding, primary share, etc."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    summary = corridor_time_summary(df)
    pivot = summary.pivot_table(index="corridor", columns="five_year_bin", values=value, fill_value=0)
    if ax is None:
        _, ax = plt.subplots(figsize=(14, 7))
    fmt = ".0f" if value in {"row_count", "unique_sources"} else ".2f"
    sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.5, annot=True, fmt=fmt, ax=ax)
    ax.set_title(f"Corridor x time heatmap: {value}")
    ax.set_xlabel("Five-year bin")
    ax.set_ylabel("Corridor")
    return ax


def plot_semantic_entropy(df: pd.DataFrame, corridors: list[str] | None = None, ax=None):
    """Line chart: semantic diversity over time. More variation means less single-track attribution."""
    import matplotlib.pyplot as plt

    summary = corridor_time_summary(df)
    if corridors:
        summary = summary[summary["corridor"].isin(corridors)]
    pivot = summary.pivot_table(
        index="five_year_bin",
        columns="corridor",
        values="semantic_entropy_normalized",
        fill_value=np.nan,
    ).sort_index()
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(ax=ax, marker="o")
    ax.set_title("Semantic diversity over time by corridor")
    ax.set_xlabel("Five-year bin")
    ax.set_ylabel("Normalized semantic entropy")
    ax.legend(title="Corridor", bbox_to_anchor=(1.02, 1), loc="upper left")
    return ax


def plot_first_appearance_timeline(df: pd.DataFrame, min_rows: int = 2, ax=None):
    """Scatter timeline: first appearance of semantic families by corridor."""
    import matplotlib.pyplot as plt

    data = first_appearance_timeline(df, min_rows=min_rows).copy()
    if data.empty:
        raise ValueError("No first appearance data after filtering")
    corridors = list(dict.fromkeys(data["corridor"]))
    y_map = {corr: i for i, corr in enumerate(corridors)}
    data["y"] = data["corridor"].map(y_map)
    sizes = 35 + data["rows"].clip(upper=50) * 5
    if ax is None:
        _, ax = plt.subplots(figsize=(13, max(5, len(corridors) * 0.45)))
    for family, sub in data.groupby("semantic_family"):
        ax.scatter(sub["first_year"], sub["y"], s=sizes.loc[sub.index], alpha=0.75, label=family)
    ax.set_yticks(list(y_map.values()), list(y_map.keys()))
    ax.set_title("First appearance of semantic families by corridor")
    ax.set_xlabel("First observed year")
    ax.set_ylabel("Corridor")
    ax.legend(title="Semantic family", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.grid(True, axis="x", alpha=0.35)
    return ax


def plot_low_binding_pockets(df: pd.DataFrame, n: int = 15, ax=None):
    """Horizontal bar chart of groups where binding is weakest."""
    import matplotlib.pyplot as plt

    data = low_binding_pockets(df).head(n).copy()
    labels = []
    for _, row in data.iterrows():
        bits = [
            str(row.get(col, ""))
            for col in ["period", "corridor", "source_type", "authority_level"]
            if str(row.get(col, "")) and str(row.get(col, "")) != "nan"
        ]
        labels.append(" / ".join(bits)[:80])
    data["label"] = labels
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 7))
    ax.barh(data["label"], data["binding_gap"])
    ax.invert_yaxis()
    ax.set_title("Largest low-binding pockets")
    ax.set_xlabel("Binding gap (1 - binding index)")
    return ax


def plot_leave_one_source_type_out(df: pd.DataFrame, n: int = 15, ax=None):
    """Bar chart of robustness: change in index after excluding source types."""
    import matplotlib.pyplot as plt

    data = leave_one_source_type_out(df).copy()
    data["abs_delta"] = data["delta_from_full_index"].abs()
    data = data.sort_values("abs_delta", ascending=False).head(n)
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 7))
    ax.barh(data["excluded_source_type"], data["delta_from_full_index"])
    ax.axvline(0, color="black", linewidth=1)
    ax.invert_yaxis()
    ax.set_title("Leave-one-source-type-out sensitivity")
    ax.set_xlabel("Change in overall binding index")
    return ax
