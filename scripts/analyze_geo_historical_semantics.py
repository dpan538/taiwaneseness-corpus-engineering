#!/usr/bin/env python3
"""Aggregate scored historical attestations by period and corridor."""

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


def summarize(rows: list[dict], keys: list[str]) -> list[dict]:
    groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(key, "") for key in keys)].append(row)

    output: list[dict] = []
    for key_values, group in groups.items():
        out = {key: value for key, value in zip(keys, key_values)}
        out["attestation_count"] = str(len(group))
        out["binding_rate"] = f"{sum(as_float(r.get('binding_present', '0')) for r in group) / len(group):.6f}"
        for domain in DOMAINS:
            out[f"mean_{domain}_score"] = f"{sum(as_float(r.get(f'{domain}_score', '0')) for r in group) / len(group):.6f}"
        output.append(out)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scored-attestations",
        default="data/processed/historical_geo_attestations_scored.csv",
    )
    parser.add_argument("--output-dir", default="outputs/geo_historical")
    args = parser.parse_args()

    rows = read_csv(Path(args.scored_attestations))
    output_dir = Path(args.output_dir)

    period_rows = summarize(rows, ["period"])
    period_corridor_rows = summarize(rows, ["period", "corridor"])
    brand_period_rows = summarize(rows, ["brand_or_category", "period"])

    summary_fields = ["period", "attestation_count", "binding_rate"] + [
        f"mean_{domain}_score" for domain in DOMAINS
    ]
    write_csv(output_dir / "period_semantic_summary.csv", period_rows, summary_fields)

    corridor_fields = ["period", "corridor", "attestation_count", "binding_rate"] + [
        f"mean_{domain}_score" for domain in DOMAINS
    ]
    write_csv(
        output_dir / "period_corridor_semantic_summary.csv",
        period_corridor_rows,
        corridor_fields,
    )

    brand_fields = ["brand_or_category", "period", "attestation_count", "binding_rate"] + [
        f"mean_{domain}_score" for domain in DOMAINS
    ]
    write_csv(output_dir / "brand_period_semantic_summary.csv", brand_period_rows, brand_fields)


if __name__ == "__main__":
    main()
