#!/usr/bin/env python3
"""
scripts/writing_readiness_assessor.py

Assess whether the weighted Taiwan-side historical corpus is ready for writing.
Outputs JSON and Markdown reports with a direct status:
ready / almost_ready / keep_collecting.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from datetime import date
from pathlib import Path


USABLE_LEVELS = {"verified", "probable", ""}


def parse_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        parsed = float(value)
        return parsed if math.isfinite(parsed) else default
    except (TypeError, ValueError):
        return default


def parse_year(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def period_matches(value, requested):
    value = value or ""
    return value == requested or requested in value or value in requested


def source_bucket(source_type):
    source_type = (source_type or "").lower()
    if "newspaper" in source_type or "archive" in source_type or "scan" in source_type:
        return "newspaper_archive"
    if "tourism" in source_type or "municipal" in source_type or "travel" in source_type:
        return "tourism_retrospective"
    if "blog" in source_type or "review" in source_type or "social" in source_type:
        return "blog_review"
    return "other"


def load_records(path, period, corridor):
    records = []
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if (row.get("verification_level") or "").strip().lower() not in USABLE_LEVELS:
                continue
            if (row.get("corridor") or "").strip() != corridor:
                continue
            if not period_matches(row.get("period"), period):
                continue
            year = parse_year(row.get("year"))
            if year is None:
                continue
            weight = parse_float(row.get("analysis_weight"), 1.0)
            weighted = parse_float(row.get("weighted_historical_binding"), 0.0)
            if row.get("historical_binding_raw"):
                binding_value = parse_float(row.get("historical_binding_raw"), 0.0)
            elif weight > 0 and weighted <= weight:
                binding_value = weighted / weight
            else:
                binding_value = weighted
            records.append(
                {
                    "year": year,
                    "binding": max(0.0, min(1.0, binding_value)),
                    "weight": max(0.0, weight),
                    "source_type": row.get("source_type", ""),
                    "authority_level": row.get("authority_level", ""),
                }
            )
    return records


def weighted_slope(records):
    if len(records) < 3:
        return None
    weight_sum = sum(row["weight"] for row in records)
    if weight_sum <= 0:
        return None
    x_mean = sum(row["year"] * row["weight"] for row in records) / weight_sum
    y_mean = sum(row["binding"] * row["weight"] for row in records) / weight_sum
    cov = sum(row["weight"] * (row["year"] - x_mean) * (row["binding"] - y_mean) for row in records)
    var_x = sum(row["weight"] * (row["year"] - x_mean) ** 2 for row in records)
    return cov / var_x if var_x else None


def bootstrap_trend(records, iterations):
    observed = weighted_slope(records)
    if observed is None or len(records) < 10:
        return observed, None, None, None, "insufficient"
    if abs(observed) < 1e-12:
        return observed, 1.0, 0.0, (0.0, 0.0), "high"

    slopes = []
    for _ in range(iterations):
        sample = [records[random.randrange(len(records))] for _ in records]
        slope = weighted_slope(sample)
        if slope is not None:
            slopes.append(slope)
    if not slopes:
        return observed, None, None, None, "error"

    slopes.sort()
    low = slopes[max(0, min(len(slopes) - 1, int(0.025 * len(slopes))))]
    high = slopes[max(0, min(len(slopes) - 1, int(0.975 * len(slopes))))]
    if observed >= 0:
        p_value = sum(1 for slope in slopes if slope < 0) / len(slopes)
    else:
        p_value = sum(1 for slope in slopes if slope > 0) / len(slopes)
    ci_width = high - low
    if ci_width < 0.1:
        stability = "high"
    elif ci_width < 0.2:
        stability = "medium"
    else:
        stability = "low"
    return observed, p_value, ci_width, (low, high), stability


def effective_n(records):
    weights = [row["weight"] for row in records]
    total = sum(weights)
    total_sq = sum(weight * weight for weight in weights)
    return (total * total / total_sq) if total_sq else 0.0


def make_recommendation(status, needed, tourism_ratio, p_value, stability):
    if status == "ready":
        return (
            "READY: Begin historical analysis writing under the v2 weighted method. "
            "Report v1/unweighted results as sensitivity checks."
        )
    if status == "almost_ready":
        return (
            "ALMOST READY: The trend is detectable, but the corpus would benefit from a small number of "
            "additional primary newspaper/archive records before freezing."
        )
    return (
        f"KEEP COLLECTING: add at least {needed} Taiwan-side records and prioritize primary newspaper/archive "
        f"sources. Current tourism-retrospective ratio is {tourism_ratio:.1%}; trend p={p_value if p_value is not None else 'N/A'}, "
        f"stability={stability}."
    )


def main():
    parser = argparse.ArgumentParser(description="Assess writing readiness from weighted attestations.")
    parser.add_argument("--weighted-attestations", required=True)
    parser.add_argument("--period", default="1946-1987_taiwan_side_formation")
    parser.add_argument("--corridor", default="Taiwan-side")
    parser.add_argument("--target-records", type=int, default=350)
    parser.add_argument("--max-tourism-ratio", type=float, default=0.40)
    parser.add_argument("--bootstrap-iterations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260604)
    parser.add_argument("--out-json", default="reports/writing_readiness.json")
    parser.add_argument("--out-md", default="reports/writing_readiness.md")
    args = parser.parse_args()

    random.seed(args.seed)
    records = load_records(args.weighted_attestations, args.period, args.corridor)
    if not records:
        raise SystemExit("No matching weighted records found.")

    n_records = len(records)
    needed = max(0, args.target_records - n_records)
    slope, p_value, ci_width, ci, stability = bootstrap_trend(records, args.bootstrap_iterations)
    buckets = Counter(source_bucket(row["source_type"]) for row in records)
    authority = Counter((row["authority_level"] or "missing").lower() for row in records)
    tourism_ratio = buckets["tourism_retrospective"] / n_records if n_records else 0.0
    n_eff = effective_n(records)

    trend_detectable = p_value is not None and p_value < 0.10
    strong_trend = p_value is not None and p_value < 0.05 and stability == "high"
    balanced = tourism_ratio <= args.max_tourism_ratio

    if n_records >= args.target_records and trend_detectable and stability in {"high", "medium"} and balanced:
        status = "ready"
    elif n_records >= args.target_records and strong_trend:
        status = "ready"
    elif n_records >= max(0, args.target_records - 25) and trend_detectable and stability in {"high", "medium"}:
        status = "almost_ready"
    else:
        status = "keep_collecting"

    recommendation = make_recommendation(status, needed, tourism_ratio, p_value, stability)
    result = {
        "status": status,
        "writing_ready": status == "ready",
        "weighted_attestations": args.weighted_attestations,
        "period": args.period,
        "corridor": args.corridor,
        "target_records": args.target_records,
        "total_records": n_records,
        "records_needed": needed,
        "effective_n": round(n_eff, 2),
        "trend_slope": slope,
        "trend_p_value": p_value,
        "ci_width": ci_width,
        "ci_low": ci[0] if ci else None,
        "ci_high": ci[1] if ci else None,
        "stability": stability,
        "source_distribution": dict(buckets),
        "authority_distribution": dict(authority),
        "tourism_ratio": tourism_ratio,
        "max_tourism_ratio": args.max_tourism_ratio,
        "recommendation": recommendation,
    }

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_json).open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)

    md = f"""# Writing Readiness Assessment

**Date**: {date.today().isoformat()}  
**Weighted attestations file**: {args.weighted_attestations}  
**Status**: {status}

## Corpus Status
- {args.corridor} {args.period} records: **{n_records}** / {args.target_records}
- Records still needed: **{needed}**
- Effective n: **{n_eff:.2f}**

## Trend Detection
- Slope: {slope if slope is not None else 'N/A'}
- p-value: {p_value if p_value is not None else 'N/A'}
- CI width: {ci_width if ci_width is not None else 'N/A'}
- Stability: {stability}

## Source Balance
- Source distribution: {dict(buckets)}
- Authority distribution: {dict(authority)}
- Tourism-retrospective ratio: {tourism_ratio:.1%} (target <= {args.max_tourism_ratio:.0%})

## Final Recommendation
{recommendation}
"""
    with Path(args.out_md).open("w", encoding="utf-8") as handle:
        handle.write(md)

    print(f"{status.upper()}: {recommendation}")
    print(f"Reports written to {args.out_json} and {args.out_md}")


if __name__ == "__main__":
    main()
