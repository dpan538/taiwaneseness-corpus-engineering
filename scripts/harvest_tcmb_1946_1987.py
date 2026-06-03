#!/usr/bin/env python3
"""Harvest TCMB open-data rows for 1946-1987 food-history candidates.

This script uses public open-data JSON endpoints exposed through data.gov.tw /
TCMB. It does not bypass logins, paywalls, robots rules, or platform controls.

The output is a candidate/attestation table. Records are marked `candidate`
unless they contain a relevant term and a plausible year in the 1946-1987
window. Human/source review is still required before treating them as verified.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import ssl
import time
import urllib.request
from pathlib import Path
from typing import Any


ENDPOINTS = {
    "TCMB_ART_AND_HUMANITY": "https://tcmbdata.culture.tw/opendata/dataSet/culture?subject=ART_AND_HUMANITY",
    "TCMB_CULTURE_AND_RELIGION": "https://tcmbdata.culture.tw/opendata/dataSet/culture?subject=CULTURE_AND_RELIGION",
}

DIRECT_DISH_TERMS = [
    "魯肉飯",
    "滷肉飯",
    "卤肉饭",
    "肉燥飯",
    "肉燥饭",
    "肉臊飯",
    "肉臊饭",
]

FOOD_CONTEXT_TERMS = [
    "小吃",
    "夜市",
    "路邊攤",
    "路边摊",
    "飯攤",
    "饭摊",
    "圓環",
    "圆环",
    "雙連",
    "双连",
    "寧夏",
    "宁夏",
    "華西街",
    "华西街",
    "台菜",
    "臺菜",
    "台灣菜",
    "台湾菜",
    "台灣料理",
    "台湾料理",
    "台灣小吃",
    "台湾小吃",
]

YEARS_RE = re.compile(r"(19[4-8][0-9])|([一二三四五六七八九零〇]{2,4})年代")


def fetch_json(url: str, user_agent: str, insecure_tls: bool = False) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    context = ssl._create_unverified_context() if insecure_tls else None
    with urllib.request.urlopen(request, timeout=90, context=context) as response:
        body = response.read()
    return json.loads(body.decode("utf-8"))


def text_of(row: dict) -> str:
    parts = [
        str(row.get("title", "") or ""),
        str(row.get("description", "") or ""),
        " ".join(str(x) for x in row.get("keywords", []) or []),
        " ".join(str(x) for x in row.get("subjects", []) or []),
        str(row.get("createDept", "") or ""),
    ]
    return " ".join(parts)


def matched_terms(text: str, terms: list[str]) -> list[str]:
    return sorted({term for term in terms if term in text})


def extract_years(text: str) -> list[int]:
    years: set[int] = set()
    for match in re.finditer(r"19[4-8][0-9]", text):
        year = int(match.group(0))
        if 1946 <= year <= 1987:
            years.add(year)
    era_map = {
        "四十": 1940,
        "五十": 1950,
        "六十": 1960,
        "七十": 1970,
        "八十": 1980,
    }
    for label, start in era_map.items():
        if f"{label}年代" in text:
            for year in range(max(start, 1946), min(start + 10, 1988)):
                years.add(year)
    return sorted(years)


def classify_period(year: int) -> str:
    if 1946 <= year <= 1987:
        return "1946-1987_taiwan_side_formation"
    return "outside_macro_scope"


def evidence_type(dish: list[str], context: list[str]) -> str:
    if dish:
        return "direct_dish_term"
    if any(term in context for term in ["台菜", "臺菜", "台灣菜", "台湾菜", "台灣料理", "台湾料理"]):
        return "taiwanese_cuisine_term"
    if context:
        return "food_context_term"
    return "no_match"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/harvested/tcmb_1946_1987_candidates.csv")
    parser.add_argument("--raw-dir", default="data/raw/tcmb_open_data")
    parser.add_argument("--limit", type=int, default=0, help="Optional row limit per endpoint")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument(
        "--user-agent",
        default="TaiwanesenessLuRouFanResearch/0.1 contact: local-research",
    )
    parser.add_argument(
        "--insecure-tls",
        action="store_true",
        help="Disable TLS certificate verification for endpoints with broken certificates; record this in run notes.",
    )
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    out_rows: list[dict] = []
    seen: set[tuple[str, str, int]] = set()

    for endpoint_name, url in ENDPOINTS.items():
        data = fetch_json(url, args.user_agent, insecure_tls=args.insecure_tls)
        raw_path = raw_dir / f"{endpoint_name}.json"
        raw_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        rows = data.get("rows", []) if isinstance(data, dict) else []
        if args.limit:
            rows = rows[: args.limit]

        for row in rows:
            text = text_of(row)
            dish_terms = matched_terms(text, DIRECT_DISH_TERMS)
            context_terms = matched_terms(text, FOOD_CONTEXT_TERMS)
            if not dish_terms and not context_terms:
                continue
            years = extract_years(text)
            if not years:
                continue

            for year in years:
                key = (endpoint_name, str(row.get("identifier") or row.get("id")), year)
                if key in seen:
                    continue
                seen.add(key)
                etype = evidence_type(dish_terms, context_terms)
                level = "probable" if etype == "direct_dish_term" else "candidate"
                out_rows.append(
                    {
                        "attestation_id": f"TCMB_{len(out_rows)+1:05d}",
                        "source_id": str(row.get("identifier") or row.get("id") or ""),
                        "verification_level": level,
                        "period": classify_period(year),
                        "year": str(year),
                        "date": "",
                        "brand_or_category": "",
                        "city": "",
                        "region": "Taiwan-side",
                        "source_type": "tcmb_open_data",
                        "source_name": endpoint_name,
                        "attestation_type": etype,
                        "original_text": text[:1200],
                        "text_for_scoring": text[:1200],
                        "dish_marker": "|".join(dish_terms),
                        "taiwan_marker": "Taiwan-side",
                        "ownership_category": "",
                        "capital_origin": "",
                        "source_url_or_archive_ref": row.get("tcmbUrl", "") or row.get("originalUrl", ""),
                        "notes": f"TCMB open-data candidate; insecure_tls={args.insecure_tls}; contentLicense={row.get('contentLicense','')}; imageLicense={row.get('imageLicense','')}",
                    }
                )

        time.sleep(args.delay)

    fieldnames = [
        "attestation_id",
        "source_id",
        "verification_level",
        "period",
        "year",
        "date",
        "brand_or_category",
        "city",
        "region",
        "source_type",
        "source_name",
        "attestation_type",
        "original_text",
        "text_for_scoring",
        "dish_marker",
        "taiwan_marker",
        "ownership_category",
        "capital_origin",
        "source_url_or_archive_ref",
        "notes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(json.dumps({"output": str(output_path), "rows": len(out_rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
