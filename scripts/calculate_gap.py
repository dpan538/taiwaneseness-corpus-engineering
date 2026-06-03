#!/usr/bin/env python3
"""Calculate Consumer Reinterpretation Gap by merchant and domain."""

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


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merchants", required=True, help="Scored merchant CSV")
    parser.add_argument("--reviews", required=True, help="Scored review CSV")
    parser.add_argument("--output", required=True, help="Output gap CSV")
    args = parser.parse_args()

    merchants = read_rows(Path(args.merchants))
    reviews = read_rows(Path(args.reviews))

    review_groups: dict[str, list[dict]] = defaultdict(list)
    for row in reviews:
        review_groups[row.get("merchant_id", "")].append(row)

    fieldnames = [
        "merchant_id",
        "city",
        "shop_name",
        "review_count",
        "binding_present",
    ]
    for domain in DOMAINS:
        fieldnames.extend(
            [
                f"merchant_{domain}_score",
                f"consumer_{domain}_mean_score",
                f"gap_{domain}",
            ]
        )

    output_rows: list[dict] = []
    for merchant in merchants:
        merchant_id = merchant.get("merchant_id", "")
        group = review_groups.get(merchant_id, [])
        out = {
            "merchant_id": merchant_id,
            "city": merchant.get("city", ""),
            "shop_name": merchant.get("shop_name", ""),
            "review_count": str(len(group)),
            "binding_present": merchant.get("binding_present", ""),
        }
        for domain in DOMAINS:
            merchant_score = as_float(merchant.get(f"{domain}_score", "0"))
            if group:
                consumer_score = sum(
                    as_float(review.get(f"{domain}_score", "0")) for review in group
                ) / len(group)
            else:
                consumer_score = 0.0
            out[f"merchant_{domain}_score"] = f"{merchant_score:.6f}"
            out[f"consumer_{domain}_mean_score"] = f"{consumer_score:.6f}"
            out[f"gap_{domain}"] = f"{merchant_score - consumer_score:.6f}"
        output_rows.append(out)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    main()
