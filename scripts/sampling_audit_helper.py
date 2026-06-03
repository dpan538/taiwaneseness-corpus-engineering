#!/usr/bin/env python3
"""Build a deterministic manual audit queue for corpus spot checks."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path


SUSPECT_SOURCE_TYPES = {"personal_blog", "review_platform", "blog", "social_media", "forum"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a prioritized manual audit queue.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--low-confidence-only", action="store_true")
    parser.add_argument("--seed", type=int, default=20260603)
    parser.add_argument("--out-csv", default="reports/audit_sampling_queue.csv")
    return parser.parse_args()


def read_rows(path: str) -> tuple[list[str], list[dict]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def confidence_score(value: str) -> float | None:
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


def source_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def parse_year(row: dict) -> int | None:
    try:
        return int(float(row.get("year") or ""))
    except ValueError:
        return None


def add_candidate(queue: dict[str, dict], row: dict, reason: str, priority: int) -> None:
    attestation_id = row.get("attestation_id") or source_ref(row) or str(id(row))
    item = queue.get(attestation_id, dict(row))
    existing_reason = item.get("audit_reason", "")
    reasons = [part for part in existing_reason.split("; ") if part]
    if reason not in reasons:
        reasons.append(reason)
    item["audit_reason"] = "; ".join(reasons)
    old_priority = int(item.get("audit_priority", "0") or "0")
    item["audit_priority"] = str(max(old_priority, priority))
    queue[attestation_id] = item


def main() -> None:
    args = parse_args()
    fieldnames, rows = read_rows(args.attestations)
    rng = random.Random(args.seed)

    year_counts = Counter(parse_year(row) for row in rows if parse_year(row) is not None)
    brand_counts = Counter((row.get("brand_or_category") or "").strip() for row in rows)
    source_counts = Counter(source_ref(row) for row in rows if source_ref(row))

    queue: dict[str, dict] = {}
    for row in rows:
        score = confidence_score(row.get("confidence", ""))
        level = (row.get("verification_level") or "").strip().lower()
        source_type = (row.get("source_type") or "").strip().lower()
        year = parse_year(row)
        brand = (row.get("brand_or_category") or "").strip()
        ref = source_ref(row)

        if score is None or score < 0.5:
            add_candidate(queue, row, "low_confidence", 90)
        if level == "verified" and source_type in SUSPECT_SOURCE_TYPES:
            add_candidate(queue, row, "verified_but_suspect_source_type", 85)
        if year is not None and year_counts[year] <= 2:
            add_candidate(queue, row, "rare_year", 70)
        if brand and brand_counts[brand] == 1:
            add_candidate(queue, row, "single_record_brand", 55)
        if ref and source_counts[ref] >= 20:
            add_candidate(queue, row, "highly_reused_source_artifact", 65)

    if args.low_confidence_only:
        queue = {key: row for key, row in queue.items() if "low_confidence" in row.get("audit_reason", "")}

    remaining = [row for row in rows if (row.get("attestation_id") or source_ref(row) or str(id(row))) not in queue]
    rng.shuffle(remaining)
    for row in remaining:
        if len(queue) >= args.sample_size:
            break
        add_candidate(queue, row, "deterministic_random_sample", 10)

    final = sorted(queue.values(), key=lambda row: int(row.get("audit_priority", "0") or "0"), reverse=True)[
        : args.sample_size
    ]
    out_fields = ["audit_priority", "audit_reason"] + [field for field in fieldnames if field not in {"audit_priority", "audit_reason"}]
    if not out_fields:
        out_fields = ["audit_priority", "audit_reason"]

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(final)

    reason_counts: defaultdict[str, int] = defaultdict(int)
    for row in final:
        for reason in row.get("audit_reason", "").split("; "):
            if reason:
                reason_counts[reason] += 1
    summary = ", ".join(f"{reason}={count}" for reason, count in sorted(reason_counts.items()))
    print(f"Generated audit queue with {len(final)} records. {summary}. Output: {args.out_csv}")


if __name__ == "__main__":
    main()
