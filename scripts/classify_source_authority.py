#!/usr/bin/env python3
"""Classify evidence source authority as primary, secondary, or tertiary."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


PRIMARY_TYPE_HINTS = (
    "newspaper",
    "archive",
    "scan",
    "api",
    "advertisement",
    "registry",
    "trademark",
    "company_filing",
    "digitised_issue",
)
SECONDARY_TYPE_HINTS = (
    "official_tourism",
    "official_event",
    "official_brand",
    "official_food",
    "official_itinerary",
    "municipal",
    "local_food_media",
    "food_media",
    "magazine",
    "news_article",
)
TERTIARY_TYPE_HINTS = ("blog", "review", "forum", "social", "retrospective")

PRIMARY_URL_HINTS = (
    "eresources.nlb.gov.sg/newspapers",
    "newspapers",
    "archive",
    "archives",
    "api",
    "gov.sg",
)
SECONDARY_URL_HINTS = (
    "twtainan.net",
    "khh.travel",
    "taiwan.net.tw",
    "tour",
    "travel",
    "official",
)
TERTIARY_URL_HINTS = (
    "blog",
    "ameblo",
    "tabelog",
    "ifoodie",
    "pixnet",
    "wordpress",
    "facebook",
    "instagram",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add authority_level and authority_weight columns.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--out-csv", default="reports/source_authority.csv")
    return parser.parse_args()


def read_csv(path: str) -> tuple[list[str], list[dict]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def source_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def contains_any(value: str, hints: tuple[str, ...]) -> bool:
    value = value.lower()
    return any(hint in value for hint in hints)


def classify_authority(source_type: str, url: str) -> tuple[str, str]:
    source_type = (source_type or "").lower()
    url = (url or "").lower()

    if contains_any(source_type, TERTIARY_TYPE_HINTS) or contains_any(url, TERTIARY_URL_HINTS):
        return "tertiary", "blog/review/social retrospective source"
    if contains_any(source_type, PRIMARY_TYPE_HINTS) or contains_any(url, PRIMARY_URL_HINTS):
        return "primary", "dated archive/newspaper/registry-like source"
    if contains_any(source_type, SECONDARY_TYPE_HINTS) or contains_any(url, SECONDARY_URL_HINTS):
        return "secondary", "official/media curated narrative source"
    return "secondary", "default secondary classification"


def authority_weight(level: str) -> str:
    return {"primary": "1.0000", "secondary": "0.7000", "tertiary": "0.4000"}.get(level, "0.5000")


def main() -> None:
    args = parse_args()
    fields, records = read_csv(args.attestations)
    counts = Counter()
    for row in records:
        level, reason = classify_authority(row.get("source_type", ""), source_ref(row))
        row["authority_level"] = level
        row["authority_weight"] = authority_weight(level)
        row["authority_reason"] = reason
        counts[level] += 1

    out_fields = list(fields)
    for field in ("authority_level", "authority_weight", "authority_reason"):
        if field not in out_fields:
            out_fields.append(field)

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    summary = ", ".join(f"{level}={count}" for level, count in sorted(counts.items()))
    print(f"Authority levels saved to {args.out_csv}. {summary}.")


if __name__ == "__main__":
    main()
