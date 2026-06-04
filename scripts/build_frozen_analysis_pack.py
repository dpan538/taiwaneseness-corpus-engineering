#!/usr/bin/env python3
"""
Build a thesis-oriented descriptive analysis pack for the frozen v2 corpus.

The script intentionally avoids plotting dependencies such as matplotlib. It
uses pandas for tabular work and writes lightweight SVG figures directly so the
analysis remains reproducible in constrained Codex/Jupyter environments.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd


PALETTE = [
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
    "#B279A2",
    "#FF9DA6",
    "#9D755D",
    "#BAB0AC",
    "#59A14F",
]

KEY_CORRIDORS = [
    "Taiwan-side",
    "Singapore",
    "Japan",
    "North America",
    "Yangtze River Delta",
    "Mainland China",
    "Hong Kong",
    "Korea",
]

NOSTALGIA_PATTERNS = {
    "old_flavor": r"古早|老味|老店|old[- ]?flavo[u]?r|old[- ]?taste|traditional",
    "night_market": r"夜市|night market",
    "home_memory": r"家鄉|故鄉|懷舊|怀旧|nostalg|memory|heritage",
    "street_snack": r"小吃|snack|street food",
}

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
    ("other_place_marker", r"台中|臺中|Taichung|嘉義|Chiayi|屏東|Pingtung|宜蘭|Yilan"),
]


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def to_num(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in [
        "year",
        "analysis_weight",
        "weighted_historical_binding",
        "historical_binding_raw",
        "target_binding_raw",
        "novelty_score",
        "authority_weight",
        "merged_row_count",
    ]:
        if col in df.columns:
            default = 1.0 if col == "analysis_weight" else 0.0
            df[col] = to_num(df[col], default)
    for col in [
        "period",
        "corridor",
        "source_type",
        "source_name",
        "authority_level",
        "attestation_type",
        "dish_marker",
        "taiwan_marker",
        "source_url",
        "source_url_or_archive_ref",
        "original_text",
        "text_for_scoring",
    ]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
        df[col] = df[col].replace({"nan": "", "NaN": "", "None": "", "none": ""})
    for col in ["period", "corridor", "source_type", "authority_level", "attestation_type"]:
        df[col] = df[col].where(df[col].str.len().gt(0), "unknown")
    if "analysis_weight" not in df.columns:
        df["analysis_weight"] = 1.0
    if "weighted_historical_binding" not in df.columns:
        raw = (df["dish_marker"].str.len().gt(0) & df["taiwan_marker"].str.len().gt(0)).astype(float)
        df["historical_binding_raw"] = raw
        df["weighted_historical_binding"] = raw * df["analysis_weight"]
    if "historical_binding_raw" not in df.columns:
        df["historical_binding_raw"] = (df["weighted_historical_binding"] > 0).astype(float)
    df["source_ref"] = df["source_url"].where(df["source_url"].str.len().gt(0), df["source_url_or_archive_ref"])
    df["is_positive"] = df["weighted_historical_binding"] > 0.00001
    df["five_year_bin"] = (df["year"].astype(int) // 5) * 5
    df["decade"] = (df["year"].astype(int) // 10) * 10
    return df


def weighted_index(group: pd.DataFrame) -> float:
    weight_sum = group["analysis_weight"].sum()
    if weight_sum <= 0:
        return 0.0
    return float(group["weighted_historical_binding"].sum() / weight_sum)


def weighted_positive_rate(group: pd.DataFrame) -> float:
    weight_sum = group["analysis_weight"].sum()
    if weight_sum <= 0:
        return 0.0
    return float(group.loc[group["is_positive"], "analysis_weight"].sum() / weight_sum)


def metrics_for_group(group: pd.DataFrame) -> dict:
    return {
        "row_count": int(len(group)),
        "weight_sum": round(float(group["analysis_weight"].sum()), 4),
        "binding_index": round(weighted_index(group), 4),
        "positive_rate_weighted": round(weighted_positive_rate(group), 4),
        "positive_rate_rows": round(float(group["is_positive"].mean()), 4) if len(group) else 0.0,
        "primary_rows": int((group["authority_level"] == "primary").sum()),
        "secondary_rows": int((group["authority_level"] == "secondary").sum()),
        "tertiary_rows": int((group["authority_level"] == "tertiary").sum()),
        "unique_sources": int(group["source_ref"].replace("", pd.NA).dropna().nunique()),
        "first_year": int(group["year"].min()) if len(group) else None,
        "last_year": int(group["year"].max()) if len(group) else None,
    }


def group_metrics(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, group in df.groupby(cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(cols, keys))
        row.update(metrics_for_group(group))
        rows.append(row)
    return pd.DataFrame(rows)


def bootstrap_ci(values: list[float], weights: list[float], n_iter: int = 500, seed: int = 42) -> tuple[float, float]:
    paired = [(v, w) for v, w in zip(values, weights) if w > 0]
    if len(paired) < 3:
        return (math.nan, math.nan)
    rng = random.Random(seed)
    stats = []
    n = len(paired)
    for _ in range(n_iter):
        sample = [paired[rng.randrange(n)] for _ in range(n)]
        sw = sum(w for _, w in sample)
        stats.append(sum(v for v, _ in sample) / sw if sw else 0.0)
    stats.sort()
    return (round(stats[int(0.025 * n_iter)], 4), round(stats[int(0.975 * n_iter)], 4))


def cramer_v(table: pd.DataFrame) -> dict:
    observed = table.to_numpy(dtype=float)
    if observed.size == 0 or observed.sum() == 0:
        return {"chi2": 0.0, "df": 0, "cramers_v": 0.0}
    row_sums = observed.sum(axis=1, keepdims=True)
    col_sums = observed.sum(axis=0, keepdims=True)
    total = observed.sum()
    expected = row_sums @ col_sums / total
    chi2_terms = []
    for obs, exp in zip(observed.flatten(), expected.flatten()):
        if exp > 0:
            chi2_terms.append((obs - exp) ** 2 / exp)
    chi2 = sum(chi2_terms)
    r, c = observed.shape
    denom = total * max(1, min(r - 1, c - 1))
    v = math.sqrt(float(chi2) / denom) if denom else 0.0
    return {"chi2": round(float(chi2), 4), "df": int((r - 1) * (c - 1)), "cramers_v": round(v, 4)}


def split_markers(series: pd.Series) -> Counter:
    counts: Counter = Counter()
    for raw in series.dropna().astype(str):
        for part in re.split(r"[;；,/、|]", raw):
            val = part.strip()
            if val and val.lower() not in {"nan", "none", "unknown"}:
                counts[val] += 1
    return counts


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_markdown_table(df: pd.DataFrame, path: Path, max_rows: int = 30) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    view = df.head(max_rows).copy()
    columns = list(view.columns)
    rows = [[str(row[col]) for col in columns] for _, row in view.iterrows()]
    with open(path, "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(columns) + " |\n")
        f.write("| " + " | ".join(["---"] * len(columns)) + " |\n")
        for row in rows:
            escaped = [cell.replace("|", "\\|").replace("\n", " ") for cell in row]
            f.write("| " + " | ".join(escaped) + " |\n")
        f.write("\n")


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;font-size:12px;fill:#1f2937}.title{font-size:18px;font-weight:700}.axis{fill:#4b5563;font-size:11px}.grid{stroke:#e5e7eb;stroke-width:1}.line{fill:none;stroke-width:2.5}.label{font-size:11px;fill:#111827}.note{font-size:10px;fill:#6b7280}</style>',
        f'<text class="title" x="24" y="28">{html.escape(title)}</text>',
    ]


def save_svg_barh(data: pd.DataFrame, label_col: str, value_col: str, title: str, path: Path, width: int = 920) -> None:
    data = data[[label_col, value_col]].dropna().head(18)
    height = 70 + max(1, len(data)) * 28
    left, right, top = 260, 30, 50
    max_val = max(float(data[value_col].max()), 1.0)
    out = svg_header(width, height, title)
    for i, (_, row) in enumerate(data.iterrows()):
        y = top + i * 28
        val = float(row[value_col])
        bar_w = (width - left - right) * val / max_val
        color = PALETTE[i % len(PALETTE)]
        out.append(f'<text x="{left-8}" y="{y+15}" text-anchor="end">{html.escape(str(row[label_col]))}</text>')
        out.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="18" fill="{color}" opacity="0.88"/>')
        out.append(f'<text x="{left+bar_w+6}" y="{y+14}" class="label">{val:.3g}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def save_svg_line(
    series: dict[str, pd.DataFrame],
    x_col: str,
    y_col: str,
    title: str,
    path: Path,
    width: int = 960,
    height: int = 520,
    y_label: str = "Weighted binding index",
) -> None:
    all_x, all_y = [], []
    for data in series.values():
        all_x += [float(x) for x in data[x_col].dropna()]
        all_y += [float(y) for y in data[y_col].dropna()]
    if not all_x or not all_y:
        return
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(0.0, min(all_y)), max(1.0, max(all_y))
    left, right, top, bottom = 72, 170, 55, 58
    plot_w, plot_h = width - left - right, height - top - bottom

    def sx(x: float) -> float:
        return left + (x - min_x) / (max_x - min_x or 1) * plot_w

    def sy(y: float) -> float:
        return top + (max_y - y) / (max_y - min_y or 1) * plot_h

    out = svg_header(width, height, title)
    for t in [0, 0.25, 0.5, 0.75, 1.0]:
        yv = min_y + t * (max_y - min_y)
        y = sy(yv)
        out.append(f'<line class="grid" x1="{left}" x2="{left+plot_w}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(f'<text class="axis" x="{left-8}" y="{y+4:.1f}" text-anchor="end">{yv:.2f}</text>')
    out.append(f'<line x1="{left}" x2="{left+plot_w}" y1="{top+plot_h}" y2="{top+plot_h}" stroke="#444"/>')
    out.append(f'<line x1="{left}" x2="{left}" y1="{top}" y2="{top+plot_h}" stroke="#444"/>')
    for i, (name, data) in enumerate(series.items()):
        data = data[[x_col, y_col]].dropna().sort_values(x_col)
        if data.empty:
            continue
        color = PALETTE[i % len(PALETTE)]
        pts = " ".join(f"{sx(float(r[x_col])):.1f},{sy(float(r[y_col])):.1f}" for _, r in data.iterrows())
        out.append(f'<polyline class="line" points="{pts}" stroke="{color}"/>')
        for _, r in data.iterrows():
            out.append(f'<circle cx="{sx(float(r[x_col])):.1f}" cy="{sy(float(r[y_col])):.1f}" r="3.2" fill="{color}"/>')
        out.append(f'<rect x="{width-right+18}" y="{65+i*22}" width="12" height="12" fill="{color}"/>')
        out.append(f'<text x="{width-right+36}" y="{75+i*22}">{html.escape(name)}</text>')
    out.append(f'<text class="axis" x="{left+plot_w/2}" y="{height-18}" text-anchor="middle">Year / 5-year bin</text>')
    out.append(f'<text class="axis" transform="translate(18,{top+plot_h/2}) rotate(-90)" text-anchor="middle">{html.escape(y_label)}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def save_svg_heatmap(data: pd.DataFrame, row_col: str, col_col: str, value_col: str, title: str, path: Path, width: int = 1050) -> None:
    pivot = data.pivot_table(index=row_col, columns=col_col, values=value_col, aggfunc="first").fillna(0)
    rows = list(pivot.index)
    cols = list(pivot.columns)
    cell_w, cell_h = 92, 28
    left, top = 260, 60
    height = top + len(rows) * cell_h + 60
    width = max(width, left + len(cols) * cell_w + 30)
    vals = pivot.to_numpy().flatten()
    max_val = max(float(vals.max()), 1.0)
    out = svg_header(width, height, title)
    for j, col in enumerate(cols):
        x = left + j * cell_w + cell_w / 2
        out.append(f'<text class="axis" x="{x:.1f}" y="48" text-anchor="middle">{html.escape(str(col))}</text>')
    for i, row in enumerate(rows):
        y = top + i * cell_h
        out.append(f'<text x="{left-8}" y="{y+18}" text-anchor="end">{html.escape(str(row))}</text>')
        for j, col in enumerate(cols):
            val = float(pivot.loc[row, col])
            intensity = val / max_val
            color = f"rgb({int(245-165*intensity)},{int(248-120*intensity)},{int(255-70*intensity)})"
            x = left + j * cell_w
            out.append(f'<rect x="{x}" y="{y}" width="{cell_w-2}" height="{cell_h-2}" fill="{color}" stroke="#fff"/>')
            if val:
                out.append(f'<text class="label" x="{x+cell_w/2:.1f}" y="{y+18}" text-anchor="middle">{val:.2g}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def save_svg_grouped_bars(
    data: pd.DataFrame,
    label_col: str,
    value_cols: list[str],
    title: str,
    path: Path,
    width: int = 980,
) -> None:
    data = data[[label_col] + value_cols].dropna().head(16)
    height = 80 + max(1, len(data)) * 34
    left, right, top = 250, 160, 55
    max_val = max([1.0] + [float(data[col].max()) for col in value_cols if col in data])
    out = svg_header(width, height, title)
    bar_h = 11
    for i, (_, row) in enumerate(data.iterrows()):
        base_y = top + i * 34
        out.append(f'<text x="{left-8}" y="{base_y+18}" text-anchor="end">{html.escape(str(row[label_col]))}</text>')
        for j, col in enumerate(value_cols):
            val = float(row[col])
            bar_w = (width - left - right) * val / max_val
            y = base_y + j * (bar_h + 2)
            color = PALETTE[j % len(PALETTE)]
            out.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" fill="{color}" opacity="0.88"/>')
            out.append(f'<text x="{left+bar_w+5}" y="{y+9}" class="label">{val:.2g}</text>')
    for j, col in enumerate(value_cols):
        x = width - right + 20
        y = 60 + j * 20
        out.append(f'<rect x="{x}" y="{y}" width="12" height="12" fill="{PALETTE[j % len(PALETTE)]}"/>')
        out.append(f'<text x="{x+18}" y="{y+10}">{html.escape(col)}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def text_contains(series: pd.Series, pattern: str) -> pd.Series:
    return series.fillna("").astype(str).str.contains(pattern, flags=re.I, regex=True, na=False)


def classify_by_patterns(text: str, patterns: list[tuple[str, str]], default: str) -> str:
    for label, pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            return label
    return default


def classify_semantic_family(row: pd.Series) -> str:
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
    return classify_by_patterns(text, SEMANTIC_FAMILY_PATTERNS, "other_food_or_memory")


def classify_taiwan_marker_frame(row: pd.Series) -> str:
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
    return classify_by_patterns(text, TAIWAN_MARKER_FRAME_PATTERNS, "other_taiwan_marker")


def classify_discourse_frame(row: pd.Series) -> str:
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


def classify_platform_voice(row: pd.Series) -> str:
    st = str(row.get("source_type", "")).lower()
    txt = " ".join([str(row.get("source_name", "")), str(row.get("attestation_type", "")), st]).lower()
    if any(x in txt for x in ["review", "comment", "social", "consumer", "ugc", "blog"]):
        return "consumer_or_ugc"
    if any(x in txt for x in ["official", "brand", "listing", "merchant", "platform"]):
        return "merchant_or_platform"
    return "other_voice"


def build_pack(attestations: Path, target_analysis: Path | None, out_dir: Path, fig_dir: Path, table_dir: Path) -> None:
    ensure_dir(out_dir)
    ensure_dir(fig_dir)
    ensure_dir(table_dir)
    df = clean(pd.read_csv(attestations))
    target = clean(pd.read_csv(target_analysis)) if target_analysis and target_analysis.exists() else None
    df["semantic_family"] = df.apply(classify_semantic_family, axis=1)
    df["taiwan_marker_frame"] = df.apply(classify_taiwan_marker_frame, axis=1)
    df["discourse_frame"] = df.apply(classify_discourse_frame, axis=1)
    if target is not None:
        target["semantic_family"] = target.apply(classify_semantic_family, axis=1)
        target["taiwan_marker_frame"] = target.apply(classify_taiwan_marker_frame, axis=1)
        target["discourse_frame"] = target.apply(classify_discourse_frame, axis=1)

    overview = {
        "records": int(len(df)),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "source_traceability_rate": round(float(df["source_ref"].str.len().gt(0).mean()), 4),
        "duplicate_attestation_ids": int(df["attestation_id"].duplicated().sum()) if "attestation_id" in df.columns else 0,
        "authority_distribution": df["authority_level"].value_counts().to_dict(),
        "corridor_distribution": df["corridor"].replace("", "unknown").value_counts().to_dict(),
        "period_distribution": df["period"].value_counts().to_dict(),
        "overall_binding_index": round(weighted_index(df), 4),
        "overall_positive_rate_weighted": round(weighted_positive_rate(df), 4),
    }
    (out_dir / "analysis_manifest.json").write_text(json.dumps(overview, indent=2, ensure_ascii=False), encoding="utf-8")

    overview_rows = pd.DataFrame(
        [{"metric": k, "value": json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v} for k, v in overview.items()]
    )
    write_csv(overview_rows, table_dir / "01_corpus_overview_metrics.csv")

    period_corridor = group_metrics(df, ["period", "corridor"]).sort_values(["period", "row_count"], ascending=[True, False])
    write_csv(period_corridor, table_dir / "02_period_corridor_metrics.csv")
    write_markdown_table(period_corridor, table_dir / "02_period_corridor_metrics.md")

    authority_metrics = group_metrics(df, ["authority_level"]).sort_values("binding_index", ascending=False)
    source_type_metrics = group_metrics(df, ["source_type"]).sort_values("row_count", ascending=False)
    write_csv(authority_metrics, table_dir / "03_authority_metrics.csv")
    write_csv(source_type_metrics, table_dir / "04_source_type_metrics.csv")

    taiwan_hist = df[(df["corridor"] == "Taiwan-side") & df["period"].str.startswith("1946")]
    taiwan_bins = group_metrics(taiwan_hist, ["five_year_bin"]).sort_values("five_year_bin")
    write_csv(taiwan_bins, table_dir / "05_taiwan_historical_5year_saturation.csv")

    overseas = df[df["corridor"].isin(KEY_CORRIDORS) & df["year"].between(1980, 2015)]
    overseas_bins = group_metrics(overseas, ["corridor", "five_year_bin"]).sort_values(["corridor", "five_year_bin"])
    write_csv(overseas_bins, table_dir / "06_overseas_diffusion_5year_metrics.csv")

    diffusion = []
    for corr, group in df.groupby("corridor"):
        if not corr:
            continue
        pos = group[group["is_positive"]]
        neg = group[~group["is_positive"]]
        diffusion.append(
            {
                "corridor": corr,
                "rows": len(group),
                "first_any_year": int(group["year"].min()),
                "first_positive_year": int(pos["year"].min()) if len(pos) else None,
                "first_weak_or_negative_year": int(neg["year"].min()) if len(neg) else None,
                "binding_index": round(weighted_index(group), 4),
                "positive_rate_weighted": round(weighted_positive_rate(group), 4),
                "primary_rows": int((group["authority_level"] == "primary").sum()),
            }
        )
    diffusion_df = pd.DataFrame(diffusion).sort_values(["first_any_year", "rows"], ascending=[True, False])
    write_csv(diffusion_df, table_dir / "07_corridor_first_appearance_and_binding.csv")

    text = (df["original_text"] + " " + df["text_for_scoring"] + " " + df["notes"]).fillna("")
    nost_rows = []
    for name, pattern in NOSTALGIA_PATTERNS.items():
        mask = text_contains(text, pattern)
        group = df[mask]
        nost_rows.append(
            {
                "marker_family": name,
                "rows": int(mask.sum()),
                "share_of_corpus": round(float(mask.mean()), 4),
                "binding_index": round(weighted_index(group), 4) if len(group) else 0.0,
                "positive_rate_weighted": round(weighted_positive_rate(group), 4) if len(group) else 0.0,
                "primary_rows": int((group["authority_level"] == "primary").sum()) if len(group) else 0,
            }
        )
    nostalgia_df = pd.DataFrame(nost_rows).sort_values("rows", ascending=False)
    write_csv(nostalgia_df, table_dir / "08_nostalgia_marker_cooccurrence.csv")

    dish_counts = pd.DataFrame(split_markers(df["dish_marker"]).most_common(40), columns=["dish_marker", "count"])
    taiwan_counts = pd.DataFrame(split_markers(df["taiwan_marker"]).most_common(40), columns=["taiwan_marker", "count"])
    write_csv(dish_counts, table_dir / "09_top_dish_markers.csv")
    write_csv(taiwan_counts, table_dir / "10_top_taiwan_markers.csv")

    source_ref_counts = df["source_ref"].replace("", pd.NA).dropna().value_counts().head(50)
    source_concentration = source_ref_counts.reset_index()
    source_concentration.columns = ["source_ref", "row_count"]
    source_concentration["share"] = (source_concentration["row_count"] / len(df)).round(4)
    write_csv(source_concentration, table_dir / "11_source_ref_concentration_top50.csv")

    platform = df[df["period"].str.contains("2015-2025|platform", regex=True, na=False)].copy()
    platform["speaker_proxy"] = platform.apply(classify_platform_voice, axis=1)
    platform_voice = group_metrics(platform, ["speaker_proxy"]).sort_values("row_count", ascending=False)
    write_csv(platform_voice, table_dir / "12_platform_voice_proxy_metrics.csv")

    chi_tables = []
    for var in ["corridor", "authority_level", "period"]:
        tab = pd.crosstab(df[var].replace("", "unknown"), df["is_positive"])
        stat = cramer_v(tab)
        stat["variable"] = var
        stat["levels"] = int(tab.shape[0])
        chi_tables.append(stat)
    chi_df = pd.DataFrame(chi_tables)[["variable", "levels", "chi2", "df", "cramers_v"]]
    write_csv(chi_df, table_dir / "13_exploratory_association_strength.csv")

    # When the main trend is obvious, the analytic value sits in exceptions,
    # heterogeneity, and robustness checks rather than in a rising line.
    pocket_rows = []
    for cols in [["period", "corridor"], ["period", "corridor", "source_type"], ["corridor", "authority_level"]]:
        gm = group_metrics(df, cols)
        gm["grouping"] = " + ".join(cols)
        pocket_rows.append(gm)
    pockets = pd.concat(pocket_rows, ignore_index=True)
    for col in ["period", "corridor", "source_type", "authority_level"]:
        if col in pockets.columns:
            pockets[col] = pockets[col].fillna("not_applicable").replace("", "not_applicable")
    pockets["binding_gap"] = (1.0 - pockets["binding_index"]).round(4)
    pockets = pockets[(pockets["row_count"] >= 3) & (pockets["binding_gap"] > 0.02)].sort_values(
        ["binding_gap", "row_count"], ascending=[False, False]
    )
    write_csv(pockets, table_dir / "19_low_binding_pockets.csv")

    low_binding_cases = df[df["weighted_historical_binding"] <= 0.05].sort_values(["period", "corridor", "year"])
    low_case_cols = [
        "attestation_id",
        "year",
        "period",
        "corridor",
        "brand_or_category",
        "authority_level",
        "source_type",
        "dish_marker",
        "taiwan_marker",
        "analysis_weight",
        "source_ref",
        "original_text",
    ]
    write_csv(low_binding_cases[[c for c in low_case_cols if c in low_binding_cases.columns]], table_dir / "20_low_binding_counterexamples.csv")

    base_index = weighted_index(df)
    leave_rows = []
    for source_type, group in df.groupby("source_type"):
        remaining = df[df["source_type"] != source_type]
        if len(group) < 5 or remaining.empty:
            continue
        idx_without = weighted_index(remaining)
        leave_rows.append(
            {
                "excluded_source_type": source_type,
                "excluded_rows": int(len(group)),
                "excluded_share": round(len(group) / len(df), 4),
                "binding_index_without_source_type": round(idx_without, 4),
                "delta_from_full_index": round(idx_without - base_index, 4),
            }
        )
    leave_one = pd.DataFrame(leave_rows).sort_values("delta_from_full_index")
    write_csv(leave_one, table_dir / "21_leave_one_source_type_out.csv")

    authority_source = group_metrics(df, ["authority_level", "source_type"]).sort_values(["authority_level", "row_count"], ascending=[True, False])
    authority_source["binding_gap"] = (1.0 - authority_source["binding_index"]).round(4)
    write_csv(authority_source, table_dir / "22_authority_source_cross_metrics.csv")

    deltas = []
    for corr, group in df[df["corridor"].isin(KEY_CORRIDORS)].groupby("corridor"):
        bins = group_metrics(group, ["five_year_bin"]).sort_values("five_year_bin")
        prev = None
        for _, row in bins.iterrows():
            delta = None if prev is None else round(float(row["binding_index"]) - prev, 4)
            deltas.append(
                {
                    "corridor": corr,
                    "five_year_bin": int(row["five_year_bin"]),
                    "row_count": int(row["row_count"]),
                    "binding_index": row["binding_index"],
                    "delta_from_previous_bin": delta,
                    "positive_rate_weighted": row["positive_rate_weighted"],
                }
            )
            prev = float(row["binding_index"])
    write_csv(pd.DataFrame(deltas), table_dir / "23_corridor_period_deltas.csv")

    marker_rows = []
    for corr, group in df.groupby("corridor"):
        dish_counter = split_markers(group["dish_marker"])
        taiwan_counter = split_markers(group["taiwan_marker"])
        for marker_type, counter in [("dish_marker", dish_counter), ("taiwan_marker", taiwan_counter)]:
            total = sum(counter.values())
            for marker, count in counter.most_common(12):
                marker_rows.append(
                    {
                        "corridor": corr,
                        "marker_type": marker_type,
                        "marker": marker,
                        "count": count,
                        "share_within_corridor_marker_type": round(count / total, 4) if total else 0.0,
                    }
                )
    marker_specificity = pd.DataFrame(marker_rows).sort_values(["marker_type", "corridor", "count"], ascending=[True, True, False])
    write_csv(marker_specificity, table_dir / "24_marker_specificity_by_corridor.csv")

    if target is not None and len(target):
        target_type = "target_control_type" if "target_control_type" in target.columns else "negative_type"
        control_density = target.groupby(["corridor", target_type], dropna=False).size().unstack(fill_value=0).reset_index()
        count_cols = [c for c in control_density.columns if c != "corridor"]
        control_density["target_total"] = control_density[count_cols].sum(axis=1)
        if "target_positive" in control_density.columns:
            control_density["target_positive_share"] = (control_density["target_positive"] / control_density["target_total"]).round(4)
        write_csv(control_density, table_dir / "25_target_control_density_by_corridor.csv")

    semantic_cube = group_metrics(
        df,
        ["period", "five_year_bin", "corridor", "semantic_family", "taiwan_marker_frame", "discourse_frame"],
    ).sort_values(["five_year_bin", "corridor", "semantic_family", "row_count"], ascending=[True, True, True, False])
    write_csv(semantic_cube, table_dir / "26_semantic_propagation_time_geo_cube.csv")

    semantic_geo = group_metrics(df, ["corridor", "semantic_family"]).sort_values(["corridor", "row_count"], ascending=[True, False])
    corridor_totals = semantic_geo.groupby("corridor")["row_count"].transform("sum")
    semantic_geo["share_within_corridor"] = (semantic_geo["row_count"] / corridor_totals).round(4)
    write_csv(semantic_geo, table_dir / "27_semantic_family_by_corridor.csv")

    semantic_time = group_metrics(df, ["five_year_bin", "semantic_family"]).sort_values(["five_year_bin", "row_count"], ascending=[True, False])
    bin_totals = semantic_time.groupby("five_year_bin")["row_count"].transform("sum")
    semantic_time["share_within_time_bin"] = (semantic_time["row_count"] / bin_totals).round(4)
    write_csv(semantic_time, table_dir / "28_semantic_family_by_time.csv")

    semantic_first_rows = []
    for (corr, family), group in df.groupby(["corridor", "semantic_family"]):
        if not corr or not family:
            continue
        pos = group[group["is_positive"]]
        semantic_first_rows.append(
            {
                "corridor": corr,
                "semantic_family": family,
                "rows": int(len(group)),
                "first_year": int(group["year"].min()),
                "first_positive_year": int(pos["year"].min()) if len(pos) else None,
                "last_year": int(group["year"].max()),
                "binding_index": round(weighted_index(group), 4),
                "positive_rate_weighted": round(weighted_positive_rate(group), 4),
                "primary_rows": int((group["authority_level"] == "primary").sum()),
                "unique_sources": int(group["source_ref"].replace("", pd.NA).dropna().nunique()),
            }
        )
    semantic_first = pd.DataFrame(semantic_first_rows).sort_values(["first_year", "corridor", "semantic_family"])
    write_csv(semantic_first, table_dir / "29_semantic_first_appearance_by_corridor.csv")

    marker_frame_geo = group_metrics(df, ["corridor", "taiwan_marker_frame"]).sort_values(["corridor", "row_count"], ascending=[True, False])
    marker_geo_totals = marker_frame_geo.groupby("corridor")["row_count"].transform("sum")
    marker_frame_geo["share_within_corridor"] = (marker_frame_geo["row_count"] / marker_geo_totals).round(4)
    write_csv(marker_frame_geo, table_dir / "30_taiwan_marker_frame_by_corridor.csv")

    discourse_semantic = group_metrics(df, ["discourse_frame", "semantic_family"]).sort_values(
        ["discourse_frame", "row_count"], ascending=[True, False]
    )
    write_csv(discourse_semantic, table_dir / "31_discourse_frame_by_semantic_family.csv")

    if target is not None and len(target):
        target_type = "target_control_type" if "target_control_type" in target.columns else "negative_type"
        target_metrics = group_metrics(target, ["corridor", target_type]).sort_values(["corridor", target_type])
        write_csv(target_metrics, table_dir / "14_target_positive_control_metrics.csv")
        target_by_year = group_metrics(target, ["corridor", target_type, "five_year_bin"]).sort_values(
            ["corridor", target_type, "five_year_bin"]
        )
        write_csv(target_by_year, table_dir / "15_target_positive_control_5year.csv")

    case_cols = [
        "attestation_id",
        "year",
        "period",
        "corridor",
        "brand_or_category",
        "authority_level",
        "source_type",
        "dish_marker",
        "taiwan_marker",
        "historical_binding_raw",
        "analysis_weight",
        "source_ref",
        "original_text",
    ]
    case_cols = [c for c in case_cols if c in df.columns]
    early_overseas = df[(df["corridor"].isin(["Singapore", "Japan", "North America"])) & (df["year"] <= 2000)].sort_values(
        ["year", "corridor"]
    )
    write_csv(early_overseas[case_cols].head(40), table_dir / "16_casebook_early_overseas.csv")
    write_csv(taiwan_hist.sort_values(["year", "authority_level"])[case_cols].head(40), table_dir / "17_casebook_taiwan_historical.csv")
    if target is not None and len(target):
        write_csv(target.sort_values(["year", "corridor"])[case_cols + [c for c in ["target_control_type", "negative_type"] if c in target.columns]].head(60), table_dir / "18_casebook_target_controls.csv")

    # Figures
    save_svg_barh(
        pd.DataFrame(df["period"].value_counts().head(12)).reset_index().rename(columns={"count": "rows"}),
        "period",
        "rows",
        "Corpus Records by Period",
        fig_dir / "01_period_distribution.svg",
    )
    save_svg_barh(
        pd.DataFrame(df["corridor"].replace("", "unknown").value_counts().head(12)).reset_index().rename(columns={"count": "rows"}),
        "corridor",
        "rows",
        "Corpus Records by Corridor",
        fig_dir / "02_corridor_distribution.svg",
    )
    save_svg_barh(authority_metrics, "authority_level", "row_count", "Authority-Level Distribution", fig_dir / "03_authority_distribution.svg")
    save_svg_line(
        {"Taiwan-side historical": taiwan_bins.rename(columns={"five_year_bin": "bin"})},
        "bin",
        "binding_index",
        "Taiwan-Side Historical Binding Saturation, 1946-1987",
        fig_dir / "04_taiwan_historical_saturation.svg",
    )
    line_series = {}
    for corr in ["Singapore", "Japan", "North America", "Yangtze River Delta"]:
        sub = overseas_bins[overseas_bins["corridor"] == corr].rename(columns={"five_year_bin": "bin"})
        if not sub.empty:
            line_series[corr] = sub
    save_svg_line(line_series, "bin", "binding_index", "Overseas / Regional Diffusion Binding by 5-Year Bin", fig_dir / "05_overseas_diffusion_lines.svg")
    heat = period_corridor[period_corridor["corridor"].isin(KEY_CORRIDORS)]
    save_svg_heatmap(heat, "period", "corridor", "binding_index", "Weighted Binding Index by Period and Corridor", fig_dir / "06_period_corridor_binding_heatmap.svg")
    save_svg_barh(source_type_metrics.head(15), "source_type", "row_count", "Top Source Types", fig_dir / "07_source_type_distribution.svg")
    save_svg_barh(nostalgia_df, "marker_family", "rows", "Nostalgia / Memory Marker Families", fig_dir / "08_nostalgia_marker_counts.svg")
    save_svg_barh(dish_counts.head(18), "dish_marker", "count", "Top Dish Markers", fig_dir / "09_top_dish_markers.svg")
    save_svg_barh(taiwan_counts.head(18), "taiwan_marker", "count", "Top Taiwan Markers", fig_dir / "10_top_taiwan_markers.svg")
    if target is not None and len(target):
        target_summary = group_metrics(target, ["target_control_type" if "target_control_type" in target.columns else "negative_type"])
        save_svg_barh(target_summary, target_summary.columns[0], "row_count", "Target Positive vs Weak/Negative Controls", fig_dir / "11_target_control_counts.svg")
    if not pockets.empty:
        pocket_fig = pockets.head(15).copy()
        label_parts = []
        for _, row in pocket_fig.iterrows():
            bits = [str(row.get(col, "")) for col in ["period", "corridor", "source_type", "authority_level"] if str(row.get(col, "")) and str(row.get(col, "")) != "nan"]
            label_parts.append(" / ".join(bits)[:64])
        pocket_fig["pocket_label"] = label_parts
        save_svg_barh(pocket_fig, "pocket_label", "binding_gap", "Largest Low-Binding Pockets (1 - Binding Index)", fig_dir / "12_low_binding_pockets.svg")
    if not leave_one.empty:
        leave_fig = leave_one.copy()
        leave_fig["absolute_delta"] = leave_fig["delta_from_full_index"].abs()
        leave_fig = leave_fig.sort_values("absolute_delta", ascending=False).head(15)
        save_svg_barh(leave_fig, "excluded_source_type", "absolute_delta", "Source-Type Sensitivity: Absolute Change When Excluded", fig_dir / "13_leave_one_source_type_out.svg")
    if "authority_source" in locals() and not authority_source.empty:
        auth_gap = authority_source[(authority_source["row_count"] >= 5)].sort_values("binding_gap", ascending=False).head(15).copy()
        auth_gap["authority_source"] = auth_gap["authority_level"] + " / " + auth_gap["source_type"]
        save_svg_barh(auth_gap, "authority_source", "binding_gap", "Authority x Source Low-Binding Gaps", fig_dir / "14_authority_source_gap.svg")
    if target is not None and len(target):
        density = pd.read_csv(table_dir / "25_target_control_density_by_corridor.csv")
        value_cols = [c for c in ["target_positive", "target_dish_absent_taiwan_context", "dish_only", "taiwan_only"] if c in density.columns]
        if value_cols:
            save_svg_grouped_bars(density.sort_values("target_total", ascending=False), "corridor", value_cols, "Target Positive / Control Density by Corridor", fig_dir / "15_target_control_density_by_corridor.svg")
    if "semantic_geo" in locals() and not semantic_geo.empty:
        sem_heat = semantic_geo[semantic_geo["corridor"].isin(KEY_CORRIDORS)]
        save_svg_heatmap(
            sem_heat,
            "semantic_family",
            "corridor",
            "share_within_corridor",
            "Semantic Family Share by Corridor",
            fig_dir / "16_semantic_family_by_corridor_heatmap.svg",
        )
    if "semantic_time" in locals() and not semantic_time.empty:
        top_families = semantic_time.groupby("semantic_family")["row_count"].sum().sort_values(ascending=False).head(6).index
        semantic_series = {}
        for family in top_families:
            sub = semantic_time[semantic_time["semantic_family"] == family].rename(columns={"five_year_bin": "bin"})
            if not sub.empty:
                semantic_series[family] = sub
        save_svg_line(
            semantic_series,
            "bin",
            "share_within_time_bin",
            "Semantic Family Share Over Time",
            fig_dir / "17_semantic_family_time_share.svg",
            y_label="Share within time bin",
        )
    if "marker_frame_geo" in locals() and not marker_frame_geo.empty:
        marker_heat = marker_frame_geo[marker_frame_geo["corridor"].isin(KEY_CORRIDORS)]
        save_svg_heatmap(
            marker_heat,
            "taiwan_marker_frame",
            "corridor",
            "share_within_corridor",
            "Taiwan Marker Frame Share by Corridor",
            fig_dir / "18_taiwan_marker_frame_by_corridor.svg",
        )
    if "discourse_semantic" in locals() and not discourse_semantic.empty:
        discourse_plot = discourse_semantic.copy()
        discourse_totals = discourse_plot.groupby("discourse_frame")["row_count"].transform("sum")
        discourse_plot["share_within_discourse_frame"] = (discourse_plot["row_count"] / discourse_totals).round(4)
        save_svg_heatmap(
            discourse_plot,
            "semantic_family",
            "discourse_frame",
            "share_within_discourse_frame",
            "Semantic Family Share by Discourse Frame",
            fig_dir / "19_discourse_semantic_heatmap.svg",
            width=1180,
        )

    # Narrative report
    report = [
        "# Frozen V2 Macro Analysis Pack",
        "",
        "## Core Status",
        f"- Records analysed: **{len(df)}**",
        f"- Overall weighted binding index: **{overview['overall_binding_index']:.3f}**",
        f"- Weighted positive rate: **{overview['overall_positive_rate_weighted']:.1%}**",
        f"- Source traceability: **{overview['source_traceability_rate']:.1%}**",
        f"- Authority distribution: `{overview['authority_distribution']}`",
        "",
        "## Suggested Evidence Chain",
        "1. Start with corpus structure and traceability, using `01_corpus_overview_metrics.csv` and Figures 01-03.",
        "2. Treat Taiwan-side 1946-1987 as a saturation case, not as a statistically rising trend. Use `05_taiwan_historical_5year_saturation.csv` and Figure 04.",
        "3. Move the empirical contrast to corridors and diffusion windows. Use `06_overseas_diffusion_5year_metrics.csv`, `07_corridor_first_appearance_and_binding.csv`, and Figures 05-06.",
        "4. Use target positive/control records as a sensitivity layer, not as a full causal model. Use Tables 14-15 and Figure 11.",
        "5. Use authority/source-type sensitivity to show why tourism and retrospective records are down-weighted. Use Tables 03-04 and Figure 07.",
        "6. Use nostalgia marker tables as the bridge into the platform/commodity-sign chapter. Use Table 08 and Figure 08.",
        "7. Because the positive trend is saturated, move the analysis from trend detection to exception analysis: low-binding pockets, weak controls, and leave-one-source-type-out sensitivity. Use Tables 19-25 and Figures 12-15.",
        "8. For semantic propagation, combine time, geography, semantic family, Taiwan-marker frame, and discourse frame. Use Tables 26-31 and Figures 16-19.",
        "",
        "## Important Method Note",
        "`weighted_historical_binding` is already a weighted contribution. Aggregation should use `sum(weighted_historical_binding) / sum(analysis_weight)`, not multiply by `analysis_weight` again.",
        "",
    ]
    (out_dir / "analysis_readme.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build frozen v2 descriptive analysis tables and SVG figures.")
    parser.add_argument("--attestations", default="frozen_data_v2/attestations_frozen.csv")
    parser.add_argument("--target-analysis", default="frozen_data_v2/target_binding_analysis_frozen.csv")
    parser.add_argument("--out-dir", default="analysis/frozen_v2")
    parser.add_argument("--fig-dir", default="reports/figures/frozen_v2")
    parser.add_argument("--table-dir", default="reports/tables/frozen_v2")
    args = parser.parse_args()

    target = Path(args.target_analysis) if args.target_analysis else None
    build_pack(Path(args.attestations), target, Path(args.out_dir), Path(args.fig_dir), Path(args.table_dir))
    print(f"Analysis pack written to {args.out_dir}")
    print(f"Tables written to {args.table_dir}")
    print(f"Figures written to {args.fig_dir}")


if __name__ == "__main__":
    main()
