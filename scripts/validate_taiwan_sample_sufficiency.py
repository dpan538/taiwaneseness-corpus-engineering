#!/usr/bin/env python3
"""
scripts/validate_taiwan_sample_sufficiency.py

Bootstrap the Taiwan-side 1946-1987 records to estimate whether the trend
slope is stable enough, and how much larger the sample likely needs to be.

This is a planning diagnostic, not a final inference model. It supports frozen
corpus files that may not yet contain per-row analysis_weight or
weighted_historical_binding columns.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from statistics import mean, stdev


USABLE_LEVELS = {"verified", "probable"}


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


def period_matches(value, period):
    if not period:
        return True
    value = value or ""
    return value == period or period in value or value in period


def fallback_binding(row):
    dish = (row.get("dish_marker") or row.get("dish_markers") or "").strip()
    taiwan = (row.get("taiwan_marker") or row.get("taiwan_markers") or "").strip()
    if row.get("weighted_historical_binding"):
        return max(0.0, min(1.0, parse_float(row.get("weighted_historical_binding"), 0.0)))
    brand = (row.get("brand_or_category") or "").lower()
    owner = (row.get("ownership_category") or row.get("capital_origin") or "").lower()
    lexical = 1.0 if dish and taiwan else 0.0
    branding = 1.0 if taiwan or "taiwan" in brand or "台湾" in brand or "台灣" in brand else 0.0
    ownership = 1.0 if "taiwan" in owner or "台湾" in owner or "台灣" in owner else 0.0
    return max(0.0, min(1.0, (0.5 * lexical) + (0.25 * branding) + (0.25 * ownership)))


def fallback_weight(row):
    if row.get("analysis_weight"):
        return max(0.0, parse_float(row.get("analysis_weight"), 1.0))
    return 1.0


def load_records(path, period, corridor):
    all_usable_period = 0
    data = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        signal_mode = (
            "explicit_weighted"
            if {"weighted_historical_binding", "analysis_weight"}.issubset(fieldnames)
            else "fallback_lexical"
        )
        for row in reader:
            level = (row.get("verification_level") or "").strip().lower()
            if level and level not in USABLE_LEVELS:
                continue
            if not period_matches(row.get("period"), period):
                continue
            year = parse_year(row.get("year"))
            if year is None:
                continue
            all_usable_period += 1
            if corridor and (row.get("corridor") or "").strip() != corridor:
                continue
            data.append((year, fallback_binding(row), fallback_weight(row)))
    return data, all_usable_period, signal_mode


def weighted_slope(sample):
    if len(sample) < 3:
        return 0.0
    weights = [item[2] for item in sample]
    total_weight = sum(weights)
    if total_weight <= 0:
        return 0.0
    x_mean = sum(year * weight for year, _, weight in sample) / total_weight
    y_mean = sum(binding * weight for _, binding, weight in sample) / total_weight
    cov = sum(weight * (year - x_mean) * (binding - y_mean) for year, binding, weight in sample)
    var_x = sum(weight * (year - x_mean) ** 2 for year, _, weight in sample)
    return cov / var_x if var_x else 0.0


def bootstrap_slope_distribution(data, sample_size, iterations):
    if not data:
        return []
    slopes = []
    for _ in range(iterations):
        sample = random.choices(data, k=sample_size)
        slopes.append(weighted_slope(sample))
    return slopes


def percentile(sorted_values, q):
    if not sorted_values:
        return None
    idx = max(0, min(len(sorted_values) - 1, int(q * (len(sorted_values) - 1))))
    return sorted_values[idx]


def main():
    parser = argparse.ArgumentParser(description="Validate Taiwan-side trend sample sufficiency.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--period", default="1946-1987_taiwan_side_formation")
    parser.add_argument("--corridor", default="Taiwan-side")
    parser.add_argument("--max-sample", type=int, default=800)
    parser.add_argument("--step", type=int, default=50)
    parser.add_argument("--target-se", type=float, default=0.0005)
    parser.add_argument("--bootstrap-iterations", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20260604)
    parser.add_argument("--out-csv", default="reports/taiwan_sample_sufficiency.csv")
    args = parser.parse_args()

    random.seed(args.seed)
    data, all_usable_period, signal_mode = load_records(args.attestations, args.period, args.corridor)
    if not data:
        print(f"No {args.corridor} usable records found for {args.period}.", file=sys.stderr)
        sys.exit(1)

    current_n = len(data)
    observed = weighted_slope(data)
    start = min(args.step, current_n)
    candidates = list(range(start, args.max_sample + 1, args.step))
    if current_n not in candidates:
        candidates.append(current_n)
    candidates = sorted(set(candidates))

    rows = []
    for sample_size in candidates:
        slopes = bootstrap_slope_distribution(data, sample_size, args.bootstrap_iterations)
        if len(slopes) < 2:
            se = 0.0
            ci_low = slopes[0] if slopes else 0.0
            ci_high = ci_low
        else:
            slopes_sorted = sorted(slopes)
            se = stdev(slopes)
            ci_low = percentile(slopes_sorted, 0.025)
            ci_high = percentile(slopes_sorted, 0.975)
        rows.append(
            {
                "sample_size": sample_size,
                "slope_se": se,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )

    needed = None
    for row in rows:
        if row["slope_se"] <= args.target_se:
            needed = row["sample_size"]
            break

    with open(args.out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_size", "slope_se", "ci_low", "ci_high"])
        writer.writeheader()
        writer.writerows(rows)

    slope_values = [row["slope_se"] for row in rows]
    binding_values = [item[1] for item in data]
    print(f"Signal mode: {signal_mode}")
    print(f"Usable records in period, all corridors: {all_usable_period}")
    print(f"Current {args.corridor} usable records: {current_n}")
    print(f"Observed weighted slope: {observed:.8f}")
    print(f"Binding variance proxy (stdev): {stdev(binding_values) if len(binding_values) > 1 else 0.0:.8f}")
    print(f"Mean bootstrapped slope SE: {mean(slope_values):.8f}")
    print(f"Results written to {args.out_csv}")
    if needed is None:
        print(
            f"Even at n={current_n}, slope SE remains above target {args.target_se}. "
            "Collect more records or relax the target."
        )
    elif needed <= current_n:
        print(f"Target slope SE <={args.target_se} is reachable within current sample at n={needed}.")
    else:
        print(f"Need at least n={needed}; add about {needed - current_n} {args.corridor} records.")


if __name__ == "__main__":
    main()
