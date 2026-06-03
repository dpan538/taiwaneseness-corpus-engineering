#!/usr/bin/env python3
"""Health audit and claim-permission flags for the canonical corpus."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


TARGETS = {"1946_1987": 700, "1987_2015": 750, "2015_2025": 300}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--sources", default="")
    parser.add_argument("--negative", default="")
    parser.add_argument("--ownership", default="")
    parser.add_argument("--out-csv", default="reports/corpus_health.csv")
    parser.add_argument("--out-md", default="reports/corpus_health.md")
    parser.add_argument("--out-flags", default="reports/claim_flags.json")
    return parser.parse_args()


def read_csv(path: str) -> list[dict]:
    if not path or not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def phase_of(row: dict) -> str:
    period = row.get("period") or ""
    if "2015" in period and "2025" in period:
        return "2015_2025"
    if "1987" in period and "2015" in period:
        return "1987_2015"
    if "1946" in period and "1987" in period:
        return "1946_1987"
    try:
        year = int(float(row.get("year") or ""))
    except ValueError:
        return period
    if 1946 <= year <= 1987:
        return "1946_1987"
    if 1988 <= year <= 2014:
        return "1987_2015"
    if 2015 <= year <= 2025:
        return "2015_2025"
    return period


def usable(row: dict) -> bool:
    return (row.get("verification_level") or "verified").strip().lower() in {"verified", "probable", ""}


def artifact_key(row: dict) -> tuple[str, str, str]:
    source = (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_name")
        or row.get("source_id")
        or ""
    ).strip()
    date_or_year = (row.get("date") or row.get("year") or "").strip()
    brand = (row.get("brand_or_category") or row.get("brand") or "").strip()
    return source, date_or_year, brand


def year_of(row: dict) -> int | None:
    try:
        return int(float(row.get("year") or ""))
    except ValueError:
        return None


def temporal_bin(row: dict) -> str:
    year = year_of(row)
    if year is None:
        return "UNKNOWN"
    if 1940 <= year <= 1945:
        return "1940-1945"
    if 1946 <= year <= 1959:
        return "1946-1959"
    if 1960 <= year <= 1969:
        return "1960-1969"
    if 1970 <= year <= 1979:
        return "1970-1979"
    if 1980 <= year <= 1987:
        return "1980-1987"
    if 1988 <= year <= 1995:
        return "1988-1995"
    if 1996 <= year <= 2005:
        return "1996-2005"
    if 2006 <= year <= 2014:
        return "2006-2014"
    if 2015 <= year <= 2017:
        return "2015-2017"
    if 2018 <= year <= 2020:
        return "2018-2020"
    if 2021 <= year <= 2025:
        return "2021-2025"
    return "OUT_OF_SCOPE"


def markdown_table(rows: list[dict], fields: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    lines = [
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines) + "\n"


def write_alert(alerts_path: Path, severity: str, code: str, message: str, context: dict) -> None:
    alerts_path.parent.mkdir(parents=True, exist_ok=True)
    alert_id = f"{date.today().isoformat()}_{code}"
    if alerts_path.exists():
        with alerts_path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    if json.loads(line).get("alert_id") == alert_id:
                        return
                except json.JSONDecodeError:
                    continue
    alert = {
        "alert_id": alert_id,
        "created_at": date.today().isoformat(),
        "severity": severity,
        "code": code,
        "message": message,
        "context": context,
        "acknowledged": False,
    }
    with alerts_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(alert, ensure_ascii=False) + "\n")


def pct(value: float) -> float:
    return max(0.0, min(100.0, value))


def main() -> None:
    args = parse_args()
    attest = read_csv(args.attestations)
    usable_rows = [r for r in attest if usable(r)]
    ownership = read_csv(args.ownership)
    negative = read_csv(args.negative)

    phase_counts = Counter(phase_of(r) for r in usable_rows)
    phase_coverage = {phase: pct(phase_counts.get(phase, 0) / target * 100) for phase, target in TARGETS.items()}
    artifact_keys = [artifact_key(r) for r in usable_rows if any(artifact_key(r))]
    unique_sources = {key[0] for key in artifact_keys if key[0]}
    source_coverage = pct(len(unique_sources) / 300 * 100)
    verification_quality = pct(len(usable_rows) / len(attest) * 100) if attest else 0.0
    duplicate_rate = pct((len(artifact_keys) - len(set(artifact_keys))) / len(artifact_keys) * 100) if artifact_keys else 0.0
    split_artifact_groups = sum(1 for _, count in Counter(artifact_keys).items() if count > 1)
    probable_rows = [r for r in usable_rows if (r.get("verification_level") or "verified").strip().lower() in {"verified", "probable", ""}]
    low_confidence_probable = [
        r for r in probable_rows if (r.get("confidence") or "").strip().lower() == "low"
    ]
    low_confidence_probable_rate = pct(len(low_confidence_probable) / len(probable_rows) * 100) if probable_rows else 0.0
    ownership_complete = pct(sum(1 for r in ownership if r.get("ownership_category") and r.get("ownership_category") != "unknown") / len(ownership) * 100) if ownership else 0.0
    ownership_brands = {
        (r.get("brand") or r.get("brand_or_category") or "").strip().lower()
        for r in ownership
        if (r.get("brand") or r.get("brand_or_category") or "").strip()
    }
    attestation_brands = {
        (r.get("brand_or_category") or r.get("brand") or "").strip().lower()
        for r in usable_rows
        if (r.get("brand_or_category") or r.get("brand") or "").strip()
    }
    matched_brands = attestation_brands & ownership_brands
    ownership_matching_rate = pct(len(matched_brands) / len(attestation_brands) * 100) if attestation_brands else 0.0
    corridor_counts = Counter((r.get("corridor") or r.get("region") or "UNKNOWN") for r in usable_rows)
    negative_corridors = {
        (r.get("corridor") or "").strip()
        for r in negative
        if (r.get("corridor") or "").strip()
    }
    missing_or_thin_corridors = sorted(
        corridor for corridor, count in corridor_counts.items() if count < 30
    )
    expected_negative_corridors = {"Korea", "Vietnam", "Latin America"}
    negative_search_rows = []
    for corridor in sorted(expected_negative_corridors | set(missing_or_thin_corridors)):
        negative_search_rows.append(
            {
                "corridor": corridor,
                "usable_records": corridor_counts.get(corridor, 0),
                "has_negative_search_log": "1" if corridor in negative_corridors else "0",
                "claim_absence_allowed": "1" if corridor in negative_corridors else "0",
            }
        )
    negative_search_effort = pct(
        sum(1 for row in negative_search_rows if row["has_negative_search_log"] == "1")
        / len(negative_search_rows)
        * 100
    ) if negative_search_rows else 0.0
    nonempty_corridors = sum(1 for _, n in corridor_counts.items() if n >= 1)
    geographic_coverage = pct(nonempty_corridors / 12 * 100)
    source_types = Counter(r.get("source_type") or "UNKNOWN" for r in usable_rows)
    max_source_type_share = max(source_types.values()) / len(usable_rows) * 100 if usable_rows else 100.0
    source_type_diversity = pct(100 - max(0.0, max_source_type_share - 40))
    reproducibility = pct(sum(1 for r in usable_rows if r.get("source_id") or r.get("source_url_or_archive_ref") or r.get("source_url")) / len(usable_rows) * 100) if usable_rows else 0.0

    score = (
        0.20 * phase_coverage["1946_1987"]
        + 0.15 * phase_coverage["1987_2015"]
        + 0.10 * phase_coverage["2015_2025"]
        + 0.15 * source_coverage
        + 0.10 * geographic_coverage
        + 0.10 * source_type_diversity
        + 0.10 * verification_quality
        + 0.05 * (100 - duplicate_rate)
        + 0.05 * ownership_complete
        + 0.05 * reproducibility
    )

    temporal_counts = Counter((phase_of(r), temporal_bin(r)) for r in usable_rows)
    temporal_order = [
        ("1946_1987", "1946-1959"),
        ("1946_1987", "1960-1969"),
        ("1946_1987", "1970-1979"),
        ("1946_1987", "1980-1987"),
        ("1987_2015", "1988-1995"),
        ("1987_2015", "1996-2005"),
        ("1987_2015", "2006-2014"),
        ("2015_2025", "2015-2017"),
        ("2015_2025", "2018-2020"),
        ("2015_2025", "2021-2025"),
    ]
    temporal_rows = [
        {
            "phase": phase,
            "time_bin": time_bin,
            "usable_records": temporal_counts.get((phase, time_bin), 0),
            "is_empty": "1" if temporal_counts.get((phase, time_bin), 0) == 0 else "0",
        }
        for phase, time_bin in temporal_order
    ]

    phase_grade = "D"
    if all(v >= 90 for v in phase_coverage.values()) and verification_quality >= 85 and duplicate_rate < 10:
        phase_grade = "A"
    elif all(v >= 70 for v in phase_coverage.values()) and verification_quality >= 75 and duplicate_rate < 15:
        phase_grade = "B"
    elif all(v >= 40 for v in phase_coverage.values()) and verification_quality >= 60 and duplicate_rate < 25:
        phase_grade = "C"
    elif not attest or verification_quality < 40:
        phase_grade = "F"

    flags = {
        "can_make_macro_historical_claims": phase_grade in {"A", "B"},
        "can_compare_regions": all(n >= 30 for n in corridor_counts.values()) if corridor_counts else False,
        "can_compare_periods": all(v >= 70 for v in phase_coverage.values()),
        "can_analyze_ownership_shift": ownership_complete >= 60 and ownership_matching_rate >= 70,
        "can_analyze_platformization": phase_coverage["2015_2025"] >= 60,
        "can_publish_quantitative_tables": phase_grade in {"A", "B"} and score >= 70,
    }

    summary = {
        "health_score": round(score, 2),
        "grade": phase_grade,
        "usable_records": len(usable_rows),
        "unique_sources": len(unique_sources),
        "verification_quality": round(verification_quality, 2),
        "duplicate_rate": round(duplicate_rate, 2),
        "split_artifact_groups": split_artifact_groups,
        "low_confidence_probable_rate": round(low_confidence_probable_rate, 2),
        "ownership_completeness": round(ownership_complete, 2),
        "ownership_matching_rate": round(ownership_matching_rate, 2),
        "negative_search_effort": round(negative_search_effort, 2),
        **{f"{phase}_coverage": round(value, 2) for phase, value in phase_coverage.items()},
    }

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(summary)
    temporal_csv = Path(args.out_csv).with_name("corpus_temporal_distribution.csv")
    with temporal_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phase", "time_bin", "usable_records", "is_empty"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(temporal_rows)
    negative_csv = Path(args.out_csv).with_name("negative_search_effort.csv")
    with negative_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "corridor",
                "usable_records",
                "has_negative_search_log",
                "claim_absence_allowed",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(negative_search_rows)
    Path(args.out_flags).write_text(json.dumps(flags, ensure_ascii=False, indent=2), encoding="utf-8")
    alerts_path = Path(args.out_csv).with_name("alerts.jsonl")
    for row in temporal_rows:
        if row["is_empty"] == "1":
            write_alert(
                alerts_path,
                "warning",
                f"EMPTY_TIME_BIN_{row['phase']}_{row['time_bin']}",
                f"No usable records in {row['phase']} / {row['time_bin']}.",
                row,
            )
    for row in negative_search_rows:
        if row["has_negative_search_log"] == "0" and row["usable_records"] == 0:
            write_alert(
                alerts_path,
                "warning",
                f"NO_NEGATIVE_SEARCH_{row['corridor']}",
                f"{row['corridor']} has no usable records and no negative-search log.",
                row,
            )
    if ownership_matching_rate < 30 and attestation_brands:
        write_alert(
            alerts_path,
            "warning",
            "LOW_OWNERSHIP_MATCHING_RATE",
            "Ownership matching rate is below 30%; ownership analysis is exploratory only.",
            {"ownership_matching_rate": round(ownership_matching_rate, 2)},
        )
    Path(args.out_md).write_text(
        "# Corpus Health Report\n\n"
        f"Score: {score:.2f}/100\n\n"
        f"Grade: {phase_grade}\n\n"
        "## Summary\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in summary.items())
        + "\n\n## Temporal Distribution\n\n"
        + markdown_table(temporal_rows, ["phase", "time_bin", "usable_records", "is_empty"])
        + "\n## Negative Search Effort\n\n"
        + markdown_table(
            negative_search_rows,
            ["corridor", "usable_records", "has_negative_search_log", "claim_absence_allowed"],
        )
        + "\n## Ownership Matching\n\n"
        + f"- unique brands in usable attestations: {len(attestation_brands)}\n"
        + f"- brands matched to ownership events: {len(matched_brands)}\n"
        + f"- ownership_matching_rate: {ownership_matching_rate:.2f}%\n"
        + "- interpretation: below 30% means ownership analysis is exploratory only; below 70% blocks strong ownership-shift claims.\n"
        + "\n\n## Claim Flags\n\n```json\n"
        + json.dumps(flags, ensure_ascii=False, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
