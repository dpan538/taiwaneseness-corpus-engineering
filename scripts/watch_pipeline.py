#!/usr/bin/env python3
"""Inspect pipeline alerts and print unresolved warnings/critical items."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alerts", default="reports/alerts.jsonl")
    parser.add_argument("--severity", default="", help="Optional severity filter.")
    parser.add_argument("--fail-on-critical", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.alerts)
    if not path.exists():
        print(f"No alerts file found: {path}")
        return
    unresolved = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            alert = json.loads(line)
            if alert.get("acknowledged") is True:
                continue
            if args.severity and alert.get("severity") != args.severity:
                continue
            unresolved.append(alert)

    if not unresolved:
        print("No unresolved alerts.")
        return

    for alert in unresolved:
        print(
            f"[{alert.get('severity','').upper()}] {alert.get('code')}: "
            f"{alert.get('message')} context={json.dumps(alert.get('context', {}), ensure_ascii=False)}"
        )

    if args.fail_on_critical and any(a.get("severity") == "critical" for a in unresolved):
        raise SystemExit(2)


if __name__ == "__main__":
    main()

