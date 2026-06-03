#!/usr/bin/env python3
"""Aggregate brand-city presence into spatial diffusion summaries."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def as_int(value: str) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(float(value))
    except ValueError:
        return 0


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--presence", default="data/brand_city_presence_seed.csv")
    parser.add_argument("--city-metadata", default="data/city_metadata.csv")
    parser.add_argument("--output-dir", default="outputs/spatial")
    parser.add_argument(
        "--city-only",
        action="store_true",
        help="Exclude province/national rows from city and corridor summaries",
    )
    parser.add_argument(
        "--status-basis",
        default="",
        help="Optional comma-separated status_basis filter, e.g. official_store_locator",
    )
    args = parser.parse_args()

    presence_rows = read_csv(Path(args.presence))
    status_basis_filter = {
        value.strip()
        for value in args.status_basis.split(",")
        if value.strip()
    }
    if status_basis_filter:
        presence_rows = [
            row
            for row in presence_rows
            if row.get("status_basis", "") in status_basis_filter
        ]
    city_rows = read_csv(Path(args.city_metadata))
    city_meta = {row["city"]: row for row in city_rows}

    enriched: list[dict] = []
    for row in presence_rows:
        if args.city_only and row.get("area_level") != "city":
            continue
        meta = city_meta.get(row.get("city", ""), {})
        open_count = as_int(row.get("open_store_count", "0"))
        planned_count = as_int(row.get("planned_store_count", "0"))
        total_count = open_count + planned_count
        enriched_row = dict(row)
        enriched_row.update(
            {
                "macro_region": meta.get("macro_region", ""),
                "corridor": meta.get("corridor", ""),
                "coastal_status": meta.get("coastal_status", ""),
                "latitude": meta.get("latitude", ""),
                "longitude": meta.get("longitude", ""),
                "total_store_count": str(total_count),
                "has_open_presence": "1" if open_count > 0 else "0",
                "has_planned_presence": "1" if planned_count > 0 else "0",
            }
        )
        enriched.append(enriched_row)

    city_fields = [
        "record_id",
        "brand",
        "category",
        "city",
        "province",
        "area_level",
        "observation_date",
        "first_observed_year",
        "open_store_count",
        "planned_store_count",
        "total_store_count",
        "has_open_presence",
        "has_planned_presence",
        "macro_region",
        "corridor",
        "coastal_status",
        "latitude",
        "longitude",
        "status_basis",
        "source_type",
        "source_url",
        "confidence",
        "notes",
    ]

    output_dir = Path(args.output_dir)
    write_csv(output_dir / "city_presence_enriched.csv", enriched, city_fields)

    corridor_groups: dict[tuple[str, str, str], dict] = defaultdict(
        lambda: {
            "brand": "",
            "first_observed_year": "",
            "corridor": "",
            "city_records": 0,
            "open_store_count": 0,
            "planned_store_count": 0,
            "total_store_count": 0,
            "open_presence_cities": 0,
            "planned_presence_cities": 0,
        }
    )
    coastal_groups: dict[tuple[str, str, str], dict] = defaultdict(
        lambda: {
            "brand": "",
            "first_observed_year": "",
            "coastal_status": "",
            "city_records": 0,
            "open_store_count": 0,
            "planned_store_count": 0,
            "total_store_count": 0,
        }
    )

    for row in enriched:
        brand = row.get("brand", "")
        year = row.get("first_observed_year", "")
        corridor = row.get("corridor", "") or "Unknown"
        coastal_status = row.get("coastal_status", "") or "Unknown"
        open_count = as_int(row.get("open_store_count", "0"))
        planned_count = as_int(row.get("planned_store_count", "0"))
        total_count = open_count + planned_count

        key = (brand, year, corridor)
        group = corridor_groups[key]
        group["brand"] = brand
        group["first_observed_year"] = year
        group["corridor"] = corridor
        group["city_records"] += 1
        group["open_store_count"] += open_count
        group["planned_store_count"] += planned_count
        group["total_store_count"] += total_count
        group["open_presence_cities"] += 1 if open_count > 0 else 0
        group["planned_presence_cities"] += 1 if planned_count > 0 else 0

        coastal_key = (brand, year, coastal_status)
        coastal_group = coastal_groups[coastal_key]
        coastal_group["brand"] = brand
        coastal_group["first_observed_year"] = year
        coastal_group["coastal_status"] = coastal_status
        coastal_group["city_records"] += 1
        coastal_group["open_store_count"] += open_count
        coastal_group["planned_store_count"] += planned_count
        coastal_group["total_store_count"] += total_count

    corridor_rows = list(corridor_groups.values())
    total_by_brand_year: dict[tuple[str, str], int] = defaultdict(int)
    for row in corridor_rows:
        total_by_brand_year[(row["brand"], row["first_observed_year"])] += row[
            "total_store_count"
        ]
    for row in corridor_rows:
        denominator = total_by_brand_year[(row["brand"], row["first_observed_year"])]
        row["corridor_share"] = f"{(row['total_store_count'] / denominator) if denominator else 0:.6f}"

    corridor_fields = [
        "brand",
        "first_observed_year",
        "corridor",
        "city_records",
        "open_presence_cities",
        "planned_presence_cities",
        "open_store_count",
        "planned_store_count",
        "total_store_count",
        "corridor_share",
    ]
    write_csv(output_dir / "corridor_summary.csv", corridor_rows, corridor_fields)

    coastal_rows = list(coastal_groups.values())
    total_by_brand_year_coastal: dict[tuple[str, str], int] = defaultdict(int)
    for row in coastal_rows:
        total_by_brand_year_coastal[(row["brand"], row["first_observed_year"])] += row[
            "total_store_count"
        ]
    for row in coastal_rows:
        denominator = total_by_brand_year_coastal[
            (row["brand"], row["first_observed_year"])
        ]
        row["coastal_status_share"] = f"{(row['total_store_count'] / denominator) if denominator else 0:.6f}"

    coastal_fields = [
        "brand",
        "first_observed_year",
        "coastal_status",
        "city_records",
        "open_store_count",
        "planned_store_count",
        "total_store_count",
        "coastal_status_share",
    ]
    write_csv(output_dir / "coastal_status_summary.csv", coastal_rows, coastal_fields)


if __name__ == "__main__":
    main()
