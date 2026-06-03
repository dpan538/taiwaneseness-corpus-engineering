#!/usr/bin/env python3
"""Generate manual-search instructions for restricted Taiwan newspaper archives.

The important archives for 1946-1987 are often login/IP/terms restricted.
This script does not scrape them. It creates a reproducible search queue so a
researcher can perform the searches, download permitted artifacts, and record
the results in the raw capture manifest.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
from datetime import date
from pathlib import Path


DEFAULT_SOURCES = ["UDNData", "ChinaTimes", "TBMC"]
DEFAULT_KEYWORDS = ["魯肉飯", "滷肉飯", "肉燥飯", "肉臊飯", "台菜", "臺菜", "台灣小吃"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS))
    parser.add_argument("--sources", default=",".join(DEFAULT_SOURCES))
    parser.add_argument("--year-start", type=int, default=1946)
    parser.add_argument("--year-end", type=int, default=1987)
    parser.add_argument("--out-json", default="raw/manifests/manual_download_instructions.json")
    parser.add_argument("--out-csv", default="data/archive_search_log.csv")
    return parser.parse_args()


def source_url(source: str, keyword: str, year: int) -> str:
    encoded = urllib.parse.quote(keyword)
    if source == "UDNData":
        return f"https://udndata.com/ndapp/udntag/finance/Search?keyword={encoded}&from={year}0101&to={year}1231"
    if source == "ChinaTimes":
        return f"https://cshopping.chinatimes.com/search.aspx?keyword={encoded}&year={year}"
    if source == "TBMC":
        return f"https://www.tbmc.com.tw/zh-tw/search?keyword={encoded}&year={year}"
    return ""


def main() -> None:
    args = parse_args()
    keywords = [x.strip() for x in args.keywords.split(",") if x.strip()]
    sources = [x.strip() for x in args.sources.split(",") if x.strip()]

    instructions = []
    search_rows = []
    idx = 1
    for source in sources:
        for keyword in keywords:
            for year in range(args.year_start, args.year_end + 1):
                sid = f"MANUAL_{idx:06d}"
                url = source_url(source, keyword, year)
                instructions.append(
                    {
                        "search_id": sid,
                        "source_name": source,
                        "keyword": keyword,
                        "year": year,
                        "search_url": url,
                        "action": "manual_search_download_if_permitted_then_update_raw_capture_manifest",
                        "notes": "Do not automate restricted archives unless explicit permission exists.",
                    }
                )
                search_rows.append(
                    {
                        "search_id": sid,
                        "source_id": source,
                        "query_terms": keyword,
                        "date_start": f"{year}-01-01",
                        "date_end": f"{year}-12-31",
                        "filters": json.dumps({"source_name": source}, ensure_ascii=False),
                        "result_count": "",
                        "earliest_hit_date": "",
                        "latest_hit_date": "",
                        "sample_hit_ids": "",
                        "search_url_or_command": url,
                        "notes": "manual restricted-archive search queue",
                    }
                )
                idx += 1

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(instructions, ensure_ascii=False, indent=2), encoding="utf-8")

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out_csv.exists()
    with out_csv.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(search_rows[0].keys()))
        if write_header:
            writer.writeheader()
        writer.writerows(search_rows)

    print(json.dumps({"instructions": len(instructions), "out_json": args.out_json, "out_csv": args.out_csv}, ensure_ascii=False))


if __name__ == "__main__":
    main()

