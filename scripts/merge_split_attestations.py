#!/usr/bin/env python3
"""Merge split attestations back to one row per source artifact.

The evidence unit is a source artifact, not an extracted marker. Rows that share
the same source URL/archive ref, date-or-year, and brand/category are therefore
collapsed into a single attestation with merged marker fields.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path


LEVEL_RANK = {"rejected": 0, "candidate": 1, "probable": 2, "verified": 3, "": 3}
CONFIDENCE_RANK = {"low": 1, "medium": 2, "high": 3}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--strong-date-key",
        action="store_true",
        help="Use exact date when present; otherwise year. This is the default evidence-unit key.",
    )
    return parser.parse_args()


def read_rows(path: str) -> tuple[list[str], list[dict]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def artifact_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def date_key(row: dict, strong_date_key: bool) -> str:
    if strong_date_key:
        return (row.get("date") or row.get("year") or "").strip()
    return (row.get("date") or row.get("year") or "").strip()


def group_key(row: dict, strong_date_key: bool) -> tuple[str, str, str]:
    return (
        artifact_ref(row),
        date_key(row, strong_date_key),
        (row.get("brand_or_category") or row.get("brand") or "").strip(),
    )


def split_values(value: str) -> list[str]:
    out: list[str] = []
    for sep in ("|", ";"):
        value = value.replace(sep, ";")
    for item in value.split(";"):
        item = item.strip()
        if item and item not in out:
            out.append(item)
    return out


def merge_unique(values: list[str], sep: str = ";") -> str:
    seen: list[str] = []
    for value in values:
        for item in split_values(value or ""):
            if item not in seen:
                seen.append(item)
    return sep.join(seen)


def merge_text(values: list[str], sep: str = " || ") -> str:
    seen: list[str] = []
    for value in values:
        value = (value or "").strip()
        if value and value not in seen:
            seen.append(value)
    return sep.join(seen)


def best_by_rank(rows: list[dict], field: str, rank: dict[str, int]) -> str:
    best = ""
    best_rank = -1
    for row in rows:
        value = (row.get(field) or "").strip().lower()
        value_rank = rank.get(value, 0)
        if value_rank > best_rank:
            best = row.get(field) or ""
            best_rank = value_rank
    return best


def stable_hash(value: str, length: int = 12) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def merge_group(rows: list[dict], fields: list[str], strong_date_key: bool) -> dict:
    first = dict(rows[0])
    ref, date_or_year, brand = group_key(first, strong_date_key)
    first["source_url"] = first.get("source_url") or first.get("source_url_or_archive_ref") or ref
    first["source_url_or_archive_ref"] = first.get("source_url_or_archive_ref") or first.get("source_url") or ref
    first["brand_or_category"] = first.get("brand_or_category") or brand

    first["attestation_type"] = merge_unique([r.get("attestation_type", "") for r in rows], sep="|")
    first["dish_marker"] = merge_unique(
        [r.get("dish_marker", "") or r.get("matched_dish_markers", "") for r in rows],
        sep=";",
    )
    first["taiwan_marker"] = merge_unique(
        [r.get("taiwan_marker", "") or r.get("matched_taiwan_markers", "") for r in rows],
        sep=";",
    )
    first["original_text"] = merge_text([r.get("original_text", "") for r in rows])
    first["text_for_scoring"] = merge_text([r.get("text_for_scoring", "") for r in rows])
    first["notes"] = merge_text([r.get("notes", "") for r in rows])
    first["verification_level"] = best_by_rank(rows, "verification_level", LEVEL_RANK)
    first["confidence"] = best_by_rank(rows, "confidence", CONFIDENCE_RANK)

    dedupe_basis = "|".join([ref, date_or_year, brand])
    first["dedupe_key"] = stable_hash(dedupe_basis, 16)
    source_hint = first.get("source_id") or "SRC"
    first["attestation_id"] = f"MERGED_{stable_hash(source_hint + '|' + dedupe_basis, 14)}"
    first["merged_from_attestation_ids"] = merge_unique([r.get("attestation_id", "") for r in rows], sep=";")
    first["merged_row_count"] = str(len(rows))

    for field in fields:
        first.setdefault(field, "")
    return first


def main() -> None:
    args = parse_args()
    fields, rows = read_rows(args.input)
    if not rows:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.output).open("w", encoding="utf-8", newline="") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()
        print(f"merged_rows=0 output={args.output}")
        return

    for extra in ["dedupe_key", "merged_from_attestation_ids", "merged_row_count"]:
        if extra not in fields:
            fields.append(extra)

    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    singletons: list[dict] = []
    for row in rows:
        key = group_key(row, args.strong_date_key)
        if all(key):
            groups[key].append(row)
        else:
            singletons.append(row)

    merged_rows = [merge_group(group, fields, args.strong_date_key) for _, group in sorted(groups.items())]
    for row in singletons:
        row = dict(row)
        row["source_url"] = row.get("source_url") or row.get("source_url_or_archive_ref") or ""
        row["source_url_or_archive_ref"] = row.get("source_url_or_archive_ref") or row.get("source_url") or ""
        row.setdefault("dedupe_key", stable_hash("|".join([artifact_ref(row), row.get("year", ""), row.get("brand_or_category", "")]), 16))
        row.setdefault("merged_from_attestation_ids", row.get("attestation_id", ""))
        row.setdefault("merged_row_count", "1")
        merged_rows.append(row)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(merged_rows)

    print(f"merged_rows={len(rows)} unique_attestations={len(merged_rows)} output={args.output}")


if __name__ == "__main__":
    main()
