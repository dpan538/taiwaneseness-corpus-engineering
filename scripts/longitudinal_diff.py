#!/usr/bin/env python3
"""Compare merchant marker changes across repeated capture dates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import date
from pathlib import Path


TEXT_FIELDS = [
    "shop_name",
    "branch_name",
    "platform_tags",
    "merchant_description",
    "menu_item_names",
    "recommended_dishes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute longitudinal merchant marker diffs.")
    parser.add_argument("--merchants", required=True)
    parser.add_argument("--lexicon", default="config/taiwaneseness_lexicon.json")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def load_marker_groups(path: str) -> dict[str, list[str]]:
    lexicon = json.loads(Path(path).read_text(encoding="utf-8"))
    groups = {
        "dish": lexicon.get("dish_markers", []),
        "taiwan": lexicon.get("taiwan_markers", []),
    }
    for name, terms in lexicon.get("domains", {}).items():
        groups[name] = terms
    return groups


def text_blob(row: dict[str, str]) -> str:
    return " ".join((row.get(field) or "") for field in TEXT_FIELDS)


def text_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def count_hits(text: str, markers: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for marker in markers if marker and marker.lower() in lowered)


def main() -> None:
    args = parse_args()
    marker_groups = load_marker_groups(args.lexicon)

    by_merchant: dict[str, list[dict[str, str]]] = defaultdict(list)
    with Path(args.merchants).open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            by_merchant[row.get("merchant_id", "")].append(row)

    out_rows = []
    for merchant_id, rows in sorted(by_merchant.items()):
        if len(rows) < 2:
            continue
        rows.sort(key=lambda r: r.get("capture_date") or "")
        for before, after in zip(rows, rows[1:]):
            before_text = text_blob(before)
            after_text = text_blob(after)
            out = {
                "merchant_id": merchant_id,
                "city": after.get("city") or before.get("city") or "",
                "platform": after.get("platform") or before.get("platform") or "",
                "capture_date_before": before.get("capture_date") or "",
                "capture_date_after": after.get("capture_date") or "",
                "text_changed": str(text_hash(before_text) != text_hash(after_text)),
            }
            for group, markers in marker_groups.items():
                before_count = count_hits(before_text, markers)
                after_count = count_hits(after_text, markers)
                out[f"{group}_markers_before"] = before_count
                out[f"{group}_markers_after"] = after_count
                out[f"{group}_marker_delta"] = after_count - before_count
            out_rows.append(out)

    fields = [
        "merchant_id",
        "city",
        "platform",
        "capture_date_before",
        "capture_date_after",
        "text_changed",
    ]
    for group in marker_groups:
        fields.extend(
            [f"{group}_markers_before", f"{group}_markers_after", f"{group}_marker_delta"]
        )

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)


if __name__ == "__main__":
    main()

