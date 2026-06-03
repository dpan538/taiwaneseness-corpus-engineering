#!/usr/bin/env python3
"""Append documented zero-yield searches to negative_searches.csv."""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import date
from pathlib import Path


FIELDS = [
    "negative_search_id",
    "source_id",
    "phase",
    "corridor",
    "query_terms",
    "date_start",
    "date_end",
    "access_date",
    "result_count",
    "search_url_or_command",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--corridor", required=True)
    parser.add_argument("--query-terms", required=True)
    parser.add_argument("--date-start", default="")
    parser.add_argument("--date-end", default="")
    parser.add_argument("--search-url-or-command", default="manual_or_api")
    parser.add_argument("--notes", default="")
    parser.add_argument("--out", default="data/negative_searches.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = "|".join([args.source_id, args.phase, args.corridor, args.query_terms, args.date_start, args.date_end])
    row = {
        "negative_search_id": "NEG_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:12],
        "source_id": args.source_id,
        "phase": args.phase,
        "corridor": args.corridor,
        "query_terms": args.query_terms,
        "date_start": args.date_start,
        "date_end": args.date_end,
        "access_date": date.today().isoformat(),
        "result_count": "0",
        "search_url_or_command": args.search_url_or_command,
        "notes": args.notes,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out.exists()
    with out.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    print(row["negative_search_id"])


if __name__ == "__main__":
    main()

