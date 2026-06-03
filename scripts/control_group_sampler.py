#!/usr/bin/env python3
"""Sample target and control merchant groups from captured platform records.

This script is intentionally offline: it samples from an existing merchant CSV
instead of crawling a platform. Use it after compliant platform capture.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_OTHER_TAIWAN_DISH_MARKERS = [
    "台湾牛肉面",
    "台灣牛肉麵",
    "台式牛肉面",
    "台式牛肉麵",
    "台湾香肠",
    "台灣香腸",
    "台湾奶茶",
    "台灣奶茶",
    "珍珠奶茶",
    "台湾鸡排",
    "台灣雞排",
    "盐酥鸡",
    "鹽酥雞",
    "台湾小吃",
    "台灣小吃",
    "台湾菜",
    "台灣菜",
]


TEXT_FIELDS = [
    "shop_name",
    "branch_name",
    "platform_tags",
    "merchant_description",
    "menu_item_names",
    "recommended_dishes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sample Taiwan lu rou fan target merchants and two control groups."
    )
    parser.add_argument("--merchants", required=True, help="Input merchant CSV.")
    parser.add_argument("--lexicon", default="config/taiwaneseness_lexicon.json")
    parser.add_argument("--per-city", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20260603)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary", default=None)
    return parser.parse_args()


def load_lexicon(path: str) -> tuple[list[str], list[str]]:
    lexicon = json.loads(Path(path).read_text(encoding="utf-8"))
    return lexicon.get("dish_markers", []), lexicon.get("taiwan_markers", [])


def row_text(row: dict[str, str]) -> str:
    return " ".join((row.get(field) or "") for field in TEXT_FIELDS)


def contains_any(text: str, markers: list[str]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers if marker)


def marker_hits(text: str, markers: list[str]) -> list[str]:
    lowered = text.lower()
    return [marker for marker in markers if marker and marker.lower() in lowered]


def classify_group(
    row: dict[str, str],
    dish_markers: list[str],
    taiwan_markers: list[str],
    other_taiwan_dishes: list[str],
) -> tuple[str | None, list[str], list[str], list[str]]:
    text = row_text(row)
    dish_hits = marker_hits(text, dish_markers)
    taiwan_hits = marker_hits(text, taiwan_markers)
    other_hits = marker_hits(text, other_taiwan_dishes)

    has_lrf = bool(dish_hits)
    has_taiwan = bool(taiwan_hits)
    has_other_taiwan_dish = bool(other_hits)

    if has_lrf and has_taiwan:
        return "target_taiwan_lu_rou_fan", dish_hits, taiwan_hits, other_hits
    if has_lrf and not has_taiwan:
        return "control_same_dish_no_taiwan", dish_hits, taiwan_hits, other_hits
    if has_taiwan and has_other_taiwan_dish and not has_lrf:
        return "control_taiwan_other_dish", dish_hits, taiwan_hits, other_hits
    return None, dish_hits, taiwan_hits, other_hits


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    dish_markers, taiwan_markers = load_lexicon(args.lexicon)

    with Path(args.merchants).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    buckets: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    all_counts: Counter[tuple[str, str]] = Counter()

    for row in rows:
        group, dish_hits, taiwan_hits, other_hits = classify_group(
            row, dish_markers, taiwan_markers, DEFAULT_OTHER_TAIWAN_DISH_MARKERS
        )
        if not group:
            continue
        city = row.get("city") or "UNKNOWN"
        enriched = dict(row)
        enriched["experimental_group"] = group
        enriched["dish_marker_hits"] = "|".join(dish_hits)
        enriched["taiwan_marker_hits"] = "|".join(taiwan_hits)
        enriched["other_taiwan_dish_hits"] = "|".join(other_hits)
        buckets[(city, group)].append(enriched)
        all_counts[(city, group)] += 1

    sampled: list[dict[str, str]] = []
    for key, group_rows in sorted(buckets.items()):
        random.shuffle(group_rows)
        sampled.extend(group_rows[: args.per_city])

    out_fields = fieldnames + [
        "experimental_group",
        "dish_marker_hits",
        "taiwan_marker_hits",
        "other_taiwan_dish_hits",
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sampled)

    if args.summary:
        Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.summary).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["city", "experimental_group", "available", "sampled"]
            )
            writer.writeheader()
            sampled_counts = Counter(
                ((row.get("city") or "UNKNOWN"), row["experimental_group"])
                for row in sampled
            )
            for (city, group), available in sorted(all_counts.items()):
                writer.writerow(
                    {
                        "city": city,
                        "experimental_group": group,
                        "available": available,
                        "sampled": sampled_counts[(city, group)],
                    }
                )


if __name__ == "__main__":
    main()

