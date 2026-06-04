#!/usr/bin/env python3
"""Add capture/search provenance fields and append manifest/log entries."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def source_ref(row: dict[str, str]) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or ""
    ).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add reproducible provenance IDs to accepted records.")
    parser.add_argument("--new-records-csv", required=True)
    parser.add_argument("--source-id", default="", help="Fallback source_id if rows do not already have one.")
    parser.add_argument("--manifest", default="raw/manifests/raw_capture_manifest.jsonl")
    parser.add_argument("--execution-log", default="logs/execution_log.csv")
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with Path(args.new_records_csv).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)

    if not rows:
        raise SystemExit("No rows found.")

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_entries: list[dict[str, object]] = []
    log_entries: list[dict[str, str]] = []
    for row in rows:
        ref = source_ref(row)
        attestation_id = (row.get("attestation_id") or "").strip()
        source_id = (row.get("source_id") or args.source_id or "SRC_UNSPECIFIED").strip()
        capture_id = (row.get("capture_id") or stable_id("cap", source_id, ref, attestation_id)).strip()
        search_id = (row.get("search_id") or stable_id("srch", source_id, ref)).strip()
        row["capture_id"] = capture_id
        row["search_id"] = search_id
        row["source_id"] = source_id

        manifest_entries.append(
            {
                "capture_id": capture_id,
                "source_id": source_id,
                "search_id": search_id,
                "capture_date": timestamp,
                "artifact_type": row.get("attestation_type") or "unknown",
                "source_url": ref,
                "local_path": row.get("local_path") or "",
                "sha256": row.get("sha256") or "",
                "http_status": row.get("status") or row.get("http_status") or "",
                "content_type": row.get("content_type") or "",
                "notes": row.get("notes") or "Provenance backfilled for accepted record.",
            }
        )
        log_entries.append(
            {
                "task_id": search_id,
                "executed_at": timestamp,
                "execution_status": "success",
                "result_count": "1",
                "accepted_attestation_id": attestation_id or capture_id,
                "failure_reason": "",
                "target": ref,
                "status": row.get("status") or row.get("http_status") or "",
                "content_length": row.get("content_length") or "",
            }
        )

    out_fields = list(fields)
    for field in ("capture_id", "search_id", "source_id"):
        if field not in out_fields:
            out_fields.append(field)

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    if not args.dry_run:
        manifest_path = Path(args.manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("a", encoding="utf-8") as handle:
            for entry in manifest_entries:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

        log_path = Path(args.execution_log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        exists = log_path.exists() and log_path.stat().st_size > 0
        with log_path.open("a", encoding="utf-8", newline="") as handle:
            fields_log = [
                "task_id",
                "executed_at",
                "execution_status",
                "result_count",
                "accepted_attestation_id",
                "failure_reason",
                "target",
                "status",
                "content_length",
            ]
            writer = csv.DictWriter(handle, fieldnames=fields_log, lineterminator="\n")
            if not exists:
                writer.writeheader()
            writer.writerows(log_entries)

    mode = "dry run" if args.dry_run else "updated"
    print(f"Provenance {mode} for {len(rows)} rows: {args.out_csv}")


if __name__ == "__main__":
    main()
