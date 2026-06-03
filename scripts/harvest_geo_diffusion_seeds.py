#!/usr/bin/env python3
"""
scripts/harvest_geo_diffusion_seeds.py

Generate a manual search plan for the geo-diffusion subcorpus. The output is a
work queue, not harvested evidence. Each resulting attestation should still be
manually verified and stored separately from the historical Taiwan-side corpus.
"""

from __future__ import annotations

import argparse
import csv
import sys
from urllib.parse import quote


STRATEGIES = {
    "Hong_Kong": {
        "corridor": "Hong Kong",
        "source": "HK MMIS",
        "base_url": "https://mmis.hkpl.gov.hk/",
        "keywords": ["台灣滷肉飯", "台灣肉燥飯", "台灣小吃", "台灣菜", "台式滷肉飯"],
        "start_year": 1987,
        "end_year": 2005,
        "source_type": "newspaper_archive",
        "notes": "Search old newspapers in HK MMIS; prefer ads/articles with date, page, and publication.",
    },
    "Macau": {
        "corridor": "Macau",
        "source": "Macau newspaper/archive search",
        "base_url": "",
        "keywords": ["台灣滷肉飯", "台灣肉燥飯", "台灣小吃", "台灣菜"],
        "start_year": 1987,
        "end_year": 2005,
        "source_type": "newspaper_archive",
        "notes": "Look for dated newspaper ads/articles or cultural-event listings; keep Macau separate from Hong Kong.",
    },
    "Fujian_Xiamen_Fuzhou": {
        "corridor": "Fujian coastal",
        "source": "福建日报/厦门日报/福州晚报 databases or library indexes",
        "base_url": "",
        "keywords": ["台湾卤肉饭", "台式卤肉饭", "台湾小吃店", "台湾美食节", "台商餐饮"],
        "start_year": 1990,
        "end_year": 2005,
        "source_type": "newspaper_archive",
        "notes": "Prioritize Xiamen/Fuzhou dated reports; avoid undated retrospective brand pages unless clearly sourced.",
    },
    "Guangdong_Guangzhou_Shenzhen": {
        "corridor": "Guangdong coastal",
        "source": "南方日报/广州日报/深圳特区报 databases or library indexes",
        "base_url": "",
        "keywords": ["台湾卤肉饭", "台式卤肉饭", "台湾小吃", "台湾美食节", "台商餐饮"],
        "start_year": 1990,
        "end_year": 2005,
        "source_type": "newspaper_archive",
        "notes": "Prioritize dated newspaper items and opening/food-festival reports.",
    },
    "Sichuan_Chengdu": {
        "corridor": "Sichuan inland",
        "source": "华西都市报/成都商报 indexes",
        "base_url": "",
        "keywords": ["台湾卤肉饭", "台湾小吃", "台湾美食节", "台式快餐", "台商餐饮"],
        "start_year": 1998,
        "end_year": 2010,
        "source_type": "newspaper_archive",
        "notes": "Treat online reposts cautiously; record original newspaper/date if available.",
    },
    "Hubei_Wuhan": {
        "corridor": "Hubei inland",
        "source": "楚天都市报/长江日报 indexes",
        "base_url": "",
        "keywords": ["台湾卤肉饭", "台湾小吃", "台湾美食节", "台式快餐", "台商餐饮"],
        "start_year": 1998,
        "end_year": 2010,
        "source_type": "newspaper_archive",
        "notes": "Prioritize dated local reports; use Baidu only as a pointer to original publication metadata.",
    },
    "General_Mainland": {
        "corridor": "Mainland China",
        "source": "人民日报图文数据库 / national newspaper databases",
        "base_url": "",
        "keywords": ["台湾卤肉饭", "台湾小吃", "台商餐饮", "台湾美食节"],
        "start_year": 1987,
        "end_year": 2015,
        "source_type": "newspaper_archive",
        "notes": "Use national results as context or cross-corridor corroboration, not as a replacement for local sources.",
    },
}


def build_search_url(strategy, keyword, year):
    source = strategy["source"]
    base_url = strategy.get("base_url") or ""
    if source == "HK MMIS":
        return f"{base_url} (search: {keyword}, year: {year})"
    if "百度" in source:
        return f"https://www.baidu.com/s?wd={quote(keyword + ' ' + str(year))}"
    return f"Search {source} for '{keyword}' in {year}"


def main():
    parser = argparse.ArgumentParser(description="Generate geo-diffusion search tasks.")
    parser.add_argument(
        "--regions",
        nargs="+",
        default=[
            "Hong_Kong",
            "Macau",
            "Fujian_Xiamen_Fuzhou",
            "Guangdong_Guangzhou_Shenzhen",
            "Sichuan_Chengdu",
            "Hubei_Wuhan",
            "General_Mainland",
        ],
    )
    parser.add_argument("--out-csv", default="working/geo_diffusion_search_plan.csv")
    parser.add_argument("--template-csv", default="working/geo_diffusion_manual_template.csv")
    args = parser.parse_args()

    rows = []
    for region in args.regions:
        strategy = STRATEGIES.get(region)
        if not strategy:
            print(f"Region {region} is not defined; skipping.", file=sys.stderr)
            continue
        for keyword in strategy["keywords"]:
            for year in range(strategy["start_year"], strategy["end_year"] + 1):
                rows.append(
                    {
                        "region": region,
                        "corridor": strategy["corridor"],
                        "source": strategy["source"],
                        "source_type": strategy["source_type"],
                        "keyword": keyword,
                        "year": year,
                        "url_or_command": build_search_url(strategy, keyword, year),
                        "notes": strategy["notes"],
                        "status": "pending",
                        "attestation_id": "",
                    }
                )

    with open(args.out_csv, "w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "region",
            "corridor",
            "source",
            "source_type",
            "keyword",
            "year",
            "url_or_command",
            "notes",
            "status",
            "attestation_id",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    template_fields = [
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
        "original_text",
        "dish_marker",
        "taiwan_marker",
        "confidence",
        "notes",
        "source_id",
        "verification_level",
        "authority_level",
        "ownership_category",
        "capital_origin",
    ]
    with open(args.template_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=template_fields)
        writer.writeheader()

    print(f"Generated {len(rows)} geo-diffusion search tasks: {args.out_csv}")
    print(f"Manual template created: {args.template_csv}")


if __name__ == "__main__":
    main()
