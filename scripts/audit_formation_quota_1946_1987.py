#!/usr/bin/env python3
"""Audit 1946-1987 attestations against the detailed formation quota plan."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def year(row: dict) -> int | None:
    try:
        return int(float(row.get("year", "")))
    except (TypeError, ValueError):
        return None


def usable(row: dict) -> bool:
    level = (row.get("verification_level") or "verified").strip().lower()
    return level in {"", "probable", "verified"}


def norm_place(row: dict) -> str:
    values = [
        row.get("region", ""),
        row.get("corridor", ""),
        row.get("province", ""),
        row.get("city", ""),
        row.get("country_or_area", ""),
    ]
    return " ".join(value for value in values if value).lower()


def source_key(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    )


def in_year_range(value: int, range_text: str) -> bool:
    start_text, end_text = range_text.split("-", 1)
    return int(start_text) <= value <= int(end_text)


def quota_id_for(row: dict, quota_rows: list[dict]) -> str:
    y = year(row)
    if y is None:
        return "UNCLASSIFIED"
    place = norm_place(row)

    if "taiwan-side" in place or "taipei" in place or "taiwan" in place:
        for quota in quota_rows:
            if quota["region"] == "Taiwan-side" and in_year_range(y, quota["years"]):
                return quota["quota_id"]

    region_map = [
        ("Mainland China", ["mainland", "china", "beijing", "shanghai"]),
        ("Japan", ["japan", "tokyo", "nagoya", "nagasaki", "aichi", "shinjuku"]),
        ("Singapore", ["singapore", "newspapersg", "straits times", "business times", "new nation"]),
        ("Vietnam", ["vietnam"]),
        ("South Korea", ["korea", "seoul"]),
        ("North America", ["north america", "united states", "canada", "new york", "flushing"]),
        ("Latin America", ["latin america"]),
    ]
    for region, markers in region_map:
        if any(marker in place for marker in markers):
            for quota in quota_rows:
                if quota["region"] == region and in_year_range(y, quota["years"]):
                    return quota["quota_id"]

    return "UNCLASSIFIED"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--plan", default="data/formation_1946_1987_quota_plan.csv")
    parser.add_argument("--output-dir", default="outputs/formation_quota_audit")
    args = parser.parse_args()

    quota_rows = read_csv(Path(args.plan))
    rows = [
        row
        for row in read_csv(Path(args.attestations))
        if usable(row) and (year(row) is not None) and 1946 <= year(row) <= 1987
    ]

    counts: Counter[str] = Counter()
    sources: dict[str, set[str]] = defaultdict(set)
    examples: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        qid = quota_id_for(row, quota_rows)
        counts[qid] += 1
        key = source_key(row)
        if key:
            sources[qid].add(key)
        if len(examples[qid]) < 5:
            examples[qid].append(row.get("attestation_id", ""))

    audit_rows: list[dict] = []
    for quota in quota_rows:
        qid = quota["quota_id"]
        target = int(quota["target_records"])
        min_sources = int(quota["minimum_unique_sources"])
        count = counts.get(qid, 0)
        source_count = len(sources.get(qid, set()))
        audit_rows.append(
            {
                "quota_id": qid,
                "region": quota["region"],
                "years": quota["years"],
                "records": str(count),
                "target_records": str(target),
                "record_coverage": f"{count / target if target else 0:.3f}",
                "unique_sources": str(source_count),
                "minimum_unique_sources": str(min_sources),
                "source_coverage": f"{source_count / min_sources if min_sources else 0:.3f}",
                "example_attestation_ids": ";".join(value for value in examples.get(qid, []) if value),
            }
        )

    if counts.get("UNCLASSIFIED"):
        audit_rows.append(
            {
                "quota_id": "UNCLASSIFIED",
                "region": "UNCLASSIFIED",
                "years": "1946-1987",
                "records": str(counts["UNCLASSIFIED"]),
                "target_records": "0",
                "record_coverage": "0.000",
                "unique_sources": str(len(sources.get("UNCLASSIFIED", set()))),
                "minimum_unique_sources": "0",
                "source_coverage": "0.000",
                "example_attestation_ids": ";".join(examples.get("UNCLASSIFIED", [])),
            }
        )

    output_dir = Path(args.output_dir)
    write_csv(
        output_dir / "quota_coverage.csv",
        audit_rows,
        [
            "quota_id",
            "region",
            "years",
            "records",
            "target_records",
            "record_coverage",
            "unique_sources",
            "minimum_unique_sources",
            "source_coverage",
            "example_attestation_ids",
        ],
    )
    write_csv(
        output_dir / "summary.csv",
        [
            {"metric": "usable_1946_1987_records", "value": str(len(rows))},
            {"metric": "quota_target_records", "value": str(sum(int(row["target_records"]) for row in quota_rows))},
            {"metric": "unclassified_records", "value": str(counts.get("UNCLASSIFIED", 0))},
        ],
        ["metric", "value"],
    )


if __name__ == "__main__":
    main()
