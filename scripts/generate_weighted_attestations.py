#!/usr/bin/env python3
"""
scripts/generate_weighted_attestations.py

Generate per-row v2 analysis weights for downstream diagnostics.

Input must include novelty_score and authority_level columns. The output keeps
all original columns and adds:
- analysis_weight
- historical_binding_raw
- weighted_historical_binding

The weighted_historical_binding column is the row contribution:
historical_binding_raw * analysis_weight.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


AUTHORITY_WEIGHTS = {
    "primary": 1.2,
    "secondary": 0.7,
    "tertiary": 0.2,
}


def parse_float(value, default=0.5):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def marker_present(row, *fields):
    return any((row.get(field) or "").strip() for field in fields)


def row_raw_binding(row):
    dish = marker_present(row, "dish_marker", "dish_markers", "matched_dish_markers")
    taiwan = marker_present(row, "taiwan_marker", "taiwan_markers", "matched_taiwan_markers")
    return 1.0 if dish and taiwan else 0.0


def analysis_weight(row):
    novelty = max(0.0, min(1.0, parse_float(row.get("novelty_score"), 0.5)))
    authority_level = (row.get("authority_level") or "secondary").strip().lower()
    authority = AUTHORITY_WEIGHTS.get(authority_level, 0.3)
    return (0.7 * novelty) + (0.3 * authority)


def main():
    parser = argparse.ArgumentParser(description="Generate per-row v2 weighted attestations.")
    parser.add_argument("--input", required=True, help="CSV with novelty_score and authority_level")
    parser.add_argument("--output", required=True, help="Output CSV")
    args = parser.parse_args()

    with Path(args.input).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)

    if not fields:
        raise SystemExit(f"No CSV header found in {args.input}")
    for required in ("novelty_score", "authority_level"):
        if required not in fields:
            raise SystemExit(f"Missing required column: {required}")

    out_fields = list(fields)
    for field in ("analysis_weight", "historical_binding_raw", "weighted_historical_binding"):
        if field not in out_fields:
            out_fields.append(field)

    for row in rows:
        weight = analysis_weight(row)
        raw_binding = row_raw_binding(row)
        row["analysis_weight"] = f"{weight:.4f}"
        row["historical_binding_raw"] = f"{raw_binding:.4f}"
        row["weighted_historical_binding"] = f"{raw_binding * weight:.4f}"

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} weighted rows: {args.output}")


if __name__ == "__main__":
    main()
