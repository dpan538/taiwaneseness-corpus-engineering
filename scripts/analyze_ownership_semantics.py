#!/usr/bin/env python3
"""Join semantic attestations with ownership categories and summarize."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


DOMAINS = [
    "geographic",
    "nostalgia",
    "night_market",
    "authenticity",
    "platform_fast_food",
]


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scored-attestations",
        default="data/processed/historical_geo_attestations_scored.csv",
    )
    parser.add_argument("--ownership", default="data/ownership_capital_seed.csv")
    parser.add_argument("--output-dir", default="outputs/ownership")
    args = parser.parse_args()

    attestations = read_csv(Path(args.scored_attestations))
    ownership_rows = read_csv(Path(args.ownership))

    ownership_by_brand: dict[str, dict] = {}
    for row in ownership_rows:
        brand = row.get("brand", "")
        if brand and brand not in ownership_by_brand:
            ownership_by_brand[brand] = row

    joined: list[dict] = []
    for row in attestations:
        brand = row.get("brand_or_category", "")
        ownership = ownership_by_brand.get(brand, {})
        out = dict(row)
        out["ownership_category"] = ownership.get("ownership_category", "unknown")
        out["capital_origin"] = ownership.get("capital_origin", "unknown")
        out["founding_place"] = ownership.get("founding_place", "")
        out["mainland_entry_year"] = ownership.get("mainland_entry_year", "")
        joined.append(out)

    output_dir = Path(args.output_dir)
    joined_fields = list(joined[0].keys()) if joined else []
    write_csv(output_dir / "historical_attestations_with_ownership.csv", joined, joined_fields)

    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in joined:
        groups[
            (
                row.get("period", ""),
                row.get("corridor", ""),
                row.get("ownership_category", ""),
            )
        ].append(row)

    summary: list[dict] = []
    for (period, corridor, ownership_category), group in groups.items():
        out = {
            "period": period,
            "corridor": corridor,
            "ownership_category": ownership_category,
            "attestation_count": str(len(group)),
            "binding_rate": f"{sum(as_float(r.get('binding_present', '0')) for r in group) / len(group):.6f}",
        }
        for domain in DOMAINS:
            out[f"mean_{domain}_score"] = f"{sum(as_float(r.get(f'{domain}_score', '0')) for r in group) / len(group):.6f}"
        summary.append(out)

    fields = [
        "period",
        "corridor",
        "ownership_category",
        "attestation_count",
        "binding_rate",
    ] + [f"mean_{domain}_score" for domain in DOMAINS]
    write_csv(output_dir / "period_corridor_ownership_summary.csv", summary, fields)


if __name__ == "__main__":
    main()
