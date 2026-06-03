#!/usr/bin/env python3
"""Audit whether the evidence corpus is large and balanced enough for inference."""

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


def is_usable(row: dict) -> bool:
    level = (row.get("verification_level") or "verified").strip().lower()
    return level in {"verified", "probable", ""}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--plan", default="data/source_collection_plan_200.csv")
    parser.add_argument("--output-dir", default="outputs/evidence_audit")
    args = parser.parse_args()

    rows = read_csv(Path(args.attestations))
    plan_rows = read_csv(Path(args.plan))
    usable_rows = [row for row in rows if is_usable(row)]

    period_targets = {
        row["period"]: int(row["target_attestations"])
        for row in plan_rows
        if row.get("period") and row.get("target_attestations")
    }

    period_counts = Counter(row.get("period", "") for row in usable_rows)
    source_type_counts = Counter(row.get("source_type", "") for row in usable_rows)
    region_counts = Counter(
        row.get("region", "") or row.get("corridor", "") for row in usable_rows
    )
    unique_sources = {
        row.get("source_url_or_archive_ref")
        or row.get("source_url")
        or row.get("source_name")
        or row.get("source_id")
        for row in usable_rows
    }
    unique_sources.discard("")
    unique_sources.discard(None)

    period_audit = []
    for period, target in period_targets.items():
        count = period_counts.get(period, 0)
        period_audit.append(
            {
                "period": period,
                "usable_attestations": str(count),
                "target_attestations": str(target),
                "coverage_ratio": f"{count / target if target else 0:.3f}",
                "meets_half_quota": "1" if count >= target / 2 else "0",
                "meets_full_quota": "1" if count >= target else "0",
            }
        )

    output_dir = Path(args.output_dir)
    write_csv(
        output_dir / "period_quota_audit.csv",
        period_audit,
        [
            "period",
            "usable_attestations",
            "target_attestations",
            "coverage_ratio",
            "meets_half_quota",
            "meets_full_quota",
        ],
    )

    def counter_rows(counter: Counter) -> list[dict]:
        return [
            {"key": key or "UNKNOWN", "usable_attestations": str(value)}
            for key, value in counter.most_common()
        ]

    write_csv(
        output_dir / "source_type_counts.csv",
        counter_rows(source_type_counts),
        ["key", "usable_attestations"],
    )
    write_csv(
        output_dir / "region_counts.csv",
        counter_rows(region_counts),
        ["key", "usable_attestations"],
    )

    total_target = sum(period_targets.values())
    usable_total = len(usable_rows)
    all_periods_half = all(
        int(row["meets_half_quota"]) for row in period_audit
    ) if period_audit else False
    summary = [
        {
            "metric": "usable_attestations",
            "value": str(usable_total),
            "target": "200",
            "passes": "1" if usable_total >= 200 else "0",
        },
        {
            "metric": "unique_sources",
            "value": str(len(unique_sources)),
            "target": "100",
            "passes": "1" if len(unique_sources) >= 100 else "0",
        },
        {
            "metric": "period_target_total",
            "value": str(total_target),
            "target": str(total_target),
            "passes": "1",
        },
        {
            "metric": "all_periods_half_quota",
            "value": "1" if all_periods_half else "0",
            "target": "1",
            "passes": "1" if all_periods_half else "0",
        },
        {
            "metric": "inference_ready",
            "value": "1" if usable_total >= 200 and all_periods_half else "0",
            "target": "1",
            "passes": "1" if usable_total >= 200 and all_periods_half else "0",
        },
    ]
    write_csv(output_dir / "summary.csv", summary, ["metric", "value", "target", "passes"])


if __name__ == "__main__":
    main()
