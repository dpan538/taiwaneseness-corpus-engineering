#!/usr/bin/env python3
"""
scripts/estimate_primary_needed.py

Estimate how many primary Taiwan-side records may be needed to detect a
positive trend under simple simulation assumptions.

The input can be either a primary-only CSV or a full weighted attestation CSV;
by default the script filters to Taiwan-side / 1946-1987 / primary records.
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def parse_year(value):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def parse_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def period_matches(value, period):
    value = value or ""
    return value == period or period in value or value in period


def row_binding(row):
    if row.get("historical_binding_raw"):
        return parse_float(row.get("historical_binding_raw"), 0.0)
    weight = parse_float(row.get("analysis_weight"), 0.0)
    weighted = parse_float(row.get("weighted_historical_binding"), 0.0)
    if weight > 0 and weighted <= weight:
        return weighted / weight
    return weighted


def load_current(path, period, corridor, primary_only):
    rows = []
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if primary_only and (row.get("authority_level") or "").strip().lower() != "primary":
                continue
            if corridor and (row.get("corridor") or "").strip() != corridor:
                continue
            if period and not period_matches(row.get("period"), period):
                continue
            year = parse_year(row.get("year"))
            if year is None:
                continue
            rows.append((year, max(0.0, min(1.0, row_binding(row)))))
    return rows


def slope(years, bindings):
    if len(years) < 3:
        return 0.0
    x_mean = sum(years) / len(years)
    y_mean = sum(bindings) / len(bindings)
    numerator = sum((year - x_mean) * (binding - y_mean) for year, binding in zip(years, bindings))
    denominator = sum((year - x_mean) ** 2 for year in years)
    return numerator / denominator if denominator else 0.0


def permutation_p_value(years, bindings, iterations):
    observed = slope(years, bindings)
    if abs(observed) < 1e-12:
        return 1.0
    extreme = 0
    for _ in range(iterations):
        shuffled = list(bindings)
        random.shuffle(shuffled)
        if abs(slope(years, shuffled)) >= abs(observed):
            extreme += 1
    return extreme / iterations if iterations else 1.0


def simulate_success_rate(current, additional_count, effect, noise, simulations, permutation_iterations):
    successes = 0
    base_years = [item[0] for item in current]
    base_bindings = [item[1] for item in current]
    for _ in range(simulations):
        new_years = [random.randint(1970, 1987) for _ in range(additional_count)]
        new_bindings = [max(0.0, min(1.0, random.gauss(effect, noise))) for _ in range(additional_count)]
        p_value = permutation_p_value(base_years + new_years, base_bindings + new_bindings, permutation_iterations)
        if p_value < 0.10:
            successes += 1
    return successes / simulations if simulations else 0.0


def main():
    parser = argparse.ArgumentParser(description="Estimate additional primary records needed.")
    parser.add_argument("--weighted-csv", "--current-primary", dest="weighted_csv", required=True)
    parser.add_argument("--period", default="1946-1987_taiwan_side_formation")
    parser.add_argument("--corridor", default="Taiwan-side")
    parser.add_argument("--include-non-primary", action="store_true")
    parser.add_argument("--additional", type=int, default=50)
    parser.add_argument("--effect", type=float, default=0.7)
    parser.add_argument("--noise", type=float, default=0.2)
    parser.add_argument("--simulations", type=int, default=200)
    parser.add_argument("--permutations", type=int, default=100)
    parser.add_argument("--target-success", type=float, default=0.80)
    parser.add_argument("--max-additional", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260604)
    args = parser.parse_args()

    random.seed(args.seed)
    current = load_current(args.weighted_csv, args.period, args.corridor, not args.include_non_primary)
    if len(current) < 3:
        print(f"Only {len(current)} matching current records; adding weak synthetic anchors for simulation stability.")
        current = current + [(1975, 0.2), (1980, 0.3), (1985, 0.4)]

    success = simulate_success_rate(
        current,
        args.additional,
        args.effect,
        args.noise,
        args.simulations,
        args.permutations,
    )
    print(f"Current matching records: {len(current)}")
    print(f"With +{args.additional} new primaries, effect={args.effect}, noise={args.noise}: p<0.10 success={success:.1%}")

    needed = args.additional
    while success < args.target_success and needed < args.max_additional:
        needed += 10
        success = simulate_success_rate(
            current,
            needed,
            args.effect,
            args.noise,
            args.simulations,
            args.permutations,
        )
    if success >= args.target_success:
        print(f"Estimated additional primaries for {args.target_success:.0%} success: {needed}")
    else:
        print(f"Even +{args.max_additional} primaries did not reach {args.target_success:.0%} success under this simulation.")


if __name__ == "__main__":
    main()
