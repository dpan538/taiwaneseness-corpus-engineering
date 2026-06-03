#!/usr/bin/env python3
"""
scripts/diagnose_all_trends.py

Build a compact dashboard for three pre-writing diagnostics:
1. Taiwan-side binding trend over time.
2. Lu rou fan vs rouzao fan semantic binding trends.
3. Multi-corridor trends and early non-Taiwan corridor links.

The script intentionally uses only the Python standard library so it can run
inside the frozen corpus workflow without adding dependencies.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from collections import defaultdict
from statistics import stdev


VERIFICATION_WEIGHTS = {
    "verified": 1.0,
    "probable": 0.7,
    "candidate": 0.3,
    "rejected": 0.0,
}

AUTHORITY_WEIGHTS = {
    "primary": 1.0,
    "secondary": 0.7,
    "tertiary": 0.4,
}

USABLE_LEVELS = {"verified", "probable"}


def parse_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        parsed = float(value)
        return parsed if math.isfinite(parsed) else default
    except (TypeError, ValueError):
        return default


def parse_int(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def period_matches(value, requested):
    if not requested:
        return True
    value = value or ""
    if value == requested:
        return True
    return requested in value or value in requested


def source_authority(row):
    level = (row.get("authority_level") or "").strip().lower()
    if level in AUTHORITY_WEIGHTS:
        return level

    source_type = (row.get("source_type") or row.get("attestation_type") or "").lower()
    source_url = (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("archive_ref")
        or ""
    ).lower()
    if any(token in source_type for token in ("newspaper", "archive", "scan", "advertisement", "ad")):
        return "primary"
    if any(token in source_url for token in ("newspaper", "dl.ndl.go.jp", "memory.culture.tw")):
        return "primary"
    if any(token in source_url for token in ("blog", "tabelog", "ameblo")):
        return "tertiary"
    return "secondary"


def row_weight(row):
    if row.get("analysis_weight"):
        return max(parse_float(row.get("analysis_weight"), 1.0), 0.0)

    novelty = parse_float(row.get("novelty_score"), 0.5)
    authority = AUTHORITY_WEIGHTS.get(source_authority(row), 0.7)
    verification = VERIFICATION_WEIGHTS.get((row.get("verification_level") or "").lower(), 0.5)
    return max(0.0, (0.5 * novelty) + (0.3 * authority) + (0.2 * verification))


def row_binding(row):
    if row.get("historical_binding_raw"):
        return max(0.0, min(1.0, parse_float(row.get("historical_binding_raw"), 0.0)))
    if row.get("weighted_historical_binding"):
        weighted = max(0.0, parse_float(row.get("weighted_historical_binding"), 0.0))
        weight = parse_float(row.get("analysis_weight"), 0.0)
        if weight > 0 and weighted <= weight:
            return max(0.0, min(1.0, weighted / weight))
        return max(0.0, min(1.0, weighted))

    dish = (row.get("dish_marker") or row.get("dish_markers") or "").strip()
    taiwan = (row.get("taiwan_marker") or row.get("taiwan_markers") or "").strip()
    brand = (row.get("brand_or_category") or "").lower()
    owner = (row.get("ownership_category") or row.get("capital_origin") or "").lower()

    lexical = 1.0 if dish and taiwan else 0.0
    branding = 1.0 if taiwan or "taiwan" in brand or "台湾" in brand or "台灣" in brand else 0.0
    ownership = 1.0 if "taiwan" in owner or "台湾" in owner or "台灣" in owner else 0.0
    return max(0.0, min(1.0, (0.5 * lexical) + (0.25 * branding) + (0.25 * ownership)))


def load_records(path, period_filter=None, usable_only=True):
    records = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if period_filter and not period_matches(row.get("period"), period_filter):
                continue
            year = parse_int(row.get("year"))
            if year is None:
                continue
            level = (row.get("verification_level") or "").strip().lower()
            if usable_only and level and level not in USABLE_LEVELS:
                continue
            row["_year"] = year
            row["_binding"] = row_binding(row)
            row["_weight"] = row_weight(row)
            if row["_weight"] <= 0:
                continue
            records.append(row)
    return records


def inspect_signal_columns(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
    has_binding = "weighted_historical_binding" in fields
    has_raw_binding = "historical_binding_raw" in fields
    has_weight = "analysis_weight" in fields
    if has_binding and has_weight:
        mode = "explicit_weighted_binding"
    elif has_binding:
        mode = "explicit_binding_default_weight"
    else:
        mode = "fallback_row_heuristic"
    return {
        "mode": mode,
        "has_weighted_historical_binding": has_binding,
        "has_historical_binding_raw": has_raw_binding,
        "has_analysis_weight": has_weight,
        "strict_writing_ready_allowed": has_binding and has_weight,
    }


def year_bin(year, interval):
    if interval <= 1:
        return year
    return (year // interval) * interval


def aggregate_by_year(records, year_interval=5, key_func=None):
    buckets = defaultdict(lambda: defaultdict(lambda: {"weighted_sum": 0.0, "weight_sum": 0.0, "n": 0}))
    for row in records:
        key = key_func(row) if key_func else "all"
        bucket = year_bin(row["_year"], year_interval)
        buckets[key][bucket]["weighted_sum"] += row["_binding"] * row["_weight"]
        buckets[key][bucket]["weight_sum"] += row["_weight"]
        buckets[key][bucket]["n"] += 1

    result = {}
    for key, grouped in buckets.items():
        years = sorted(grouped)
        values = []
        weights = []
        counts = []
        for year in years:
            weight_sum = grouped[year]["weight_sum"]
            values.append(grouped[year]["weighted_sum"] / weight_sum if weight_sum else None)
            weights.append(weight_sum)
            counts.append(grouped[year]["n"])
        result[key] = (years, values, weights, counts)
    return result


def weighted_slope(years, values, weights):
    clean = [(y, v, w) for y, v, w in zip(years, values, weights) if v is not None and w > 0]
    if len(clean) < 2:
        return None
    total_w = sum(item[2] for item in clean)
    if total_w <= 0:
        return None
    x_mean = sum(y * w for y, _, w in clean) / total_w
    y_mean = sum(v * w for _, v, w in clean) / total_w
    cov = sum(w * (y - x_mean) * (v - y_mean) for y, v, w in clean)
    var_x = sum(w * (y - x_mean) ** 2 for y, _, w in clean)
    return cov / var_x if var_x else None


def bootstrap_trend(years, values, weights, iterations=500):
    paired = [(y, v, w) for y, v, w in zip(years, values, weights) if v is not None and w > 0]
    if len(paired) < 3:
        return None, None, None, None

    observed = weighted_slope(
        [item[0] for item in paired],
        [item[1] for item in paired],
        [item[2] for item in paired],
    )
    if observed is None:
        return None, None, None, None
    if abs(observed) < 1e-12:
        return observed, 0.0, 0.0, 1.0

    slopes = []
    for _ in range(iterations):
        sample = [paired[random.randrange(len(paired))] for _ in paired]
        slope = weighted_slope(
            [item[0] for item in sample],
            [item[1] for item in sample],
            [item[2] for item in sample],
        )
        if slope is not None:
            slopes.append(slope)
    if not slopes:
        return observed, None, None, None

    slopes.sort()
    low_idx = max(0, min(len(slopes) - 1, int(0.025 * len(slopes))))
    high_idx = max(0, min(len(slopes) - 1, int(0.975 * len(slopes))))
    ci_low = slopes[low_idx]
    ci_high = slopes[high_idx]
    if observed >= 0:
        p_value = sum(1 for slope in slopes if slope < 0) / len(slopes)
    else:
        p_value = sum(1 for slope in slopes if slope > 0) / len(slopes)
    return observed, ci_low, ci_high, p_value


def stability_rating(ci_low, ci_high):
    if ci_low is None or ci_high is None:
        return "insufficient"
    width = ci_high - ci_low
    if width < 0.1:
        return "high"
    if width < 0.2:
        return "medium"
    return "low"


def summarize_group(records, years, values, weights, counts, iterations):
    slope, ci_low, ci_high, p_value = bootstrap_trend(years, values, weights, iterations)
    return {
        "num_records": len(records),
        "years_covered": [year for year, value in zip(years, values) if value is not None],
        "time_series": [
            {
                "year_bin": year,
                "binding_index": round(value, 6) if value is not None else None,
                "weight_sum": round(weight, 4),
                "n": count,
            }
            for year, value, weight, count in zip(years, values, weights, counts)
        ],
        "slope": slope,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "stability": stability_rating(ci_low, ci_high),
        "trend_emerged": p_value is not None and p_value < 0.10,
    }


def trend_taiwan_domestic(records, year_interval, iterations):
    subset = [row for row in records if (row.get("corridor") or "").strip() == "Taiwan-side"]
    if not subset:
        return None
    aggregate = aggregate_by_year(subset, year_interval)
    years, values, weights, counts = aggregate["all"]
    return summarize_group(subset, years, values, weights, counts, iterations)


def dish_type(row):
    text = " ".join(
        str(row.get(field) or "")
        for field in ("dish_marker", "dish_markers", "original_text", "window_text_concatenated", "brand_or_category")
    ).lower()
    if any(token in text for token in ("滷肉飯", "魯肉飯", "卤肉饭", "鲁肉饭", "ルーローハン", "lu rou", "braised pork rice")):
        return "lu_rou_fan"
    if any(token in text for token in ("肉燥", "肉臊", "rouzao", "rou zao")):
        return "rouzao_fan"
    if any(token in text for token in ("porridge", "粥")):
        return "porridge"
    if text.strip():
        return "other"
    return "unknown"


def trend_dish_semantic(records, year_interval, iterations):
    aggregate = aggregate_by_year(records, year_interval, key_func=dish_type)
    results = {}
    for key in sorted(aggregate):
        subset = [row for row in records if dish_type(row) == key]
        years, values, weights, counts = aggregate[key]
        results[key] = summarize_group(subset, years, values, weights, counts, iterations)
    return results


def trend_geo_network(records, corridors, year_interval, iterations, early_threshold_year):
    aggregate = aggregate_by_year(records, year_interval, key_func=lambda row: (row.get("corridor") or "unknown").strip())
    results = {}
    early_links = []

    for corridor in corridors:
        if corridor not in aggregate:
            results[corridor] = {
                "num_records": 0,
                "years_covered": [],
                "time_series": [],
                "slope": None,
                "p_value": None,
                "ci_low": None,
                "ci_high": None,
                "stability": "insufficient",
                "trend_emerged": False,
            }
            continue
        subset = [row for row in records if (row.get("corridor") or "").strip() == corridor]
        years, values, weights, counts = aggregate[corridor]
        results[corridor] = summarize_group(subset, years, values, weights, counts, iterations)

    for corridor, summary in results.items():
        if corridor == "Taiwan-side":
            continue
        for point in summary.get("time_series", []):
            value = point.get("binding_index")
            if point.get("year_bin") <= early_threshold_year and value is not None and value > 0.05:
                early_links.append(
                    {
                        "corridor": corridor,
                        "first_year_bin": point["year_bin"],
                        "first_binding": value,
                        "n": point["n"],
                    }
                )
                break

    return results, early_links


def effective_n(weights):
    total = sum(weights)
    total_sq = sum(weight * weight for weight in weights)
    return (total * total / total_sq) if total_sq else 0.0


def sample_sufficiency(records, target_ci_half_width):
    values = [row["_binding"] for row in records]
    weights = [row["_weight"] for row in records]
    if len(values) < 2:
        return {
            "effective_n": round(effective_n(weights), 2),
            "mean_binding": None,
            "ci_half_width": None,
            "estimated_additional_records_needed": None,
            "interpretation": "insufficient",
        }

    weighted_mean = sum(v * w for v, w in zip(values, weights)) / sum(weights)
    std = stdev(values)
    n_eff = effective_n(weights)
    if n_eff <= 0:
        half_width = None
        needed = None
    else:
        half_width = 1.96 * std / math.sqrt(n_eff)
        if half_width <= target_ci_half_width:
            needed = 0
        else:
            target_n = (1.96 * std / target_ci_half_width) ** 2
            needed = max(0, int(math.ceil(target_n - n_eff)))

    return {
        "effective_n": round(n_eff, 2),
        "mean_binding": round(weighted_mean, 6),
        "ci_half_width": round(half_width, 6) if half_width is not None else None,
        "estimated_additional_records_needed": needed,
        "interpretation": "sufficient" if needed == 0 else "insufficient",
    }


def format_number(value, digits=4):
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


def build_markdown(dashboard):
    taiwan = dashboard["trend_taiwan_domestic"]
    sample = dashboard["sample_sufficiency"]
    lines = [
        "# Trend Diagnosis Dashboard",
        "",
        f"**Period**: {dashboard['period']}",
        f"**Total usable records in analysis**: {dashboard['total_records']}",
        f"**Binding signal mode**: {dashboard['binding_signal']['mode']}",
        f"**Strict writing-ready allowed**: {'Yes' if dashboard['binding_signal']['strict_writing_ready_allowed'] else 'No'}",
        "",
        "## Sample Sufficiency",
        f"- Effective n: {sample['effective_n']}",
        f"- Mean binding: {format_number(sample['mean_binding'], 4)}",
        f"- CI half-width: {format_number(sample['ci_half_width'], 4)}",
        f"- Estimated additional records needed: {sample['estimated_additional_records_needed'] if sample['estimated_additional_records_needed'] is not None else 'N/A'}",
        f"- Sufficient? {'Yes' if sample['interpretation'] == 'sufficient' else 'No'}",
        "",
        "## Trend 1: Taiwan Domestic Evolution",
    ]
    if taiwan:
        lines.extend(
            [
                f"- Records: {taiwan['num_records']}",
                f"- Slope: {format_number(taiwan['slope'])} (p={format_number(taiwan['p_value'])})",
                f"- 95% slope CI: [{format_number(taiwan['ci_low'])}, {format_number(taiwan['ci_high'])}]",
                f"- Stability: {taiwan['stability']}",
                f"- Trend emerged? {'Yes' if taiwan['trend_emerged'] else 'No'}",
            ]
        )
    else:
        lines.append("- No Taiwan-side records in this period.")

    lines.extend(["", "## Trend 2: Dish Semantic"])
    for key, summary in dashboard["trend_dish_semantic"].items():
        lines.extend(
            [
                "",
                f"### {key}",
                f"- Records: {summary['num_records']}",
                f"- Slope: {format_number(summary['slope'])} (p={format_number(summary['p_value'])})",
                f"- Stability: {summary['stability']}",
                f"- Trend emerged? {'Yes' if summary['trend_emerged'] else 'No'}",
            ]
        )

    lines.extend(["", "## Trend 3: Geo-Network"])
    for corridor, summary in dashboard["trend_geo_network"].items():
        lines.extend(
            [
                "",
                f"### {corridor}",
                f"- Records: {summary['num_records']}",
                f"- Slope: {format_number(summary['slope'])} (p={format_number(summary['p_value'])})",
                f"- Stability: {summary['stability']}",
                f"- Trend emerged? {'Yes' if summary['trend_emerged'] else 'No'}",
            ]
        )

    lines.extend(["", "## Unique Early Corridors"])
    if dashboard["unique_early_corridors"]:
        for item in dashboard["unique_early_corridors"]:
            lines.append(
                f"- {item['corridor']}: first binding bin {item['first_year_bin']} "
                f"(binding={format_number(item['first_binding'], 3)}, n={item['n']})"
            )
    else:
        lines.append("- No early non-Taiwan corridor links detected.")

    lines.extend(
        [
            "",
            "## Final Recommendation",
            dashboard["recommendation"],
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a combined trend diagnosis dashboard.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--period", default="1946-1987_taiwan_side_formation")
    parser.add_argument("--year-interval", type=int, default=5)
    parser.add_argument("--corridors", nargs="+", default=["Taiwan-side", "Singapore", "Japan", "North America"])
    parser.add_argument("--early-threshold-year", type=int, default=1980)
    parser.add_argument("--bootstrap-iterations", type=int, default=500)
    parser.add_argument("--target-ci-half-width", type=float, default=0.05)
    parser.add_argument("--out-dir", default="reports/trend_diagnosis")
    parser.add_argument("--seed", type=int, default=20260603)
    args = parser.parse_args()

    random.seed(args.seed)
    signal_info = inspect_signal_columns(args.attestations)
    records = load_records(args.attestations, period_filter=args.period)
    if not records:
        print(f"No usable records found for period {args.period}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)

    taiwan = trend_taiwan_domestic(records, args.year_interval, args.bootstrap_iterations)
    dish = trend_dish_semantic(records, args.year_interval, args.bootstrap_iterations)
    geo, early_links = trend_geo_network(
        records,
        args.corridors,
        args.year_interval,
        args.bootstrap_iterations,
        args.early_threshold_year,
    )
    sample = sample_sufficiency(records, args.target_ci_half_width)

    taiwan_ready = bool(taiwan and taiwan["trend_emerged"] and taiwan["stability"] == "high")
    key_dish_summaries = [dish[key] for key in ("lu_rou_fan", "rouzao_fan") if key in dish]
    dish_ready = any(item["trend_emerged"] and item["stability"] == "high" for item in key_dish_summaries)
    geo_ready = any(item["trend_emerged"] and item["stability"] == "high" for item in geo.values())
    sample_ok = sample["estimated_additional_records_needed"] == 0
    preliminary_writing_ready = taiwan_ready and dish_ready and sample_ok
    writing_ready = preliminary_writing_ready and signal_info["strict_writing_ready_allowed"]

    if writing_ready:
        recommendation = (
            "Writing-ready for the historical trend chapter. The main domestic trend, at least one key dish "
            "semantic trend, and sample sufficiency all pass the diagnostic threshold. Keep the weighted/cleaned "
            "results as the main analysis and report unweighted results as sensitivity checks."
        )
    elif preliminary_writing_ready:
        recommendation = (
            "Preliminary trends are visible, but strict writing-ready status is withheld because this input lacks "
            "explicit per-row weighted_historical_binding and analysis_weight columns. Recompute the row-level "
            "weighted corpus, rerun this dashboard, and treat the current result as a directional pretest."
        )
    else:
        reasons = []
        if not taiwan_ready:
            reasons.append("Taiwan domestic trend is not both significant and highly stable")
        if not dish_ready:
            reasons.append("lu rou fan / rouzao fan semantic trend is not yet clear enough")
        if not sample_ok:
            reasons.append(
                f"estimated additional records needed is {sample['estimated_additional_records_needed']}"
            )
        if not geo_ready:
            reasons.append("geo-network trend is still exploratory")
        recommendation = (
            "Not yet ready for strong historical-trend writing. "
            + "; ".join(reasons)
            + ". Continue targeted collection, prioritizing under-covered Taiwan-side years and dish-specific primary records."
        )

    dashboard = {
        "period": args.period,
        "attestations_file": args.attestations,
        "total_records": len(records),
        "year_interval": args.year_interval,
        "binding_signal": signal_info,
        "sample_sufficiency": sample,
        "trend_taiwan_domestic": taiwan,
        "trend_dish_semantic": dish,
        "trend_geo_network": geo,
        "unique_early_corridors": early_links,
        "readiness": {
            "taiwan_ready": taiwan_ready,
            "dish_ready": dish_ready,
            "geo_ready": geo_ready,
            "sample_ok": sample_ok,
            "preliminary_writing_ready": preliminary_writing_ready,
            "writing_ready": writing_ready,
        },
        "preliminary_writing_ready": preliminary_writing_ready,
        "writing_ready": writing_ready,
        "recommendation": recommendation,
    }

    json_path = os.path.join(args.out_dir, "trend_dashboard.json")
    md_path = os.path.join(args.out_dir, "trend_dashboard.md")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(dashboard, handle, indent=2, ensure_ascii=False)
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write(build_markdown(dashboard))

    print(f"Dashboard saved to {md_path}")
    print(f"Recommendation: {recommendation}")


if __name__ == "__main__":
    main()
