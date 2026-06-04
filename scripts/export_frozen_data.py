#!/usr/bin/env python3
"""Export thesis-ready frozen corpus tables and aggregate binding indices."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export frozen thesis data products.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--target-analysis", default="")
    parser.add_argument("--out-dir", default="frozen_data_v2")
    return parser.parse_args()


def load_rows(path: str) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def parse_float(value: str | None, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except ValueError:
        return default


def parse_year(value: str | None) -> int | None:
    try:
        return int(float(value or ""))
    except ValueError:
        return None


def raw_binding(row: dict[str, str]) -> float:
    if row.get("historical_binding_raw"):
        return parse_float(row.get("historical_binding_raw"), 0.0)
    weight = parse_float(row.get("analysis_weight"), 1.0)
    weighted = parse_float(row.get("weighted_historical_binding"), 0.0)
    if weight > 0 and weighted <= weight:
        return weighted / weight
    return weighted


def weighted_mean(rows: list[dict[str, str]]) -> tuple[float, float, int]:
    sum_w = 0.0
    sum_b = 0.0
    for row in rows:
        weight = parse_float(row.get("analysis_weight"), 1.0)
        binding = raw_binding(row)
        sum_w += weight
        sum_b += binding * weight
    return (sum_b / sum_w if sum_w else 0.0, sum_w, len(rows))


def write_grouped(rows: list[dict[str, str]], group_fields: list[str], out_csv: Path) -> None:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = tuple((row.get(field) or "unknown") for field in group_fields)
        groups[key].append(row)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        fields = group_fields + ["weighted_binding_index", "weight_sum", "row_count"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for key in sorted(groups):
            index, weight_sum, count = weighted_mean(groups[key])
            writer.writerow(
                {
                    **{field: value for field, value in zip(group_fields, key)},
                    "weighted_binding_index": f"{index:.6f}",
                    "weight_sum": f"{weight_sum:.4f}",
                    "row_count": str(count),
                }
            )


def write_year_corridor(rows: list[dict[str, str]], out_csv: Path) -> None:
    groups: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        year = parse_year(row.get("year"))
        if year is None:
            continue
        groups[(year, row.get("corridor") or "unknown")].append(row)

    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        fields = ["year", "corridor", "weighted_binding_index", "weight_sum", "row_count"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for (year, corridor) in sorted(groups):
            index, weight_sum, count = weighted_mean(groups[(year, corridor)])
            writer.writerow(
                {
                    "year": year,
                    "corridor": corridor,
                    "weighted_binding_index": f"{index:.6f}",
                    "weight_sum": f"{weight_sum:.4f}",
                    "row_count": str(count),
                }
            )


def write_target_grouped(path: str, out_dir: Path) -> dict[str, object]:
    if not path or not Path(path).exists():
        return {"target_analysis_exported": False}

    _, rows = load_rows(path)
    write_grouped(rows, ["period", "corridor", "target_control_type"], out_dir / "target_binding_by_period_corridor_type.csv")
    write_year_corridor(rows, out_dir / "target_binding_by_year_corridor.csv")
    shutil.copy(path, out_dir / "target_binding_analysis_frozen.csv")
    return {
        "target_analysis_exported": True,
        "target_analysis_rows": len(rows),
        "target_control_distribution": dict(Counter((row.get("target_control_type") or "unknown") for row in rows)),
    }


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fields, rows = load_rows(args.attestations)
    shutil.copy(args.attestations, out_dir / "attestations_frozen.csv")

    write_year_corridor(rows, out_dir / "binding_by_year_corridor.csv")
    write_grouped(rows, ["period", "corridor"], out_dir / "binding_by_period_corridor.csv")
    write_grouped(rows, ["period", "corridor", "authority_level"], out_dir / "binding_by_period_corridor_authority.csv")
    write_grouped(rows, ["period", "corridor", "source_type"], out_dir / "binding_by_period_corridor_source_type.csv")

    target_summary = write_target_grouped(args.target_analysis, out_dir)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "attestations": args.attestations,
        "records": len(rows),
        "fields": len(fields),
        "out_dir": str(out_dir),
        "authority_distribution": dict(Counter((row.get("authority_level") or "missing") for row in rows).most_common()),
        "corridor_distribution": dict(Counter((row.get("corridor") or "unknown") for row in rows).most_common()),
        "period_distribution": dict(Counter((row.get("period") or "unknown") for row in rows).most_common()),
        **target_summary,
    }
    (out_dir / "freeze_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Frozen data exported to {out_dir}")
    print(f"Records={len(rows)}")
    print("Files: attestations_frozen.csv, binding_by_year_corridor.csv, binding_by_period_corridor.csv, freeze_manifest.json")


if __name__ == "__main__":
    main()
