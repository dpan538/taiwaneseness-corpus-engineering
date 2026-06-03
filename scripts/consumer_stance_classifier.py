#!/usr/bin/env python3
"""Rule-based consumer stance classifier for Taiwan-marker reviews."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


MERCHANT_TEXT_FIELDS = [
    "shop_name",
    "branch_name",
    "platform_tags",
    "merchant_description",
    "menu_item_names",
    "recommended_dishes",
]

REJECTION_MARKERS = [
    "不是台湾",
    "不是台灣",
    "不像台湾",
    "不像台灣",
    "不正宗",
    "不地道",
    "假台湾",
    "假台灣",
    "根本不是",
    "普通盖饭",
    "普通蓋飯",
    "not Taiwanese",
    "not authentic",
]

NONFOOD_ATTRIBUTE_MARKERS = [
    "服务",
    "服務",
    "态度",
    "態度",
    "老板",
    "老闆",
    "店员",
    "店員",
    "装修",
    "裝修",
    "环境",
    "環境",
    "口音",
    "说话",
    "說話",
    "氛围",
    "氛圍",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify consumer Taiwan-marker stance.")
    parser.add_argument("--reviews", required=True)
    parser.add_argument("--merchants", default=None)
    parser.add_argument("--lexicon", default="config/taiwaneseness_lexicon.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary", default=None)
    return parser.parse_args()


def load_lexicon(path: str) -> tuple[list[str], list[str]]:
    lexicon = json.loads(Path(path).read_text(encoding="utf-8"))
    dish = lexicon.get("dish_markers", [])
    taiwan = lexicon.get("taiwan_markers", [])
    for domain_terms in lexicon.get("domains", {}).values():
        taiwan.extend(term for term in domain_terms if term not in taiwan)
    return dish, sorted(set(taiwan), key=len, reverse=True)


def hits(text: str, markers: list[str]) -> list[str]:
    lowered = text.lower()
    return [marker for marker in markers if marker and marker.lower() in lowered]


def load_merchant_markers(
    merchant_path: str | None, taiwan_markers: list[str]
) -> dict[str, set[str]]:
    if not merchant_path:
        return {}
    result: dict[str, set[str]] = {}
    with Path(merchant_path).open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            text = " ".join((row.get(field) or "") for field in MERCHANT_TEXT_FIELDS)
            result[row.get("merchant_id", "")] = set(hits(text, taiwan_markers))
    return result


def classify_stance(
    review_text: str,
    merchant_markers: set[str],
    taiwan_markers: list[str],
    dish_markers: list[str],
) -> tuple[int, str, list[str]]:
    taiwan_hits = hits(review_text, taiwan_markers)
    dish_hits = hits(review_text, dish_markers)
    rejection_hits = hits(review_text, REJECTION_MARKERS)
    nonfood_hits = hits(review_text, NONFOOD_ATTRIBUTE_MARKERS)

    if not taiwan_hits and not rejection_hits:
        return 0, "no_taiwan_mention", []

    if rejection_hits:
        return 4, "rejects_or_contests_taiwan_authenticity", rejection_hits

    if taiwan_hits and nonfood_hits and not dish_hits:
        return 3, "shifts_taiwan_marker_to_nonfood_attribute", taiwan_hits + nonfood_hits

    overlap = set(taiwan_hits) & merchant_markers
    if overlap:
        return 1, "reproduces_merchant_taiwan_markers", sorted(overlap)

    if taiwan_hits:
        return 2, "adds_new_taiwan_markers", taiwan_hits

    return 0, "no_taiwan_mention", []


def main() -> None:
    args = parse_args()
    dish_markers, taiwan_markers = load_lexicon(args.lexicon)
    merchant_markers = load_merchant_markers(args.merchants, taiwan_markers)

    with Path(args.reviews).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_rows = []
    summary: dict[tuple[str, str], Counter[int]] = defaultdict(Counter)
    for row in rows:
        merchant_id = row.get("merchant_id", "")
        stance, label, evidence = classify_stance(
            row.get("review_text") or "",
            merchant_markers.get(merchant_id, set()),
            taiwan_markers,
            dish_markers,
        )
        enriched = dict(row)
        enriched["consumer_stance"] = str(stance)
        enriched["consumer_stance_label"] = label
        enriched["stance_evidence_markers"] = "|".join(evidence)
        out_rows.append(enriched)
        summary[(row.get("city") or "UNKNOWN", merchant_id)][stance] += 1

    out_fields = fieldnames + [
        "consumer_stance",
        "consumer_stance_label",
        "stance_evidence_markers",
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)

    if args.summary:
        Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.summary).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "city",
                    "merchant_id",
                    "review_count",
                    "no_mention_rate",
                    "reproduction_rate",
                    "transformation_rate",
                    "rejection_rate",
                ],
            )
            writer.writeheader()
            for (city, merchant_id), counts in sorted(summary.items()):
                total = sum(counts.values()) or 1
                writer.writerow(
                    {
                        "city": city,
                        "merchant_id": merchant_id,
                        "review_count": total,
                        "no_mention_rate": counts[0] / total,
                        "reproduction_rate": counts[1] / total,
                        "transformation_rate": (counts[2] + counts[3]) / total,
                        "rejection_rate": counts[4] / total,
                    }
                )


if __name__ == "__main__":
    main()

