#!/usr/bin/env python3
"""Estimate semantic overlap between source artifacts.

This complements simple source frequency counts. Two source URLs can be counted
as separate artifacts while still carrying nearly identical prose.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import re
from collections import Counter, defaultdict
from pathlib import Path


TEXT_FIELDS = ("original_text", "text_for_scoring", "window_text_concatenated", "notes")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check semantic overlap between source artifacts.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument("--similarity-threshold", type=float, default=0.30)
    parser.add_argument("--texts-per-source", type=int, default=3)
    parser.add_argument("--out-csv", default="reports/semantic_source_overlap.csv")
    return parser.parse_args()


def read_rows(path: str) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def source_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def evidence_text(row: dict) -> str:
    for field in TEXT_FIELDS:
        value = (row.get(field) or "").strip()
        if value:
            value = re.sub(r"\s+", " ", value)
            value = re.sub(r"https?://\S+", "", value)
            return value.strip()
    return ""


def write_csv(path: str, rows: list[dict]) -> None:
    fieldnames = [
        "source_1",
        "source_2",
        "source_type_1",
        "source_type_2",
        "count_1",
        "count_2",
        "similarity",
    ]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    rows = read_rows(args.attestations)

    source_texts: dict[str, list[str]] = defaultdict(list)
    source_types: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        ref = source_ref(row)
        text = evidence_text(row)
        if not ref or not text:
            continue
        source_texts[ref].append(text[:700])
        source_types[ref][row.get("source_type", "")] += 1

    top_sources = sorted(source_texts.items(), key=lambda item: len(item[1]), reverse=True)[: args.sample_size]
    source_repr = {ref: " ".join(texts[: args.texts_per_source]) for ref, texts in top_sources}
    refs = list(source_repr)

    findings: list[dict] = []
    for i, left in enumerate(refs):
        for right in refs[i + 1 :]:
            similarity = difflib.SequenceMatcher(None, source_repr[left], source_repr[right]).ratio()
            if similarity < args.similarity_threshold:
                continue
            findings.append(
                {
                    "source_1": left,
                    "source_2": right,
                    "source_type_1": source_types[left].most_common(1)[0][0],
                    "source_type_2": source_types[right].most_common(1)[0][0],
                    "count_1": str(len(source_texts[left])),
                    "count_2": str(len(source_texts[right])),
                    "similarity": f"{similarity:.4f}",
                }
            )

    write_csv(args.out_csv, findings)
    print(
        f"Found {len(findings)} source pairs with similarity >= {args.similarity_threshold:.2f}. "
        f"Output: {args.out_csv}"
    )


if __name__ == "__main__":
    main()
