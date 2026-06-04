#!/usr/bin/env python3
"""Create a balanced positive/negative binding time series by year bin."""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path


def parse_float(value: str | None, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except ValueError:
        return default


def parse_year(value: str | None) -> int | None:
    try:
        return int(float(value or ""))
    except ValueError:
        return None


def period_matches(value: str, requested: str) -> bool:
    if not requested:
        return True
    value = value or ""
    return value == requested or requested in value or value in requested


def raw_binding(row: dict[str, str]) -> float:
    if row.get("historical_binding_raw"):
        return parse_float(row.get("historical_binding_raw"), 0.0)
    weight = parse_float(row.get("analysis_weight"), 1.0)
    weighted = parse_float(row.get("weighted_historical_binding"), 0.0)
    if weight > 0 and weighted <= weight:
        return weighted / weight
    return weighted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Balance positive/negative binding rows by time bin.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--period", default="1946-1987_taiwan_side_formation")
    parser.add_argument("--corridor", default="Taiwan-side")
    parser.add_argument("--bin-years", type=int, default=5)
    parser.add_argument("--target-ratio", type=float, default=1.0, help="Desired negative/positive ratio.")
    parser.add_argument("--positive-threshold", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20260604)
    parser.add_argument("--out-csv", default="reports/balanced_binding_by_year.csv")
    parser.add_argument("--out-rows", default="", help="Optional sampled row output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    groups: dict[int, dict[str, list[dict[str, str]]]] = defaultdict(lambda: {"pos": [], "neg": []})
    with Path(args.attestations).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        for row in reader:
            if args.corridor and (row.get("corridor") or "").strip() != args.corridor:
                continue
            if args.period and not period_matches(row.get("period", ""), args.period):
                continue
            year = parse_year(row.get("year"))
            if year is None:
                continue
            binding = raw_binding(row)
            bin_key = (year // args.bin_years) * args.bin_years
            row = dict(row)
            row["_balanced_bin"] = str(bin_key)
            row["_binding_raw_for_balance"] = f"{binding:.4f}"
            if binding > args.positive_threshold:
                groups[bin_key]["pos"].append(row)
            else:
                groups[bin_key]["neg"].append(row)

    sampled_rows: list[dict[str, str]] = []
    summary_rows: list[dict[str, str]] = []
    for bin_key in sorted(groups):
        pos = groups[bin_key]["pos"]
        neg = groups[bin_key]["neg"]
        target_neg = min(len(neg), int(round(len(pos) * args.target_ratio)))
        selected_neg = random.sample(neg, target_neg) if target_neg else []
        selected = pos + selected_neg
        sampled_rows.extend(selected)

        weight_sum = 0.0
        binding_sum = 0.0
        for row in selected:
            weight = parse_float(row.get("analysis_weight"), 1.0)
            binding = parse_float(row.get("_binding_raw_for_balance"), 0.0)
            weight_sum += weight
            binding_sum += binding * weight
        balanced_index = binding_sum / weight_sum if weight_sum else 0.0
        summary_rows.append(
            {
                "year_bin": str(bin_key),
                "bin_midpoint": f"{bin_key + args.bin_years / 2:.1f}",
                "positive_rows": str(len(pos)),
                "negative_rows_available": str(len(neg)),
                "negative_rows_sampled": str(len(selected_neg)),
                "sampled_rows": str(len(selected)),
                "balanced_binding_index": f"{balanced_index:.6f}",
                "weight_sum": f"{weight_sum:.4f}",
                "bin_usable_for_balanced_trend": "1" if pos and selected_neg else "0",
            }
        )

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as handle:
        out_fields = [
            "year_bin",
            "bin_midpoint",
            "positive_rows",
            "negative_rows_available",
            "negative_rows_sampled",
            "sampled_rows",
            "balanced_binding_index",
            "weight_sum",
            "bin_usable_for_balanced_trend",
        ]
        writer = csv.DictWriter(handle, fieldnames=out_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    if args.out_rows:
        out_fields = list(fields)
        for field in ("_balanced_bin", "_binding_raw_for_balance"):
            if field not in out_fields:
                out_fields.append(field)
        Path(args.out_rows).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.out_rows).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=out_fields, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            writer.writerows(sampled_rows)

    usable_bins = sum(1 for row in summary_rows if row["bin_usable_for_balanced_trend"] == "1")
    print(f"Balanced binding summary saved to {args.out_csv}")
    print(f"Usable balanced bins: {usable_bins}/{len(summary_rows)}")
    if usable_bins == 0:
        print("No bins contain both positive and negative rows; add reviewed weak/no-binding controls.")


if __name__ == "__main__":
    main()
