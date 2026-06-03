#!/usr/bin/env python3
"""
scripts/harvest_primary_from_culture_memory.py

Harvest primary-source candidates from public culture-memory platforms.

Currently supports a Playwright-based adapter for Taiwan Culture Memory Bank.
The output is a candidate list for human review, not automatically accepted
attestations.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import random
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote


class SourceAdapter:
    def __init__(self, source_name: str, search_url_template: str):
        self.source_name = source_name
        self.search_url_template = search_url_template

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        return self.search_url_template.format(keyword=quote(keyword), page=page)

    async def wait_for_results(self, page: Any) -> None:
        await page.wait_for_selector(".search-item, .item, .result-item, article", timeout=15000)

    async def parse_result_page(self, page: Any) -> list[dict]:
        raise NotImplementedError


class TaiwanCultureMemoryAdapter(SourceAdapter):
    def __init__(self):
        super().__init__(
            source_name="國家文化記憶庫",
            search_url_template="https://memory.culture.tw/Home/List?Keyword={keyword}&page={page}",
        )

    async def wait_for_results(self, page: Any) -> None:
        await page.wait_for_selector(
            ".search-result-list .result-item, .result-item, .card, article, .list-item",
            timeout=15000,
        )

    async def parse_result_page(self, page: Any) -> list[dict]:
        selectors = [
            ".search-result-list .result-item",
            ".result-item",
            ".card",
            "article",
            ".list-item",
        ]
        items = []
        for selector in selectors:
            items = await page.query_selector_all(selector)
            if items:
                break

        results = []
        for item in items:
            try:
                title_elem = await item.query_selector("a, .result-title a, h3 a, h2 a")
                title = (await title_elem.inner_text()) if title_elem else ""
                detail_url = (await title_elem.get_attribute("href")) if title_elem else ""
                if detail_url and detail_url.startswith("/"):
                    detail_url = "https://memory.culture.tw" + detail_url

                desc_elem = await item.query_selector(".result-description, .description, p, .card-text")
                description = (await desc_elem.inner_text()) if desc_elem else ""
                img_elem = await item.query_selector("img")
                image_url = (await img_elem.get_attribute("src")) if img_elem else ""
                if image_url and image_url.startswith("/"):
                    image_url = "https://memory.culture.tw" + image_url

                year = ""
                text = f"{title} {description}"
                match = re.search(r"\b(19[4-9]\d|20[0-2]\d)\b", text)
                if match:
                    year = match.group(1)

                if title or detail_url or description:
                    results.append(
                        {
                            "source_name": self.source_name,
                            "title": title.strip(),
                            "year": year,
                            "description": " ".join(description.split()),
                            "url": detail_url,
                            "image_url": image_url,
                            "attestation_type": "archive_record",
                        }
                    )
            except Exception as exc:
                print(f"Error parsing result item: {exc}")
        return results


async def harvest_source(adapter: SourceAdapter, keywords: list[str], max_pages: int, delay: tuple[float, float]):
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. Install it with `pip install playwright` and `playwright install chromium`."
        ) from exc

    all_results = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
            )
        )
        page = await context.new_page()
        for keyword in keywords:
            for page_number in range(1, max_pages + 1):
                url = adapter.build_search_url(keyword, page_number)
                print(f"Fetching {adapter.source_name}: {keyword} page {page_number}")
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await adapter.wait_for_results(page)
                    await asyncio.sleep(random.uniform(*delay))
                    results = await adapter.parse_result_page(page)
                    for result in results:
                        result["search_keyword"] = keyword
                        result["page"] = page_number
                        result["search_url"] = url
                    all_results.extend(results)
                    print(f"  -> {len(results)} candidates")
                except Exception as exc:
                    print(f"  !! failed {url}: {exc}")
        await browser.close()
    return all_results


def write_candidates(rows: list[dict], out_csv: str) -> None:
    fields = [
        "source_name",
        "title",
        "year",
        "description",
        "url",
        "image_url",
        "attestation_type",
        "search_keyword",
        "page",
        "search_url",
    ]
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(out_csv).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Harvest primary-source candidates from culture memory platforms.")
    parser.add_argument("--keywords", nargs="+", default=["老照片 滷肉飯", "滷肉飯 菜單", "肉燥飯 1970", "台灣小吃 老照片"])
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--delay", type=float, nargs=2, default=[1.0, 3.0])
    parser.add_argument("--out-csv", default="working/primary_candidates.csv")
    parser.add_argument("--check-deps", action="store_true", help="Only check whether Playwright is importable.")
    args = parser.parse_args()

    if args.check_deps:
        try:
            import playwright  # noqa: F401
        except ImportError:
            print("Playwright missing")
            raise SystemExit(1)
        print("Playwright available")
        return

    adapters = [TaiwanCultureMemoryAdapter()]
    all_candidates = []
    for adapter in adapters:
        rows = asyncio.run(harvest_source(adapter, args.keywords, args.max_pages, tuple(args.delay)))
        all_candidates.extend(rows)

    write_candidates(all_candidates, args.out_csv)
    print(f"Saved {len(all_candidates)} candidate records to {args.out_csv}")


if __name__ == "__main__":
    main()
