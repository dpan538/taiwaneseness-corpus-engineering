#!/usr/bin/env python3
"""Validate harvested/merged attestation records for basic data quality."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REQUIRED_FIELDS = ("year", "original_text", "dish_marker", "taiwan_marker", "source_url")


def source_ref(row: dict) -> str:
    return (row.get("source_url") or row.get("source_url_or_archive_ref") or "").strip()


def artifact_key(row: dict) -> tuple[str, str, str, str]:
    return (
        source_ref(row).lower().rstrip("/"),
        (row.get("year") or "").strip(),
        (row.get("brand_or_category") or "").strip().lower(),
        (row.get("attestation_type") or "").strip().lower(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate harvested record quality.")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--out-report", default="reports/record_quality_report.csv")
    parser.add_argument("--out-json", default="reports/record_quality.json")
    args = parser.parse_args()

    with Path(args.input_csv).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    n = len(rows)
    if n == 0:
        summary = {"total_records": 0, "quality_grade": "empty"}
    else:
        missing_counts = {}
        for field in REQUIRED_FIELDS:
            if field not in fieldnames:
                missing_counts[field] = n
            elif field == "source_url":
                missing_counts[field] = sum(1 for row in rows if not source_ref(row))
            else:
                missing_counts[field] = sum(1 for row in rows if not (row.get(field) or "").strip())

        refs = [source_ref(row).lower().rstrip("/") for row in rows if source_ref(row)]
        ref_counts = Counter(refs)
        duplicate_url_groups = sum(1 for count in ref_counts.values() if count > 1)
        duplicate_url_ratio = duplicate_url_groups / len(ref_counts) if ref_counts else 0.0

        invalid_years = 0
        for row in rows:
            try:
                year = int((row.get("year") or "").strip())
                if year < 1940 or year > 2026:
                    invalid_years += 1
            except ValueError:
                invalid_years += 1

        key_counts = Counter(artifact_key(row) for row in rows if artifact_key(row)[0])
        duplicate_artifact_groups = sum(1 for count in key_counts.values() if count > 1)

        split_counts = Counter(
            (
                source_ref(row).lower().rstrip("/"),
                (row.get("year") or "").strip(),
                (row.get("brand_or_category") or "").strip().lower(),
            )
            for row in rows
            if source_ref(row)
        )
        suspicious_split_groups = sum(1 for count in split_counts.values() if count > 1)

        source_types = Counter(row.get("source_type") or "unknown" for row in rows)
        corridors = Counter(row.get("corridor") or "unknown" for row in rows)
        source_names = Counter(row.get("source_name") or row.get("source_id") or "unknown" for row in rows)

        hard_fail = (
            missing_counts["year"] / n > 0.1
            or invalid_years / n > 0.1
            or duplicate_artifact_groups > 0
            or suspicious_split_groups > n * 0.05
        )
        warning = duplicate_url_ratio > 0.05 or missing_counts["original_text"] / n > 0.2
        grade = "C" if hard_fail else "B" if warning else "A"

        summary = {
            "input_csv": args.input_csv,
            "total_records": n,
            "missing_fields": missing_counts,
            "unique_source_refs": len(ref_counts),
            "duplicate_url_groups": duplicate_url_groups,
            "duplicate_url_ratio": round(duplicate_url_ratio, 4),
            "duplicate_artifact_groups": duplicate_artifact_groups,
            "suspicious_split_groups": suspicious_split_groups,
            "invalid_year_count": invalid_years,
            "invalid_year_ratio": round(invalid_years / n, 4),
            "source_type_distribution": dict(source_types.most_common(12)),
            "corridor_distribution": dict(corridors.most_common(12)),
            "top_source_names": dict(source_names.most_common(12)),
            "quality_grade": grade,
        }

    Path(args.out_report).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_json).open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    with Path(args.out_report).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        for key, value in summary.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    writer.writerow([f"{key}.{subkey}", subvalue])
            else:
                writer.writerow([key, value])

    print(f"Record quality summary: grade {summary['quality_grade']}, records={summary['total_records']}")


if __name__ == "__main__":
    main()
