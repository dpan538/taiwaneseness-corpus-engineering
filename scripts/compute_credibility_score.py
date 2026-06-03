#!/usr/bin/env python3
"""Compute per-row and aggregate corpus credibility scores."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute reproducible credibility scores.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--out-per-row", default="reports/credibility_per_row.csv")
    parser.add_argument("--out-summary", default="reports/credibility_summary.json")
    parser.add_argument("--out-csv-summary", default="reports/credibility_summary.csv")
    return parser.parse_args()


def read_csv(path: str) -> tuple[list[str], list[dict]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: str, rows: list[dict], fields: list[str]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def verification_weight(level: str) -> float:
    return {
        "verified": 1.0,
        "probable": 0.7,
        "candidate": 0.3,
        "rejected": 0.0,
        "": 0.7,
    }.get((level or "").strip().lower(), 0.3)


def authority_weight(row: dict) -> float:
    if row.get("authority_weight"):
        return float_value(row.get("authority_weight"), 0.5)
    return {
        "primary": 1.0,
        "secondary": 0.7,
        "tertiary": 0.4,
    }.get((row.get("authority_level") or "secondary").strip().lower(), 0.5)


def confidence_weight(value: str) -> float:
    value = (value or "").strip().lower()
    if value in {"high", "verified"}:
        return 0.9
    if value in {"medium", "probable"}:
        return 0.65
    if value in {"low", "candidate"}:
        return 0.3
    return float_value(value, 0.5)


def float_value(value: str, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def corroboration_key(row: dict) -> tuple[str, str, str]:
    return (
        (row.get("brand_or_category") or row.get("brand") or "").strip().lower(),
        (row.get("year") or "").strip(),
        (row.get("period") or "").strip(),
    )


def corroboration_score(distinct_sources: int) -> float:
    if distinct_sources <= 1:
        return 0.0
    # Log-like saturation: 2 sources=0.35, 3=0.70, 4+=1.0.
    return min(1.0, 0.35 * (distinct_sources - 1))


def interpretation(score: float) -> str:
    if score >= 0.75:
        return "strong"
    if score >= 0.65:
        return "good"
    if score >= 0.5:
        return "moderate"
    return "low"


def main() -> None:
    args = parse_args()
    fields, rows = read_csv(args.attestations)

    sources_by_key: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    rows_by_key = Counter()
    for row in rows:
        key = corroboration_key(row)
        rows_by_key[key] += 1
        ref = source_ref(row)
        if ref:
            sources_by_key[key].add(ref)

    scores: list[float] = []
    component_sums = Counter()
    for row in rows:
        v_score = verification_weight(row.get("verification_level", ""))
        a_score = authority_weight(row)
        n_score = max(0.0, min(1.0, float_value(row.get("novelty_score"), 0.5)))
        c_score = confidence_weight(row.get("confidence", ""))
        key = corroboration_key(row)
        distinct_sources = len(sources_by_key.get(key, set()))
        corr_score = corroboration_score(distinct_sources)

        credibility = (
            0.35 * v_score
            + 0.25 * a_score
            + 0.20 * n_score
            + 0.10 * c_score
            + 0.10 * corr_score
        )
        credibility = max(0.0, min(1.0, credibility))

        row["credibility_score"] = f"{credibility:.4f}"
        row["credibility_interpretation"] = interpretation(credibility)
        row["credibility_verification_component"] = f"{v_score:.4f}"
        row["credibility_authority_component"] = f"{a_score:.4f}"
        row["credibility_novelty_component"] = f"{n_score:.4f}"
        row["credibility_confidence_component"] = f"{c_score:.4f}"
        row["credibility_corroboration_component"] = f"{corr_score:.4f}"
        row["corroborating_distinct_sources"] = str(distinct_sources)
        row["corroborating_rows_same_brand_year_period"] = str(rows_by_key[key])

        scores.append(credibility)
        component_sums["verification"] += v_score
        component_sums["authority"] += a_score
        component_sums["novelty"] += n_score
        component_sums["confidence"] += c_score
        component_sums["corroboration"] += corr_score

    out_fields = list(fields)
    for field in (
        "credibility_score",
        "credibility_interpretation",
        "credibility_verification_component",
        "credibility_authority_component",
        "credibility_novelty_component",
        "credibility_confidence_component",
        "credibility_corroboration_component",
        "corroborating_distinct_sources",
        "corroborating_rows_same_brand_year_period",
    ):
        if field not in out_fields:
            out_fields.append(field)
    write_csv(args.out_per_row, rows, out_fields)

    total = len(scores)
    overall = sum(scores) / total if total else 0.0
    sorted_scores = sorted(scores)
    median = sorted_scores[total // 2] if total else 0.0
    if total and total % 2 == 0:
        median = (sorted_scores[total // 2 - 1] + sorted_scores[total // 2]) / 2
    stdev = math.sqrt(sum((score - overall) ** 2 for score in scores) / total) if total else 0.0
    high_ratio = sum(1 for score in scores if score >= 0.7) / total if total else 0.0
    low_ratio = sum(1 for score in scores if score < 0.5) / total if total else 0.0
    credibility_bins = Counter(interpretation(score) for score in scores)

    summary = {
        "overall_credibility_index": round(overall, 4),
        "overall_credibility_percent": round(overall * 100, 2),
        "credibility_interpretation": interpretation(overall),
        "median_credibility": round(median, 4),
        "stdev_credibility": round(stdev, 4),
        "high_credibility_ratio": round(high_ratio, 4),
        "low_credibility_ratio": round(low_ratio, 4),
        "total_records": total,
        "component_means": {
            key: round(component_sums[key] / total, 4) if total else 0.0
            for key in ("verification", "authority", "novelty", "confidence", "corroboration")
        },
        "credibility_bins": dict(sorted(credibility_bins.items())),
        "method_notes": [
            "Corroboration uses distinct source references for the same brand/year/period, not raw row counts.",
            "String confidence values are mapped as high=0.9, medium=0.65, low=0.3.",
            "Missing novelty defaults to 0.5; missing authority defaults to secondary-like 0.5-0.7 depending on fields.",
        ],
    }

    Path(args.out_summary).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_summary).open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    csv_summary_rows = []
    for key, value in summary.items():
        if isinstance(value, (dict, list)):
            continue
        csv_summary_rows.append({"metric": key, "value": value})
    for key, value in summary["component_means"].items():
        csv_summary_rows.append({"metric": f"component_mean_{key}", "value": value})
    for key, value in summary["credibility_bins"].items():
        csv_summary_rows.append({"metric": f"credibility_bin_{key}", "value": value})
    write_csv(args.out_csv_summary, csv_summary_rows, ["metric", "value"])

    print(f"Overall credibility: {overall:.3f} ({interpretation(overall)}, high ratio: {high_ratio:.1%})")
    print(f"Per-row scores saved to {args.out_per_row}")
    print(f"Summary saved to {args.out_summary}")


if __name__ == "__main__":
    main()
