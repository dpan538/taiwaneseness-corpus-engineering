#!/usr/bin/env python3
"""Final audit before freezing the thesis corpus.

The frozen dataset is allowed to contain weak/no-binding controls, so marker
presence is reported separately from structural readiness. Freeze readiness is
based on artifact-level duplication, critical anomaly status, source
traceability, and required structural fields.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


STRUCTURAL_REQUIRED = ["attestation_id", "year", "period", "corridor", "source_url"]
MARKER_FIELDS = ["dish_marker", "taiwan_marker"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run final freeze-readiness audit.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--anomaly-json", default="")
    parser.add_argument("--negative-searches", default="data/negative_searches.csv")
    parser.add_argument("--max-structural-missing-rate", type=float, default=0.02)
    parser.add_argument("--min-traceable-rate", type=float, default=0.95)
    parser.add_argument("--out-json", default="reports/final_audit.json")
    parser.add_argument("--out-md", default="reports/final_audit.md")
    return parser.parse_args()


def load_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def source_ref(row: dict[str, str]) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or ""
    ).strip()


def artifact_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        source_ref(row).lower().rstrip("/"),
        (row.get("year") or "").strip(),
        (row.get("brand_or_category") or "").strip().lower(),
        (row.get("attestation_type") or "").strip().lower(),
    )


def missing_counts(rows: list[dict[str, str]], fields: list[str]) -> dict[str, int]:
    return {field: sum(1 for row in rows if not (row.get(field) or "").strip()) for field in fields}


def duplicate_artifacts(rows: list[dict[str, str]]) -> list[str]:
    seen: set[tuple[str, str, str, str]] = set()
    duplicates: list[str] = []
    for row in rows:
        key = artifact_key(row)
        if key in seen:
            duplicates.append(row.get("attestation_id") or "")
        seen.add(key)
    return duplicates


def duplicate_ids(rows: list[dict[str, str]]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for row in rows:
        attestation_id = (row.get("attestation_id") or "").strip()
        if not attestation_id:
            continue
        if attestation_id in seen:
            duplicates.append(attestation_id)
        seen.add(attestation_id)
    return duplicates


def anomaly_has_critical(path: str) -> tuple[bool, dict]:
    if not path or not Path(path).exists():
        return False, {"status": "not_provided"}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "has_critical" in data:
            return bool(data.get("has_critical")), data
        critical = data.get("critical")
        if isinstance(critical, dict):
            return any(bool(value) for value in critical.values()), data
        if isinstance(critical, (int, float)):
            return critical > 0, data
    return False, data if isinstance(data, dict) else {"raw": data}


def safe_int(value: str) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def period_corridor_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = Counter()
    for row in rows:
        period = row.get("period") or "unknown"
        corridor = row.get("corridor") or "unknown"
        counts[f"{period} / {corridor}"] += 1
    return dict(counts.most_common())


def main() -> None:
    args = parse_args()
    fields, rows = load_csv(args.attestations)
    total = len(rows)
    if total == 0:
        raise SystemExit("No rows found.")

    structural_missing = missing_counts(rows, STRUCTURAL_REQUIRED)
    marker_missing = missing_counts(rows, MARKER_FIELDS)
    structural_missing_rates = {field: count / total for field, count in structural_missing.items()}
    marker_missing_rates = {field: count / total for field, count in marker_missing.items()}

    dup_artifacts = duplicate_artifacts(rows)
    dup_ids = duplicate_ids(rows)
    traceable = sum(1 for row in rows if source_ref(row))
    traceable_rate = traceable / total
    critical_anomaly, anomaly_payload = anomaly_has_critical(args.anomaly_json)

    invalid_year_count = sum(1 for row in rows if safe_int(row.get("year", "")) is None)
    negative_search_exists = Path(args.negative_searches).exists() and Path(args.negative_searches).stat().st_size > 0

    authority_counts = Counter((row.get("authority_level") or "missing") for row in rows)
    source_type_counts = Counter((row.get("source_type") or "missing") for row in rows)
    tertiary_ratio = authority_counts.get("tertiary", 0) / total
    primary_count = authority_counts.get("primary", 0)

    structural_ok = all(rate <= args.max_structural_missing_rate for rate in structural_missing_rates.values())
    traceable_ok = traceable_rate >= args.min_traceable_rate
    duplicate_ok = not dup_artifacts and not dup_ids
    years_ok = invalid_year_count == 0
    freeze_ready = structural_ok and traceable_ok and duplicate_ok and years_ok and not critical_anomaly

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "attestations": args.attestations,
        "total_records": total,
        "fields_count": len(fields),
        "freeze_ready": freeze_ready,
        "checks": {
            "structural_missing_ok": structural_ok,
            "source_traceability_ok": traceable_ok,
            "duplicate_free": duplicate_ok,
            "valid_years": years_ok,
            "no_critical_anomalies": not critical_anomaly,
            "negative_search_log_exists": negative_search_exists,
        },
        "structural_missing": structural_missing,
        "structural_missing_rates": {k: round(v, 4) for k, v in structural_missing_rates.items()},
        "marker_missing": marker_missing,
        "marker_missing_rates": {k: round(v, 4) for k, v in marker_missing_rates.items()},
        "duplicate_artifact_count": len(dup_artifacts),
        "duplicate_attestation_id_count": len(dup_ids),
        "source_traceable_rate": round(traceable_rate, 4),
        "invalid_year_count": invalid_year_count,
        "primary_count": primary_count,
        "tertiary_ratio": round(tertiary_ratio, 4),
        "authority_distribution": dict(authority_counts.most_common()),
        "top_source_types": dict(source_type_counts.most_common(15)),
        "period_corridor_counts": period_corridor_counts(rows),
        "anomaly_summary": anomaly_payload,
        "recommendation": (
            "Freeze candidate is structurally ready for thesis writing."
            if freeze_ready
            else "Do not freeze yet; resolve failed structural checks or document an override."
        ),
    }

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def mark(value: bool) -> str:
        return "PASS" if value else "FAIL"

    md = [
        "# Final Data Audit",
        "",
        f"Generated: {summary['generated_at']}",
        f"Input: `{args.attestations}`",
        f"Records: **{total}**",
        "",
        "## Freeze Checks",
        "| Check | Status |",
        "|---|---|",
        f"| Structural fields present | {mark(structural_ok)} |",
        f"| Source traceability >= {args.min_traceable_rate:.0%} | {mark(traceable_ok)} |",
        f"| No duplicate artifact / attestation IDs | {mark(duplicate_ok)} |",
        f"| Valid years | {mark(years_ok)} |",
        f"| No critical anomalies | {mark(not critical_anomaly)} |",
        f"| Negative search log exists | {mark(negative_search_exists)} |",
        "",
        f"**Overall freeze ready:** {'YES' if freeze_ready else 'NO'}",
        "",
        "## Key Metrics",
        f"- Source traceability: {traceable_rate:.1%}",
        f"- Primary records: {primary_count}",
        f"- Tertiary ratio: {tertiary_ratio:.1%}",
        f"- Duplicate artifacts: {len(dup_artifacts)}",
        f"- Duplicate attestation IDs: {len(dup_ids)}",
        f"- Invalid years: {invalid_year_count}",
        f"- Marker missing rates: {summary['marker_missing_rates']}",
        "",
        "## Recommendation",
        summary["recommendation"],
    ]
    Path(args.out_md).write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Freeze ready: {freeze_ready}")
    print(f"Records={total}, traceability={traceable_rate:.1%}, primary={primary_count}, tertiary={tertiary_ratio:.1%}")
    if not freeze_ready:
        print(summary["recommendation"])


if __name__ == "__main__":
    main()
