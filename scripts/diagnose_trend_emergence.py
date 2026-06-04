#!/usr/bin/env python3
"""Diagnose whether a binding-index time series already shows a stable trend."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path


AUTHORITY_WEIGHTS = {"primary": 1.0, "secondary": 0.7, "tertiary": 0.4}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose trend emergence in the attestation corpus.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--period", default="1946-1987_taiwan_side_formation")
    parser.add_argument("--binding-type", default="historical", choices=["lexical", "historical"])
    parser.add_argument("--year-interval", type=int, default=5)
    parser.add_argument("--bootstrap-iterations", type=int, default=1000)
    parser.add_argument("--target-ci-half-width", type=float, default=0.1)
    parser.add_argument("--output-dir", default="reports/trend_diagnosis")
    parser.add_argument("--seed", type=int, default=20260603)
    return parser.parse_args()


def read_csv(path: str) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def float_value(value: object, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def year_of(row: dict) -> int | None:
    try:
        return int(float(row.get("year") or ""))
    except (TypeError, ValueError):
        return None


def usable(row: dict) -> bool:
    return (row.get("verification_level") or "verified").strip().lower() in {"verified", "probable", ""}


def period_matches(row: dict, period_filter: str) -> bool:
    if not period_filter:
        return True
    period = (row.get("period") or "").strip()
    if period == period_filter:
        return True
    compact = period_filter.replace("_", "-")
    if compact in period or period_filter in period:
        return True
    if period_filter in {"1946-1987", "1946_1987"}:
        year = year_of(row)
        return year is not None and 1946 <= year <= 1987
    if period_filter in {"1987-2015", "1987_2015"}:
        year = year_of(row)
        return year is not None and 1988 <= year <= 2014
    if period_filter in {"2015-2025", "2015_2025"}:
        year = year_of(row)
        return year is not None and 2015 <= year <= 2025
    return False


def authority_weight(row: dict) -> float:
    if row.get("authority_weight"):
        return max(0.0, min(1.0, float_value(row.get("authority_weight"), 0.5)))
    level = (row.get("authority_level") or "").strip().lower()
    if level:
        return AUTHORITY_WEIGHTS.get(level, 0.5)
    source_type = (row.get("source_type") or "").strip().lower()
    if any(token in source_type for token in ("newspaper", "archive", "api", "scan")):
        return 1.0
    if any(token in source_type for token in ("blog", "review", "forum")):
        return 0.4
    return 0.7


def analysis_weight(row: dict) -> float:
    if row.get("analysis_weight"):
        return max(0.0, min(1.0, float_value(row.get("analysis_weight"), 0.5)))
    novelty = max(0.0, min(1.0, float_value(row.get("novelty_score"), 0.5)))
    return (0.6 * novelty) + (0.4 * authority_weight(row))


def marker_present(row: dict, *fields: str) -> bool:
    return any((row.get(field) or "").strip() for field in fields)


def brand_has_taiwan(row: dict) -> bool:
    text = " ".join(
        [
            row.get("brand_or_category") or "",
            row.get("brand") or "",
            row.get("taiwan_marker") or "",
        ]
    ).lower()
    return any(token in text for token in ("taiwan", "taiwanese", "formosa", "台", "寶島", "宝岛"))


def row_binding_value(row: dict, binding_type: str) -> tuple[float, float]:
    weight = analysis_weight(row)
    if row.get("weighted_historical_binding") and binding_type == "historical":
        return float_value(row.get("weighted_historical_binding"), 0.0), weight

    dish = 1.0 if marker_present(row, "dish_marker", "dish_markers", "matched_dish_markers") else 0.0
    taiwan = 1.0 if marker_present(row, "taiwan_marker", "taiwan_markers", "matched_taiwan_markers") else 0.0
    proximity = float_value(row.get("lexical_proximity"), 1.0 if dish and taiwan else 0.0)
    lexical = dish * taiwan * proximity
    if binding_type == "lexical":
        return lexical, weight

    branding = 1.0 if brand_has_taiwan(row) else 0.0
    owner = (row.get("ownership_category") or "").strip()
    ownership = 1.0 if owner == "Taiwan_capital" else 0.0
    historical = (0.5 * lexical) + (0.25 * branding) + (0.25 * ownership)
    return historical, weight


def year_bin(year: int, interval: int) -> int:
    if interval <= 1:
        return year
    return (year // interval) * interval


def aggregate(records: list[dict], binding_type: str, year_interval: int) -> list[dict]:
    groups: dict[int, dict] = defaultdict(lambda: {"weighted_sum": 0.0, "weight_sum": 0.0, "n": 0})
    for row in records:
        year = year_of(row)
        if year is None:
            continue
        value, weight = row_binding_value(row, binding_type)
        key = year_bin(year, year_interval)
        groups[key]["weighted_sum"] += value * weight
        groups[key]["weight_sum"] += weight
        groups[key]["n"] += 1

    out = []
    for key in sorted(groups):
        group = groups[key]
        weight_sum = group["weight_sum"]
        out.append(
            {
                "year_bin": key,
                "binding_index": group["weighted_sum"] / weight_sum if weight_sum > 0 else None,
                "weight_sum": weight_sum,
                "n_records": group["n"],
            }
        )
    return out


def weighted_slope(xs: list[float], ys: list[float], ws: list[float]) -> float:
    weight_sum = sum(ws)
    if weight_sum <= 0:
        return 0.0
    x_mean = sum(w * x for x, w in zip(xs, ws)) / weight_sum
    y_mean = sum(w * y for y, w in zip(ys, ws)) / weight_sum
    cov = sum(w * (x - x_mean) * (y - y_mean) for x, y, w in zip(xs, ys, ws))
    var_x = sum(w * (x - x_mean) ** 2 for x, w in zip(xs, ws))
    return cov / var_x if var_x else 0.0


def bootstrap_trend(rows: list[dict], iterations: int) -> dict:
    usable_rows = [r for r in rows if r["binding_index"] is not None and r["weight_sum"] > 0]
    if len(usable_rows) < 3:
        return {"slope": None, "ci_low": None, "ci_high": None, "p_value": None}

    xs = [float(r["year_bin"]) for r in usable_rows]
    ys = [float(r["binding_index"]) for r in usable_rows]
    ws = [float(r["weight_sum"]) for r in usable_rows]
    observed = weighted_slope(xs, ys, ws)

    slopes = []
    n = len(usable_rows)
    for _ in range(iterations):
        sample = [usable_rows[random.randrange(n)] for _ in range(n)]
        slopes.append(
            weighted_slope(
                [float(r["year_bin"]) for r in sample],
                [float(r["binding_index"]) for r in sample],
                [float(r["weight_sum"]) for r in sample],
            )
        )
    slopes.sort()
    ci_low = slopes[int(0.025 * (iterations - 1))]
    ci_high = slopes[int(0.975 * (iterations - 1))]
    if observed >= 0:
        p_value = sum(1 for slope in slopes if slope < 0) / iterations
    else:
        p_value = sum(1 for slope in slopes if slope > 0) / iterations
    return {"slope": observed, "ci_low": ci_low, "ci_high": ci_high, "p_value": p_value}


def row_level_stats(records: list[dict], binding_type: str) -> dict:
    values = []
    weights = []
    for row in records:
        value, weight = row_binding_value(row, binding_type)
        if weight > 0:
            values.append(value)
            weights.append(weight)
    if len(values) < 2:
        return {"effective_n": len(values), "mean": None, "sd": None, "ci_half_width": None}
    weight_sum = sum(weights)
    effective_n = (weight_sum * weight_sum) / sum(w * w for w in weights)
    mean_value = sum(v * w for v, w in zip(values, weights)) / weight_sum
    variance = sum(w * (v - mean_value) ** 2 for v, w in zip(values, weights)) / weight_sum
    sd = math.sqrt(max(0.0, variance))
    ci_half_width = 1.96 * sd / math.sqrt(effective_n) if effective_n > 0 else None
    return {"effective_n": effective_n, "mean": mean_value, "sd": sd, "ci_half_width": ci_half_width}


def estimate_needed_records(stats: dict, target_half_width: float, average_weight: float) -> int | None:
    if stats["sd"] is None or stats["effective_n"] <= 0 or target_half_width <= 0:
        return None
    current_half_width = stats["ci_half_width"]
    if current_half_width is not None and current_half_width <= target_half_width:
        return 0
    target_effective_n = (1.96 * stats["sd"] / target_half_width) ** 2
    additional_effective = max(0.0, target_effective_n - stats["effective_n"])
    if average_weight <= 0:
        return math.ceil(additional_effective)
    return math.ceil(additional_effective / average_weight)


def fmt(value: object, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_outputs(output_dir: Path, rows: list[dict], summary: dict, attestations_path: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts_path = output_dir / "trend_diagnosis.csv"
    with ts_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["year_bin", "binding_index", "weight_sum", "n_records"],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "year_bin": row["year_bin"],
                    "binding_index": "" if row["binding_index"] is None else f"{row['binding_index']:.6f}",
                    "weight_sum": f"{row['weight_sum']:.4f}",
                    "n_records": row["n_records"],
                }
            )

    with (output_dir / "trend_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    md = f"""# Trend Diagnosis Report

**Period**: {summary['period']}
**Binding type**: {summary['binding_type']}
**Records used**: {summary['number_of_records']}
**Year bins with data**: {summary['number_of_year_bins_with_data']}

## Trend Analysis
- Observed slope: {fmt(summary['trend_slope'], 6)} per year
- Bootstrap p-value: {fmt(summary['trend_p_value'])}
- 95% CI: [{fmt(summary['trend_confidence_interval_low'], 6)}, {fmt(summary['trend_confidence_interval_high'], 6)}]
- Trend emerged: {'YES' if summary['trend_emerged'] else 'NO'}
- Stability: {summary['stability_rating']}

## Sample Adequacy
- Effective n: {fmt(summary['effective_n'], 2)}
- Mean binding index: {fmt(summary['mean_binding_index'])}
- Current CI half-width: {fmt(summary['current_ci_half_width'])}
- Estimated additional records needed: {summary['estimated_additional_records_needed']}

## Recommendation
{summary['recommendation']}

---
Data file: `{attestations_path}`
Time series CSV: `{ts_path}`
"""
    with (output_dir / "trend_diagnosis.md").open("w", encoding="utf-8") as f:
        f.write(md)


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    records = [r for r in read_csv(args.attestations) if usable(r) and period_matches(r, args.period)]
    if not records:
        raise SystemExit(f"No usable records matched period {args.period}")

    rows = aggregate(records, args.binding_type, args.year_interval)
    trend = bootstrap_trend(rows, args.bootstrap_iterations)
    bin_ci_width = None
    if trend["ci_low"] is not None and trend["ci_high"] is not None:
        bin_ci_width = trend["ci_high"] - trend["ci_low"]

    trend_emerged = trend["p_value"] is not None and trend["p_value"] < 0.10
    if bin_ci_width is None:
        stability = "insufficient data"
    elif bin_ci_width < 0.1:
        stability = "high"
    elif bin_ci_width < 0.2:
        stability = "medium"
    else:
        stability = "low"

    stats = row_level_stats(records, args.binding_type)
    avg_weight = sum(row_binding_value(r, args.binding_type)[1] for r in records) / len(records)
    needed = estimate_needed_records(stats, args.target_ci_half_width, avg_weight)

    if not trend_emerged:
        recommendation = "No clear directional trend yet. Continue collecting, prioritizing thin early bins."
    elif stability in {"low", "medium"}:
        recommendation = (
            f"Trend direction is visible, but stability is {stability}. "
            f"Add about {needed} records before treating it as a stable historical trend."
        )
    else:
        recommendation = (
            f"Stable trend detected. Begin exploratory writing, while adding about {needed} records for robustness."
        )

    summary = {
        "period": args.period,
        "binding_type": args.binding_type,
        "year_interval": args.year_interval,
        "number_of_records": len(records),
        "number_of_year_bins_with_data": sum(1 for row in rows if row["binding_index"] is not None),
        "trend_slope": trend["slope"],
        "trend_p_value": trend["p_value"],
        "trend_confidence_interval_low": trend["ci_low"],
        "trend_confidence_interval_high": trend["ci_high"],
        "trend_emerged": trend_emerged,
        "stability_rating": stability,
        "effective_n": stats["effective_n"],
        "mean_binding_index": stats["mean"],
        "current_ci_half_width": stats["ci_half_width"],
        "estimated_additional_records_needed": needed,
        "recommendation": recommendation,
    }
    write_outputs(Path(args.output_dir), rows, summary, args.attestations)
    print(f"Diagnostic report written to {Path(args.output_dir) / 'trend_diagnosis.md'}")
    print(f"Recommendation: {recommendation}")


if __name__ == "__main__":
    main()
