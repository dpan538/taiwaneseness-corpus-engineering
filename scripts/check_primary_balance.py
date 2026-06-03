#!/usr/bin/env python3
"""
scripts/check_primary_balance.py

Quick progress check for Taiwan-side primary records in the weighted corpus.
Uses only the standard library.
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
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


def binding_value(row):
    if row.get("historical_binding_raw"):
        return parse_float(row.get("historical_binding_raw"), 0.0)
    weight = parse_float(row.get("analysis_weight"), 0.0)
    weighted = parse_float(row.get("weighted_historical_binding"), 0.0)
    if weight > 0 and weighted <= weight:
        return weighted / weight
    return weighted


def slope(points):
    if len(points) < 3:
        return 0.0
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in points)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    return numerator / denominator if denominator else 0.0


def permutation_p_value(points, iterations):
    observed = slope(points)
    if abs(observed) < 1e-12 or len(points) < 5:
        return 1.0
    years = [point[0] for point in points]
    bindings = [point[1] for point in points]
    extreme = 0
    for _ in range(iterations):
        shuffled = list(bindings)
        random.shuffle(shuffled)
        permuted = list(zip(years, shuffled))
        if abs(slope(permuted)) >= abs(observed):
            extreme += 1
    return extreme / iterations if iterations else 1.0


def main():
    parser = argparse.ArgumentParser(description="Check primary source balance and quick trend status.")
    parser.add_argument("--weighted-csv", required=True)
    parser.add_argument("--period", default="1946-1987_taiwan_side_formation")
    parser.add_argument("--corridor", default="Taiwan-side")
    parser.add_argument("--permutations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260604)
    args = parser.parse_args()

    random.seed(args.seed)
    total = 0
    primary_points = []
    authority_counts = Counter()
    source_counts = Counter()

    with Path(args.weighted_csv).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            level = (row.get("verification_level") or "").strip().lower()
            if level not in {"verified", "probable"}:
                continue
            if (row.get("corridor") or "").strip() != args.corridor:
                continue
            if not period_matches(row.get("period"), args.period):
                continue
            year = parse_year(row.get("year"))
            if year is None:
                continue
            total += 1
            authority = (row.get("authority_level") or "missing").strip().lower()
            authority_counts[authority] += 1
            source_counts[row.get("source_type") or "missing"] += 1
            if authority == "primary":
                primary_points.append((year, binding_value(row)))

    primary_count = len(primary_points)
    primary_ratio = primary_count / total if total else 0.0
    p_value = permutation_p_value(primary_points, args.permutations) if primary_count >= 20 else None

    print(f"{args.corridor} {args.period} total records: {total}")
    print(f"Primary records: {primary_count} ({primary_ratio:.1%})")
    print(f"Authority distribution: {dict(authority_counts)}")
    print(f"Top source types: {source_counts.most_common(8)}")
    if p_value is None:
        print("Primary-only quick trend: insufficient primary records (need at least 20).")
    else:
        print(f"Primary-only quick trend p-value: {p_value:.3f}")


if __name__ == "__main__":
    main()
