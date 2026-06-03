#!/usr/bin/env python3
"""Normalize project text fields while preserving original text elsewhere.

This script intentionally performs light normalization only. Script choice is
analytically meaningful in this project, so full traditional/simplified
conversion should be handled as a separate, explicitly documented step if used.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path


WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip().lower()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument(
        "--fields",
        required=True,
        help="Comma-separated text fields to normalize into normalized_<field>",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    fields = [field.strip() for field in args.fields.split(",") if field.strip()]

    with input_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise SystemExit("Input CSV has no header")
        rows = list(reader)

    fieldnames = list(reader.fieldnames)
    if any(None in row for row in rows):
        fieldnames.append("_extra_fields")
        for row in rows:
            extras = row.pop(None, None)
            if extras:
                row["_extra_fields"] = " ".join(extras)
    for field in fields:
        if field not in fieldnames:
            raise SystemExit(f"Missing field in input CSV: {field}")
        normalized_field = f"normalized_{field}"
        if normalized_field not in fieldnames:
            fieldnames.append(normalized_field)

    for row in rows:
        for field in fields:
            row[f"normalized_{field}"] = normalize_text(row.get(field, ""))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
