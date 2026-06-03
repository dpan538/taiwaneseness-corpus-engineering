#!/usr/bin/env python3
"""Detect corpus anomalies before downstream analysis.

This supervisor script complements the health audit. It checks for source
artifact duplicates, missed split merges, source concentration, missing fields,
year outliers, marker quality issues, and verification-confidence mismatches.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


SOURCE_CONCENTRATION_WARN = 0.10
SIMILARITY_THRESHOLD = 95
MIN_YEAR = 1900
MAX_YEAR = 2026
MIN_TEXT_LEN = 5

REQUIRED_FIELDS = [
    "attestation_id",
    "source_id",
    "year",
    "period",
    "corridor",
    "dish_marker",
    "taiwan_marker",
    "verification_level",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect duplicate, split, and quality anomalies in attestation CSVs.")
    parser.add_argument("--attestations", default="data/harvested/combined_attestations_working.csv")
    parser.add_argument("--owners", default="")
    parser.add_argument("--out-csv", default="reports/anomaly_report.csv")
    parser.add_argument("--out-md", default="reports/anomaly_report.md")
    parser.add_argument("--out-alerts", default="reports/anomaly_alerts.json")
    parser.add_argument("--fuzzy", action="store_true", help="Enable slower fuzzy duplicate checks over original_text.")
    parser.add_argument("--source-threshold", type=float, default=SOURCE_CONCENTRATION_WARN)
    parser.add_argument("--similarity-threshold", type=int, default=SIMILARITY_THRESHOLD)
    return parser.parse_args()


def read_csv(path: str) -> tuple[list[str], list[dict]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: str, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else ["status"]
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def detail_path(out_csv: str, suffix: str) -> str:
    path = Path(out_csv)
    return str(path.with_name(f"{path.stem}_{suffix}{path.suffix}"))


def source_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def artifact_key(row: dict) -> tuple[str, str, str]:
    return (
        source_ref(row),
        (row.get("date") or row.get("year") or "").strip(),
        (row.get("brand_or_category") or row.get("brand") or "").strip(),
    )


def strict_duplicate_key(row: dict) -> tuple[str, str, str, str, str]:
    return (
        source_ref(row),
        (row.get("year") or "").strip(),
        (row.get("brand_or_category") or "").strip(),
        (row.get("dish_marker") or "").strip(),
        (row.get("taiwan_marker") or "").strip(),
    )


def numeric_year(row: dict) -> int | None:
    try:
        return int(float(row.get("year") or ""))
    except ValueError:
        return None


def confidence_rank(value: str) -> float | None:
    value = (value or "").strip().lower()
    if not value:
        return None
    if value in {"low", "candidate"}:
        return 0.25
    if value in {"medium", "probable"}:
        return 0.6
    if value in {"high", "verified"}:
        return 0.9
    try:
        return float(value)
    except ValueError:
        return None


def rows_for_duplicate_keys(rows: list[dict], key_func) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = key_func(row)
        if key[0]:
            buckets[key].append(row)
    out: list[dict] = []
    for key, group in sorted(buckets.items()):
        if len(group) <= 1:
            continue
        for row in group:
            item = dict(row)
            item["duplicate_group_key"] = "|".join(str(part) for part in key)
            item["duplicate_group_count"] = str(len(group))
            out.append(item)
    return out


def suspicious_split_groups(rows: list[dict]) -> list[dict]:
    counts = Counter(artifact_key(row) for row in rows if artifact_key(row)[0])
    out = []
    for key, count in sorted(counts.items()):
        if count > 1:
            out.append(
                {
                    "source_ref": key[0],
                    "date_or_year": key[1],
                    "brand_or_category": key[2],
                    "count": str(count),
                }
            )
    return out


def field_missing_counts(fields: list[str], rows: list[dict]) -> dict[str, int]:
    missing = {}
    for field in REQUIRED_FIELDS:
        if field not in fields:
            missing[field] = len(rows)
        else:
            missing[field] = sum(1 for row in rows if not (row.get(field) or "").strip())
    return missing


def year_outliers(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        year = numeric_year(row)
        if year is None or year < MIN_YEAR or year > MAX_YEAR:
            out.append(
                {
                    "attestation_id": row.get("attestation_id", ""),
                    "year": row.get("year", ""),
                    "source_url": source_ref(row),
                }
            )
    return out


def marker_issues(rows: list[dict]) -> list[dict]:
    issues = []
    for row in rows:
        for field in ("dish_marker", "taiwan_marker"):
            value = row.get(field, "")
            if not value:
                continue
            if len(value) < 2:
                issue = "too_short"
            elif len(value) > 200:
                issue = "too_long"
            elif re.search(r"[^\w\s;:：/、，。！？\-\u4e00-\u9fff\u3040-\u30ff]", value):
                issue = "special_char"
            else:
                continue
            issues.append(
                {
                    "attestation_id": row.get("attestation_id", ""),
                    "field": field,
                    "issue": issue,
                    "value": value[:120],
                }
            )
    return issues


def source_concentration(rows: list[dict], threshold: float) -> list[dict]:
    total = len(rows)
    if not total:
        return []
    counts = Counter(source_ref(row) for row in rows if source_ref(row))
    out = []
    for source, count in counts.most_common():
        ratio = count / total
        if ratio <= threshold:
            continue
        out.append({"source_ref": source, "count": str(count), "ratio": f"{ratio:.4f}"})
    return out


def verification_distribution(rows: list[dict]) -> list[dict]:
    total = len(rows)
    counts = Counter((row.get("verification_level") or "").strip() for row in rows)
    return [
        {"level": level or "(blank)", "count": str(count), "ratio": f"{count / total:.4f}" if total else "0.0000"}
        for level, count in counts.most_common()
    ]


def low_confidence_verified(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        level = (row.get("verification_level") or "").strip().lower()
        confidence = confidence_rank(row.get("confidence", ""))
        if level == "verified" and confidence is not None and confidence < 0.5:
            out.append(row)
    return out


def low_confidence_probable(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        level = (row.get("verification_level") or "").strip().lower()
        confidence = confidence_rank(row.get("confidence", ""))
        if level in {"verified", "probable"} and confidence is not None and confidence < 0.5:
            out.append(row)
    return out


def text_quality_issues(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        text = (row.get("original_text") or row.get("text_for_scoring") or "").strip()
        if len(text) < MIN_TEXT_LEN:
            out.append(
                {
                    "attestation_id": row.get("attestation_id", ""),
                    "issue": "text_too_short",
                    "text": text,
                }
            )
    return out


def fuzzy_duplicates(rows: list[dict], threshold: int) -> list[dict]:
    sample = rows[:2000]
    out = []
    for idx, row in enumerate(sample):
        text = (row.get("original_text") or "").strip()
        if not text:
            continue
        for other in sample[idx + 1 : min(idx + 100, len(sample))]:
            other_text = (other.get("original_text") or "").strip()
            if not other_text:
                continue
            ratio = difflib.SequenceMatcher(None, text, other_text).ratio() * 100
            if ratio >= threshold:
                out.append(
                    {
                        "id1": row.get("attestation_id", ""),
                        "id2": other.get("attestation_id", ""),
                        "similarity": f"{ratio:.2f}",
                    }
                )
    return out


def markdown_table(rows: list[dict], fields: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    fields, rows = read_csv(args.attestations)

    exact_dups = rows_for_duplicate_keys(rows, strict_duplicate_key)
    split_suspect = suspicious_split_groups(rows)
    missing_fields = field_missing_counts(fields, rows)
    outlier_rows = year_outliers(rows)
    marker_rows = marker_issues(rows)
    concentration_rows = source_concentration(rows, args.source_threshold)
    low_verified_rows = low_confidence_verified(rows)
    low_probable_rows = low_confidence_probable(rows)
    short_text_rows = text_quality_issues(rows)
    fuzzy_rows = fuzzy_duplicates(rows, args.similarity_threshold) if args.fuzzy else []
    verification_rows = verification_distribution(rows)

    report = {
        "total_rows": len(rows),
        "exact_duplicate_rows": len(exact_dups),
        "suspicious_split_groups": len(split_suspect),
        "year_outliers": len(outlier_rows),
        "marker_issues": len(marker_rows),
        "high_concentration_sources": len(concentration_rows),
        "low_conf_verified_rows": len(low_verified_rows),
        "low_conf_probable_rows": len(low_probable_rows),
        "short_text_rows": len(short_text_rows),
        "fuzzy_duplicate_pairs": len(fuzzy_rows),
    }

    write_csv(args.out_csv, [report], list(report.keys()))
    details = [
        ("exact_dups", exact_dups),
        ("suspicious_split", split_suspect),
        ("year_outliers", outlier_rows),
        ("marker_issues", marker_rows),
        ("source_concentration", concentration_rows),
        ("low_conf_verified", low_verified_rows),
        ("low_conf_probable", low_probable_rows),
        ("short_text", short_text_rows),
        ("fuzzy_dups", fuzzy_rows),
    ]
    for suffix, detail_rows in details:
        write_csv(detail_path(args.out_csv, suffix), detail_rows)

    critical_keys = [
        "exact_duplicate_rows",
        "suspicious_split_groups",
        "year_outliers",
        "marker_issues",
        "low_conf_verified_rows",
        "short_text_rows",
    ]
    warning_keys = ["high_concentration_sources", "low_conf_probable_rows", "fuzzy_duplicate_pairs"]
    critical_alerts = {key: report[key] for key in critical_keys if report[key] > 0}
    warning_alerts = {key: report[key] for key in warning_keys if report[key] > 0}
    alerts = {
        "has_critical": bool(critical_alerts),
        "has_warnings": bool(warning_alerts),
        "has_alerts": bool(critical_alerts or warning_alerts),
        "critical": critical_alerts,
        "warnings": warning_alerts,
    }

    md = (
        "# Corpus Anomaly Report\n\n"
        f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n"
        "## Summary\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in report.items())
        + "\n\n## Field Completeness\n\n"
        + markdown_table(
            [{"field": field, "missing_count": missing} for field, missing in missing_fields.items()],
            ["field", "missing_count"],
        )
        + "\n## Verification Level Distribution\n\n"
        + markdown_table(verification_rows, ["level", "count", "ratio"])
        + "\n## Detailed Files\n\n"
        + "\n".join(f"- {suffix}: `{detail_path(args.out_csv, suffix)}`" for suffix, _ in details)
        + "\n\n## Recommendations\n\n"
    )
    if critical_alerts.get("exact_duplicate_rows"):
        md += "- Run `scripts/dedupe_attestations.py` before downstream analysis.\n"
    if critical_alerts.get("suspicious_split_groups"):
        md += "- Run `scripts/merge_split_attestations.py` before downstream analysis.\n"
    if critical_alerts.get("year_outliers"):
        md += "- Manually review year outliers and correct or mark them invalid.\n"
    if critical_alerts.get("marker_issues"):
        md += "- Review marker fields for garbage characters or overly long strings.\n"
    if warning_alerts.get("high_concentration_sources"):
        md += "- Add source-diverse records or downweight concentrated sources in interpretation.\n"
    if warning_alerts.get("low_conf_probable_rows"):
        md += "- Review low-confidence probable rows and demote if needed.\n"
    if not critical_alerts and not warning_alerts:
        md += "- No anomalies detected.\n"

    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text(md, encoding="utf-8")
    Path(args.out_alerts).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_alerts).write_text(json.dumps(alerts, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"out_csv": args.out_csv, "out_md": args.out_md, "alerts": alerts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
