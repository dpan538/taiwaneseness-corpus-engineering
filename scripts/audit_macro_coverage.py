#!/usr/bin/env python3
"""Audit macro-phase corpus coverage."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
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


def year_to_macro(year: int) -> str:
    if 1946 <= year <= 1987:
        return "1946-1987_taiwan_side_formation"
    if 1987 <= year <= 2015:
        return "1987-2015_cross_strait_diffusion"
    if 2015 <= year <= 2025:
        return "2015-2025_internet_wanghong_capital"
    return "outside_macro_scope"


def usable(row: dict) -> bool:
    level = (row.get("verification_level") or "verified").strip().lower()
    return level in {"verified", "probable", ""}


def row_year(row: dict) -> int | None:
    for field in ("year", "event_year"):
        try:
            return int(float(row.get(field, "")))
        except (TypeError, ValueError):
            continue
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", default="")
    parser.add_argument("--capital-events", default="")
    parser.add_argument("--plan", default="data/macro_collection_plan.csv")
    parser.add_argument("--output-dir", default="outputs/macro_audit")
    args = parser.parse_args()

    rows: list[dict] = []
    if args.attestations:
        rows.extend(read_csv(Path(args.attestations)))
    if args.capital_events:
        rows.extend(read_csv(Path(args.capital_events)))

    plan = {row["macro_phase"]: row for row in read_csv(Path(args.plan))}
    counts: Counter[str] = Counter()
    sources: dict[str, set[str]] = {phase: set() for phase in plan}

    for row in rows:
        if not usable(row):
            continue
        year = row_year(row)
        if year is None:
            continue
        phase = year_to_macro(year)
        counts[phase] += 1
        source_key = (
            row.get("source_url")
            or row.get("source_url_or_archive_ref")
            or row.get("source_name")
            or row.get("source_id")
            or ""
        )
        if phase in sources and source_key:
            sources[phase].add(source_key)

    audit_rows: list[dict] = []
    for phase, plan_row in plan.items():
        target = int(plan_row["target_records"])
        min_sources = int(plan_row["minimum_unique_sources"])
        count = counts.get(phase, 0)
        source_count = len(sources.get(phase, set()))
        audit_rows.append(
            {
                "macro_phase": phase,
                "records": str(count),
                "target_records": str(target),
                "record_coverage": f"{count / target if target else 0:.3f}",
                "unique_sources": str(source_count),
                "minimum_unique_sources": str(min_sources),
                "source_coverage": f"{source_count / min_sources if min_sources else 0:.3f}",
                "passes_records": "1" if count >= target else "0",
                "passes_sources": "1" if source_count >= min_sources else "0",
            }
        )

    output_dir = Path(args.output_dir)
    write_csv(
        output_dir / "macro_coverage.csv",
        audit_rows,
        [
            "macro_phase",
            "records",
            "target_records",
            "record_coverage",
            "unique_sources",
            "minimum_unique_sources",
            "source_coverage",
            "passes_records",
            "passes_sources",
        ],
    )

    inference_ready = all(
        row["passes_records"] == "1" and row["passes_sources"] == "1"
        for row in audit_rows
    )
    write_csv(
        output_dir / "summary.csv",
        [{"metric": "macro_inference_ready", "value": "1" if inference_ready else "0"}],
        ["metric", "value"],
    )


if __name__ == "__main__":
    main()
