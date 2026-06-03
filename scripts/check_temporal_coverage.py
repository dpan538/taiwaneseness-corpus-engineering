#!/usr/bin/env python3
"""Check whether a corpus period has year-level holes or spikes."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check temporal coverage for an attestation period.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--period", default="1946-1987")
    parser.add_argument("--bin-years", type=int, default=5)
    parser.add_argument("--out-csv", default="reports/temporal_gaps.csv")
    return parser.parse_args()


def read_rows(path: str) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_year(value: str) -> int | None:
    try:
        return int(float((value or "").strip()))
    except ValueError:
        return None


def parse_period_range(period: str) -> tuple[int, int] | None:
    if "-" not in period:
        return None
    left, right = period.split("-", 1)
    try:
        return int(left[:4]), int(right[:4])
    except ValueError:
        return None


def period_matches(row: dict, requested: str, period_range: tuple[int, int] | None) -> bool:
    row_period = (row.get("period") or "").strip()
    if requested == row_period or requested in row_period:
        return True
    if period_range is None:
        return False
    year = parse_year(row.get("year", ""))
    return year is not None and period_range[0] <= year <= period_range[1]


def main() -> None:
    args = parse_args()
    rows = read_rows(args.attestations)
    period_range = parse_period_range(args.period)

    years = [
        parse_year(row.get("year", ""))
        for row in rows
        if period_matches(row, args.period, period_range)
    ]
    years = [year for year in years if year is not None]
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)

    if not years:
        with Path(args.out_csv).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["year", "status", "count", "bin_start", "bin_end", "bin_count"])
            writer.writeheader()
        print(f"No records for period {args.period}. Output: {args.out_csv}")
        return

    counts = Counter(years)
    min_year = min(years)
    max_year = max(years)
    if period_range is not None:
        min_year, max_year = period_range

    rows_out = []
    for year in range(min_year, max_year + 1):
        count = counts.get(year, 0)
        bin_start = min_year + ((year - min_year) // args.bin_years) * args.bin_years
        bin_end = min(bin_start + args.bin_years - 1, max_year)
        bin_count = sum(counts.get(y, 0) for y in range(bin_start, bin_end + 1))
        rows_out.append(
            {
                "year": str(year),
                "status": "present" if count else "missing",
                "count": str(count),
                "bin_start": str(bin_start),
                "bin_end": str(bin_end),
                "bin_count": str(bin_count),
            }
        )

    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["year", "status", "count", "bin_start", "bin_end", "bin_count"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows_out)

    missing = sum(1 for row in rows_out if row["status"] == "missing")
    print(
        f"Temporal coverage for {args.period}: years {min_year}-{max_year}, "
        f"total {len(years)} records, {missing} missing years. Output: {args.out_csv}"
    )


if __name__ == "__main__":
    main()
