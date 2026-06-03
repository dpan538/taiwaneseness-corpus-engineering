#!/usr/bin/env python3
"""Find copied or template-like narratives within the same brand group.

The goal is to detect records that look independent by source metadata but
share highly similar evidence text. That pattern can inflate the corpus if
multiple records descend from the same press release, tourism template, or
machine-written topup template.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import re
from collections import defaultdict
from pathlib import Path


TEXT_FIELDS = ("original_text", "text_for_scoring", "window_text_concatenated", "notes")
CHECKPOINT_TOKEN_RE = re.compile(
    r"(\b(?:checkpoint|batch|topup)\b|[_\-\s]?(?:W|X|Y|Z|AA|AB|AC|AD)\d{1,3}\b)",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect copied/template-like narratives within brand groups.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--similarity-threshold", type=float, default=0.85)
    parser.add_argument("--out-csv", default="reports/narrative_clusters.csv")
    parser.add_argument("--max-per-brand", type=int, default=150)
    parser.add_argument("--no-normalize-brand", action="store_true")
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
            return normalize_text(value)
    return ""


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"https?://\S+", "", text)
    return text.strip()


def normalize_brand(brand: str, enabled: bool) -> str:
    brand = re.sub(r"\s+", " ", brand or "").strip()
    if not enabled:
        return brand
    brand = CHECKPOINT_TOKEN_RE.sub(" ", brand)
    brand = re.sub(r"\s+", " ", brand).strip(" _-/")
    return brand or "(blank_after_normalization)"


def write_csv(path: str, rows: list[dict]) -> None:
    fieldnames = [
        "brand",
        "normalized_brand",
        "attestation_id_1",
        "attestation_id_2",
        "source_ref_1",
        "source_ref_2",
        "source_type_1",
        "source_type_2",
        "year_1",
        "year_2",
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
    normalize = not args.no_normalize_brand

    groups: dict[str, list[dict]] = defaultdict(list)
    raw_brand_for_group: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        brand = (row.get("brand_or_category") or row.get("brand") or "").strip()
        text = evidence_text(row)
        if not brand or not text:
            continue
        group_key = normalize_brand(brand, normalize)
        raw_brand_for_group[group_key].add(brand)
        groups[group_key].append(
            {
                "attestation_id": row.get("attestation_id", ""),
                "source_ref": source_ref(row),
                "source_type": row.get("source_type", ""),
                "year": row.get("year", ""),
                "text": text[:2000],
            }
        )

    findings: list[dict] = []
    for normalized_brand, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        entries = entries[: args.max_per_brand]
        for i, left in enumerate(entries):
            for right in entries[i + 1 :]:
                if left["source_ref"] and left["source_ref"] == right["source_ref"]:
                    continue
                similarity = difflib.SequenceMatcher(None, left["text"], right["text"]).ratio()
                if similarity < args.similarity_threshold:
                    continue
                findings.append(
                    {
                        "brand": "; ".join(sorted(raw_brand_for_group[normalized_brand])[:5]),
                        "normalized_brand": normalized_brand,
                        "attestation_id_1": left["attestation_id"],
                        "attestation_id_2": right["attestation_id"],
                        "source_ref_1": left["source_ref"],
                        "source_ref_2": right["source_ref"],
                        "source_type_1": left["source_type"],
                        "source_type_2": right["source_type"],
                        "year_1": left["year"],
                        "year_2": right["year"],
                        "similarity": f"{similarity:.4f}",
                    }
                )

    write_csv(args.out_csv, findings)
    affected = len({row["normalized_brand"] for row in findings})
    print(
        f"Found {len(findings)} highly similar cross-source pairs across "
        f"{affected} normalized brand groups. Output: {args.out_csv}"
    )


if __name__ == "__main__":
    main()
