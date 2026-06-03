#!/usr/bin/env python3
"""Score merchant or review texts with the project Taiwaneseness lexicon."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable


CHINESE_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_WORD_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+)?")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def count_terms(text: str, terms: Iterable[str]) -> tuple[int, list[str]]:
    spans: list[tuple[int, int, str]] = []
    lowered = (text or "").lower()
    for term in sorted(set(terms), key=len, reverse=True):
        needle = term.lower()
        start = 0
        while True:
            index = lowered.find(needle, start)
            if index < 0:
                break
            spans.append((index, index + len(needle), term))
            start = index + 1

    selected: list[tuple[int, int, str]] = []
    for start, end, term in sorted(spans, key=lambda item: (item[0], -(item[1] - item[0]))):
        if any(start < kept_end and end > kept_start for kept_start, kept_end, _ in selected):
            continue
        selected.append((start, end, term))

    matched = sorted({term for _, _, term in selected}, key=lambda term: term.lower())
    return len(selected), matched


def token_count(text: str) -> int:
    text = text or ""
    chinese_chars = CHINESE_CHAR_RE.findall(text)
    latin_words = LATIN_WORD_RE.findall(text)
    return max(1, len(chinese_chars) + len(latin_words))


def join_fields(row: dict, fields: list[str]) -> str:
    return " ".join(row.get(field, "") or "" for field in fields)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output scored CSV path")
    parser.add_argument("--lexicon", default="config/taiwaneseness_lexicon.json")
    parser.add_argument(
        "--text-fields",
        required=True,
        help="Comma-separated fields to concatenate for scoring",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    lexicon = load_json(Path(args.lexicon))
    text_fields = [field.strip() for field in args.text_fields.split(",") if field.strip()]
    domains: dict[str, list[str]] = lexicon["domains"]

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
    additions = [
        "analysis_text",
        "token_count",
        "dish_marker_count",
        "taiwan_marker_count",
        "binding_present",
        "matched_dish_markers",
        "matched_taiwan_markers",
        "has_traditional_script_cue",
    ]
    for domain in domains:
        additions.extend([f"{domain}_count", f"{domain}_score", f"{domain}_matched_terms"])
    for field in additions:
        if field not in fieldnames:
            fieldnames.append(field)

    traditional_chars = lexicon.get("visual_or_script_cues", {}).get(
        "traditional_script_chars", []
    )

    for row in rows:
        text = join_fields(row, text_fields)
        n_tokens = token_count(text)
        dish_count, dish_matches = count_terms(text, lexicon["dish_markers"])
        taiwan_count, taiwan_matches = count_terms(text, lexicon["taiwan_markers"])
        traditional_count, _ = count_terms(text, traditional_chars)

        row["analysis_text"] = text
        row["token_count"] = str(n_tokens)
        row["dish_marker_count"] = str(dish_count)
        row["taiwan_marker_count"] = str(taiwan_count)
        row["binding_present"] = "1" if dish_count > 0 and taiwan_count > 0 else "0"
        row["matched_dish_markers"] = "|".join(dish_matches)
        row["matched_taiwan_markers"] = "|".join(taiwan_matches)
        row["has_traditional_script_cue"] = "1" if traditional_count > 0 else "0"

        for domain, terms in domains.items():
            domain_count, matches = count_terms(text, terms)
            row[f"{domain}_count"] = str(domain_count)
            row[f"{domain}_score"] = f"{domain_count / n_tokens:.6f}"
            row[f"{domain}_matched_terms"] = "|".join(matches)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
