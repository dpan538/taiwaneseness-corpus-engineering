#!/usr/bin/env python3
"""Deduplicate attestation rows with source-artifact keys."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def artifact_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def dedupe_key(row: dict) -> str:
    basis = "|".join(
        [
            artifact_ref(row),
            (row.get("date") or row.get("year") or "").strip(),
            (row.get("brand_or_category") or row.get("brand") or "").strip(),
        ]
    )
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def main() -> None:
    args = parse_args()
    with Path(args.input).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)

    if "dedupe_key" not in fields:
        fields.append("dedupe_key")

    seen: set[str] = set()
    deduped: list[dict] = []
    for row in rows:
        row["source_url"] = row.get("source_url") or row.get("source_url_or_archive_ref") or ""
        row["source_url_or_archive_ref"] = row.get("source_url_or_archive_ref") or row.get("source_url") or ""
        key = row.get("dedupe_key") or dedupe_key(row)
        row["dedupe_key"] = key
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(deduped)

    print(f"deduped_rows={len(rows)} unique_rows={len(deduped)} output={args.output}")


if __name__ == "__main__":
    main()
