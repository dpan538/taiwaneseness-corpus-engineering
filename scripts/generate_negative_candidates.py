#!/usr/bin/env python3
"""Generate weak-binding / no-binding candidate rows from an attestation CSV.

The goal is not to fabricate negatives. It surfaces rows that already have
partial evidence:
- dish_only: dish_marker exists, taiwan_marker is blank
- taiwan_only: taiwan_marker exists, dish_marker is blank

These rows should be manually reviewed before being treated as analytical
controls.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def nonempty(row: dict[str, str], *fields: str) -> bool:
    return any((row.get(field) or "").strip() for field in fields)


def period_matches(value: str, requested: str) -> bool:
    if not requested:
        return True
    value = value or ""
    return value == requested or requested in value or value in requested


def year_value(row: dict[str, str]) -> int:
    try:
        return int(float((row.get("year") or "").strip()))
    except ValueError:
        return 9999


def source_ref(row: dict[str, str]) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or ""
    ).strip()


def candidate_type(row: dict[str, str]) -> str:
    dish = nonempty(row, "dish_marker", "dish_markers", "matched_dish_markers")
    taiwan = nonempty(row, "taiwan_marker", "taiwan_markers", "matched_taiwan_markers")
    if dish and not taiwan:
        return "dish_only"
    if taiwan and not dish:
        return "taiwan_only"
    return ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate weak/no-binding candidates from existing rows.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--period", default="", help="Optional period filter.")
    parser.add_argument("--corridor", default="", help="Optional corridor filter.")
    parser.add_argument("--max-negatives", type=int, default=200)
    parser.add_argument("--out-csv", default="working/negative_candidates.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.attestations).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)

    filtered: list[dict[str, str]] = []
    for row in rows:
        if args.corridor and (row.get("corridor") or "").strip() != args.corridor:
            continue
        if args.period and not period_matches(row.get("period", ""), args.period):
            continue
        ctype = candidate_type(row)
        if not ctype:
            continue
        item = dict(row)
        item["negative_type"] = ctype
        item["historical_binding_raw"] = "0.0000"
        item["weighted_historical_binding"] = "0.0000"
        filtered.append(item)

    filtered.sort(key=lambda row: (year_value(row), row.get("negative_type", ""), source_ref(row)))

    half = args.max_negatives // 2
    dish_only = [row for row in filtered if row["negative_type"] == "dish_only"][:half]
    taiwan_only = [row for row in filtered if row["negative_type"] == "taiwan_only"][: args.max_negatives - len(dish_only)]
    candidates = dish_only + taiwan_only

    seen: set[tuple[str, str, str, str]] = set()
    unique: list[dict[str, str]] = []
    for row in candidates:
        key = (
            source_ref(row).lower().rstrip("/"),
            (row.get("year") or "").strip(),
            (row.get("dish_marker") or "").strip(),
            (row.get("taiwan_marker") or "").strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)

    out_fields = list(fields)
    for field in ("negative_type", "historical_binding_raw", "weighted_historical_binding"):
        if field not in out_fields:
            out_fields.append(field)

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(unique)

    counts = {
        "dish_only": sum(1 for row in unique if row["negative_type"] == "dish_only"),
        "taiwan_only": sum(1 for row in unique if row["negative_type"] == "taiwan_only"),
    }
    print(f"Generated {len(unique)} negative candidates: {args.out_csv}")
    print(f"Counts: {counts}")
    print("Manual review is still required before merging these controls into the analytical corpus.")


if __name__ == "__main__":
    main()
