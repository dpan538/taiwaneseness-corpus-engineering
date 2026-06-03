#!/usr/bin/env python3
"""Merge attestation CSV tables with compatible columns."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, help="Comma-separated CSV inputs")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    paths = [Path(value.strip()) for value in args.inputs.split(",") if value.strip()]
    fieldnames: list[str] = []
    rows: list[dict] = []
    for path in paths:
        fields, table = read_rows(path)
        for field in fields:
            if field not in fieldnames:
                fieldnames.append(field)
        rows.extend(table)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"merged_rows={len(rows)} output={output_path}")


if __name__ == "__main__":
    main()
