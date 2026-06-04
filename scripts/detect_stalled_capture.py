#!/usr/bin/env python3
"""Detect whether accepted-record capture has stalled."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path


def count_csv_rows(path: str) -> int:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def parse_date_from_filename(path: str) -> datetime | None:
    match = re.search(r"(\d{8})", os.path.basename(path))
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y%m%d")
    except ValueError:
        return None


def file_time(path: str) -> datetime:
    return parse_date_from_filename(path) or datetime.fromtimestamp(os.path.getmtime(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect stalled capture using history snapshots.")
    parser.add_argument("--records-csv", required=True)
    parser.add_argument("--history-dir", default="data/history")
    parser.add_argument("--min-recent-gain", type=float, default=5.0)
    parser.add_argument("--stale-days", type=int, default=3)
    parser.add_argument("--out-json", default="reports/capture_stall.json")
    args = parser.parse_args()

    current_n = count_csv_rows(args.records_csv)
    current_time = datetime.now()

    history: list[tuple[datetime, int, str]] = []
    history_dir = Path(args.history_dir)
    if history_dir.is_dir():
        for path in history_dir.glob("attestations_*.csv"):
            history.append((file_time(str(path)), count_csv_rows(str(path)), str(path)))

    history.sort(key=lambda item: item[0])
    recent = history[-5:] + [(current_time, current_n, args.records_csv)]

    deltas = []
    for prev, cur in zip(recent, recent[1:]):
        days = max((cur[0] - prev[0]).total_seconds() / 86400, 0)
        gain = cur[1] - prev[1]
        if days > 0:
            deltas.append(gain / days)

    avg_daily_gain = sum(deltas) / len(deltas) if deltas else 0.0
    recent_daily_gain = deltas[-1] if deltas else 0.0
    days_since_prev = (
        (recent[-1][0] - recent[-2][0]).total_seconds() / 86400 if len(recent) > 1 else 0.0
    )

    # No history does not prove activity. Mark it separately.
    insufficient_history = len(recent) < 2
    stall_detected = False
    if not insufficient_history:
        stall_detected = (
            recent_daily_gain < args.min_recent_gain and days_since_prev >= args.stale_days
        ) or (len(deltas) >= 3 and avg_daily_gain < 1.0)

    summary = {
        "records_csv": args.records_csv,
        "current_record_count": current_n,
        "history_points": [
            {"timestamp": item[0].isoformat(), "records": item[1], "path": item[2]} for item in recent
        ],
        "avg_daily_gain": round(avg_daily_gain, 2),
        "recent_daily_gain": round(recent_daily_gain, 2),
        "days_since_previous_snapshot": round(days_since_prev, 2),
        "insufficient_history": insufficient_history,
        "stall_detected": stall_detected,
        "message": (
            "Insufficient history to determine capture velocity."
            if insufficient_history
            else "Capture seems stalled. Check task execution and accepted-record writes."
            if stall_detected
            else "Capture appears active by available history."
        ),
    }

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_json).open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    state = "UNKNOWN" if insufficient_history else "STALLED" if stall_detected else "ACTIVE"
    print(f"Capture stall detection: {state} (current records {current_n})")


if __name__ == "__main__":
    main()
