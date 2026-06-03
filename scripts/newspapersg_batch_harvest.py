#!/usr/bin/env python3
"""Generate NewspaperSG manual search plans and attestation templates.

This script does not download or scrape NewspaperSG. It creates a structured
list of advanced-search URLs for manual inspection, plus a CSV template for
recording one attestation per original ad/article artifact.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus


DEFAULT_KEYWORDS = [
    "Taiwan porridge",
    "Taiwanese restaurant",
    "Taiwanese food",
    "Taiwanese snack",
    "Formosa restaurant",
    "Taipei restaurant Singapore",
    "lu rou fan",
    "braised pork rice Taiwan",
]

SEARCH_FIELDS = [
    "keyword",
    "from_date",
    "to_date",
    "url",
    "status",
    "result_count",
    "valid_attestations",
    "attestation_id",
    "notes",
]

TEMPLATE_FIELDS = [
    "attestation_id",
    "year",
    "date",
    "period",
    "brand_or_category",
    "city",
    "province",
    "corridor",
    "source_type",
    "source_name",
    "source_url",
    "attestation_type",
    "text_for_scoring",
    "confidence",
    "notes",
    "source_id",
    "verification_level",
    "region",
    "original_text",
    "dish_marker",
    "taiwan_marker",
    "ownership_category",
    "capital_origin",
    "source_url_or_archive_ref",
    "dedupe_key",
    "merged_from_attestation_ids",
    "merged_row_count",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a NewspaperSG manual search plan.")
    parser.add_argument("--keywords", nargs="+", help="Search phrases. If omitted, uses --keywords-file or defaults.")
    parser.add_argument("--keywords-file", default="", help="Text file with one search phrase per line.")
    parser.add_argument("--start-year", type=int, default=1975)
    parser.add_argument("--end-year", type=int, default=1987)
    parser.add_argument(
        "--interval",
        choices=["year", "month", "single"],
        default="year",
        help="Date range granularity.",
    )
    parser.add_argument("--out-csv", default="working/newspapersg_search_plan.csv")
    parser.add_argument("--template-csv", default="working/manual_harvest_template.csv")
    parser.add_argument("--include-example", action="store_true", help="Add one commented-style example row to template.")
    return parser.parse_args()


def load_keywords(args: argparse.Namespace) -> list[str]:
    if args.keywords:
        return args.keywords
    if args.keywords_file:
        path = Path(args.keywords_file)
        if path.exists():
            with path.open(encoding="utf-8") as f:
                keywords = [line.strip() for line in f if line.strip() and not line.lstrip().startswith("#")]
            if keywords:
                return keywords
        print(f"Keyword file not found or empty: {args.keywords_file}; using defaults.", file=sys.stderr)
    print(f"No keywords provided, using defaults: {DEFAULT_KEYWORDS}", file=sys.stderr)
    return DEFAULT_KEYWORDS


def generate_date_ranges(start_year: int, end_year: int, interval: str) -> list[tuple[str, str]]:
    if start_year > end_year:
        raise ValueError("--start-year must be <= --end-year")
    if interval == "single":
        return [(f"{start_year}-01-01", f"{end_year}-12-31")]
    ranges = []
    for year in range(start_year, end_year + 1):
        if interval == "year":
            ranges.append((f"{year}-01-01", f"{year}-12-31"))
            continue
        for month in range(1, 13):
            from_date = f"{year}-{month:02d}-01"
            if month == 12:
                to_date = f"{year}-12-31"
            else:
                to_date = (datetime(year, month + 1, 1) - timedelta(days=1)).strftime("%Y-%m-%d")
            ranges.append((from_date, to_date))
    return ranges


def build_search_url(keyword: str, from_date: str, to_date: str) -> str:
    encoded = quote_plus(keyword)
    return (
        "https://eresources.nlb.gov.sg/newspapers/NewspaperSearch"
        f"?searchType=advanced&keyword={encoded}&fromdate={from_date}&todate={to_date}"
    )


def period_for_year(year: int) -> str:
    if 1946 <= year <= 1987:
        return "1946-1987_taiwan_side_formation"
    if 1988 <= year <= 2014:
        return "1987-2015_cross_strait_diffusion"
    if 2015 <= year <= 2025:
        return "2015-2025_internet_wanghong_capital"
    return "out_of_scope"


def write_search_plan(path: str, keywords: list[str], date_ranges: list[tuple[str, str]]) -> int:
    rows = []
    for keyword in keywords:
        for from_date, to_date in date_ranges:
            rows.append(
                {
                    "keyword": keyword,
                    "from_date": from_date,
                    "to_date": to_date,
                    "url": build_search_url(keyword, from_date, to_date),
                    "status": "pending",
                    "result_count": "",
                    "valid_attestations": "",
                    "attestation_id": "",
                    "notes": "",
                }
            )
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SEARCH_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_template(path: str, include_example: bool) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if include_example:
        rows.append(
            {
                "attestation_id": "SRC_NEWSG_MANUAL_001",
                "year": "1985",
                "date": "1985-06-12",
                "period": period_for_year(1985),
                "brand_or_category": "Goodwood Park Hotel",
                "city": "Singapore",
                "province": "",
                "corridor": "Singapore",
                "source_type": "newspaper_archive",
                "source_name": "NewspaperSG",
                "source_url": "https://eresources.nlb.gov.sg/newspapers/digitised/page/example",
                "attestation_type": "ad",
                "text_for_scoring": "1985 Singapore ad Taiwan porridge Goodwood Park Hotel",
                "confidence": "high",
                "notes": "Example row; replace or delete before merge.",
                "source_id": "SRC_NEWSG_MANUAL_001",
                "verification_level": "probable",
                "region": "Singapore",
                "original_text": "Advertisement: Traditional Taiwan porridge with over 40 items.",
                "dish_marker": "Taiwan porridge",
                "taiwan_marker": "Taiwan",
                "ownership_category": "",
                "capital_origin": "",
                "source_url_or_archive_ref": "https://eresources.nlb.gov.sg/newspapers/digitised/page/example",
                "dedupe_key": "",
                "merged_from_attestation_ids": "",
                "merged_row_count": "1",
            }
        )
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TEMPLATE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    keywords = load_keywords(args)
    date_ranges = generate_date_ranges(args.start_year, args.end_year, args.interval)
    count = write_search_plan(args.out_csv, keywords, date_ranges)
    write_template(args.template_csv, args.include_example)
    print(f"Generated {count} search URLs -> {args.out_csv}")
    print(f"Manual harvest template created -> {args.template_csv}")
    print("Next: inspect URLs manually, then record one row per original ad/article artifact.")


if __name__ == "__main__":
    main()
