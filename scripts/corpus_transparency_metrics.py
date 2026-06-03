#!/usr/bin/env python3
"""Compute reproducible corpus transparency metrics.

The score intentionally reflects missing infrastructure. If a corpus has no
row-level search_id or raw capture manifest, those components remain low rather
than being inferred from downstream data.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


DEFAULT_EXPECTED_NEGATIVE_CORRIDORS = ("Korea", "Vietnam", "Latin America")
DEFAULT_EXPECTED_NEGATIVE_PHASES = ("1946_1987",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute corpus transparency metrics.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--negative-searches", default="data/negative_searches.csv")
    parser.add_argument("--manifest", default="raw/manifests/raw_capture_manifest.jsonl")
    parser.add_argument("--harvest-log", default="data/harvest_log_1946_1987.csv")
    parser.add_argument("--out-json", default="reports/transparency_metrics.json")
    parser.add_argument("--out-csv", default="reports/transparency_metrics.csv")
    return parser.parse_args()


def read_csv(path: str) -> list[dict]:
    if not path or not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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


def row_log_ref(row: dict) -> str:
    for field in ("search_id", "harvest_id", "capture_id", "negative_search_id"):
        value = (row.get(field) or "").strip()
        if value and not value.lower().startswith("manual"):
            return value
    return ""


def phase_of(row: dict) -> str:
    period = (row.get("period") or "").strip()
    if "1946" in period and "1987" in period:
        return "1946_1987"
    if "1987" in period and "2015" in period:
        return "1987_2015"
    if "2015" in period and "2025" in period:
        return "2015_2025"
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
    return period or "UNKNOWN"


def load_capture_ids(path: str) -> set[str]:
    capture_ids: set[str] = set()
    manifest = Path(path)
    if not manifest.exists():
        return capture_ids
    with manifest.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            capture_id = str(obj.get("capture_id") or "").strip()
            if capture_id:
                capture_ids.add(capture_id)
    return capture_ids


def negative_pairs(rows: list[dict]) -> set[tuple[str, str]]:
    out = set()
    for row in rows:
        corridor = (row.get("corridor") or "").strip()
        phase = (row.get("phase") or row.get("period") or "").strip()
        if corridor and phase:
            out.add((corridor, phase))
    return out


def ratio(numerator: int | float, denominator: int | float, default: float = 0.0) -> float:
    return float(numerator) / float(denominator) if denominator else default


def main() -> None:
    args = parse_args()
    attestations = read_csv(args.attestations)
    total = len(attestations)
    negatives = read_csv(args.negative_searches)
    harvest_log = read_csv(args.harvest_log)
    capture_ids = load_capture_ids(args.manifest)

    traceable = sum(1 for row in attestations if source_ref(row))
    row_logged = sum(1 for row in attestations if row_log_ref(row))
    source_id_present = sum(1 for row in attestations if (row.get("source_id") or "").strip())
    harvest_log_available = 1.0 if harvest_log else 0.0
    capture_exists = sum(1 for row in attestations if (row.get("capture_id") or "").strip() in capture_ids)
    verification_recorded = sum(
        1
        for row in attestations
        if (row.get("verification_level") or "").strip().lower() not in {"", "unknown"}
    )
    notes_recorded = sum(1 for row in attestations if (row.get("notes") or "").strip())

    attested_pairs = {
        ((row.get("corridor") or row.get("region") or "").strip(), phase_of(row))
        for row in attestations
        if (row.get("corridor") or row.get("region") or "").strip()
    }
    neg_pairs = negative_pairs(negatives)
    attested_negative_coverage = ratio(len(attested_pairs & neg_pairs), len(attested_pairs), default=1.0)

    expected_negative_pairs = {
        (corridor, phase)
        for corridor in DEFAULT_EXPECTED_NEGATIVE_CORRIDORS
        for phase in DEFAULT_EXPECTED_NEGATIVE_PHASES
    }
    expected_negative_coverage = ratio(
        len(expected_negative_pairs & neg_pairs),
        len(expected_negative_pairs),
        default=1.0,
    )

    scripts_present = 1.0 if Path("scripts").exists() and any(Path("scripts").iterdir()) else 0.0
    configs_present = 1.0 if Path("configs").exists() and any(Path("configs").iterdir()) else 0.0
    audit_present = 1.0 if Path("reports/corpus_health.md").exists() else 0.0
    docs_present = 1.0 if Path("docs").exists() and any(Path("docs").iterdir()) else 0.0
    documentation_score = (scripts_present + configs_present + audit_present + docs_present) / 4.0

    components = {
        "source_traceable_ratio": ratio(traceable, total),
        "row_process_log_ref_ratio": ratio(row_logged, total),
        "harvest_log_available": harvest_log_available,
        "raw_capture_exists_ratio": ratio(capture_exists, total),
        "verification_recorded_ratio": ratio(verification_recorded, total),
        "notes_recorded_ratio": ratio(notes_recorded, total),
        "expected_negative_search_coverage_ratio": expected_negative_coverage,
        "attested_pair_negative_search_coverage_ratio": attested_negative_coverage,
        "documentation_score": documentation_score,
    }

    weights = {
        "source_traceable_ratio": 0.20,
        "row_process_log_ref_ratio": 0.12,
        "harvest_log_available": 0.08,
        "raw_capture_exists_ratio": 0.15,
        "verification_recorded_ratio": 0.18,
        "notes_recorded_ratio": 0.07,
        "expected_negative_search_coverage_ratio": 0.10,
        "documentation_score": 0.10,
    }
    transparency_score = sum(components[key] * weight for key, weight in weights.items()) * 100

    phase_counts = Counter(phase_of(row) for row in attestations)
    metrics = {
        "transparency_score": round(transparency_score, 2),
        "total_records": total,
        "components": {key: round(value, 4) for key, value in components.items()},
        "counts": {
            "traceable_records": traceable,
            "row_process_log_ref_records": row_logged,
            "source_id_present_records": source_id_present,
            "raw_capture_matched_records": capture_exists,
            "verification_recorded_records": verification_recorded,
            "notes_recorded_records": notes_recorded,
            "attested_corridor_phase_pairs": len(attested_pairs),
            "negative_search_pairs": len(neg_pairs),
            "harvest_log_rows": len(harvest_log),
            "raw_capture_manifest_ids": len(capture_ids),
            "phase_counts": dict(phase_counts),
        },
        "method_notes": [
            "Row process-log references use search_id, harvest_id, capture_id, or negative_search_id if present; source_id is reported separately and is not counted as process-log evidence.",
            "Raw capture matching is strict and requires capture_id in both the attestation row and manifest JSONL.",
            "Expected negative-search coverage uses Korea, Vietnam, and Latin America for 1946_1987 by default.",
            "Attested-pair negative coverage is reported for transparency but not included in the weighted score.",
        ],
    }

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_json).open("w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    csv_rows = []
    for key, value in metrics["components"].items():
        csv_rows.append({"metric": key, "value": value, "category": "component"})
    for key, value in metrics["counts"].items():
        if isinstance(value, dict):
            continue
        csv_rows.append({"metric": key, "value": value, "category": "count"})
    csv_rows.append({"metric": "transparency_score", "value": metrics["transparency_score"], "category": "score"})
    write_csv(args.out_csv, csv_rows, ["metric", "value", "category"])

    print(f"Transparency score: {metrics['transparency_score']:.1f}/100")
    print(f"Details saved to {args.out_json} and {args.out_csv}")


if __name__ == "__main__":
    main()
