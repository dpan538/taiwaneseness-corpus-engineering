#!/usr/bin/env python3
"""Compute real harvest progress from execution logs and accepted-record files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


def parse_int(value: str | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def count_rows(path: str | None) -> int | None:
    if not path:
        return None
    target = Path(path)
    if not target.exists():
        return None
    with target.open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description="Update progress counters from actual execution logs.")
    parser.add_argument("--execution-log", required=True)
    parser.add_argument("--attestations", help="Optional accepted records CSV to count.")
    parser.add_argument("--target-accepted", type=int, default=100)
    parser.add_argument("--out-json", default="reports/progress_dashboard.json")
    parser.add_argument("--out-md", default="")
    args = parser.parse_args()

    log_path = Path(args.execution_log)
    if not log_path.exists():
        raise SystemExit(f"Execution log not found: {args.execution_log}")

    rows: list[dict[str, str]] = []
    with log_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    executed_rows = [row for row in rows if (row.get("executed_at") or "").strip()]
    successful_rows = [row for row in executed_rows if (row.get("execution_status") or "").strip().lower() == "success"]
    failed_rows = [row for row in executed_rows if row not in successful_rows]

    executed_task_ids = {row.get("task_id", "") for row in executed_rows if row.get("task_id")}
    successful_task_ids = {row.get("task_id", "") for row in successful_rows if row.get("task_id")}
    total_results = sum(parse_int(row.get("result_count")) for row in successful_rows)

    accepted_ids = {
        row.get("accepted_attestation_id", "").strip()
        for row in successful_rows
        if row.get("accepted_attestation_id", "").strip()
    }
    accepted_from_file = count_rows(args.attestations)
    accepted_count = accepted_from_file if accepted_from_file is not None else len(accepted_ids)

    failure_reasons = Counter((row.get("failure_reason") or "unknown").strip() or "unknown" for row in failed_rows)
    failure_denominator = len(successful_rows) + len(failed_rows)
    failure_ratio = len(failed_rows) / failure_denominator if failure_denominator else 0.0
    yield_rate = accepted_count / len(successful_task_ids) if successful_task_ids else 0.0

    if len(executed_task_ids) == 0:
        recommendation = "STOP - no tasks have actually executed."
    elif failure_ratio > 0.5:
        recommendation = "STOP - failure ratio is too high; inspect execution failures before continuing."
    elif accepted_count < args.target_accepted:
        recommendation = "CONTINUE SMALL BATCHES - accepted records are below target; count only logged executions."
    else:
        recommendation = "READY FOR REVIEW - accepted-record target reached; run corpus audits before push."

    progress = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "execution_log": args.execution_log,
        "attestations": args.attestations or "",
        "execution_log_rows": len(rows),
        "executed_url_count": len(executed_task_ids),
        "successful_url_count": len(successful_task_ids),
        "failure_count": len(failed_rows),
        "failure_ratio": round(failure_ratio, 4),
        "result_count": total_results,
        "accepted_record_count": accepted_count,
        "target_accepted": args.target_accepted,
        "accepted_remaining": max(0, args.target_accepted - accepted_count),
        "accepted_per_successful_url": round(yield_rate, 4),
        "top_failure_reasons": dict(failure_reasons.most_common(10)),
        "next_recommendation": recommendation,
    }

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_json).open("w", encoding="utf-8") as handle:
        json.dump(progress, handle, ensure_ascii=False, indent=2)

    if args.out_md:
        md = f"""# Progress Dashboard

Generated: {progress['timestamp']}

- Executed URLs/tasks: {progress['executed_url_count']}
- Successful URL/tasks: {progress['successful_url_count']}
- Failures: {progress['failure_count']} ({progress['failure_ratio']:.1%})
- Raw result count: {progress['result_count']}
- Accepted records: {progress['accepted_record_count']} / {progress['target_accepted']}
- Accepted remaining: {progress['accepted_remaining']}
- Accepted per successful URL: {progress['accepted_per_successful_url']}

## Top Failure Reasons
"""
        if failure_reasons:
            for reason, count in failure_reasons.most_common(10):
                md += f"- {reason}: {count}\n"
        else:
            md += "- None\n"
        md += f"\n## Recommendation\n{recommendation}\n"
        Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_md).write_text(md, encoding="utf-8")

    print("Progress dashboard updated.")
    print(f"Executed URLs/tasks: {progress['executed_url_count']}")
    print(f"Successful URLs/tasks: {progress['successful_url_count']}")
    print(f"Accepted records: {progress['accepted_record_count']} / {progress['target_accepted']}")
    print(f"Failure ratio: {progress['failure_ratio']:.1%}")
    print(f"Recommendation: {recommendation}")


if __name__ == "__main__":
    main()
