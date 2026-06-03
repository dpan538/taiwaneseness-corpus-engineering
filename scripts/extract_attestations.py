#!/usr/bin/env python3
"""Extract candidate attestations while merging windows per source artifact."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocr-jsonl", required=True)
    parser.add_argument("--lexicon", default="config/taiwaneseness_lexicon.json")
    parser.add_argument("--context-chars", type=int, default=80)
    parser.add_argument("--out-csv", default="interim/extracted_windows/attestation_candidates.csv")
    return parser.parse_args()


def load_markers(path: str) -> tuple[list[str], list[str]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    dish = data.get("dish_markers", [])
    taiwan = data.get("taiwan_markers", [])
    for terms in data.get("domains", {}).values():
        taiwan.extend(terms)
    return sorted(set(dish), key=len, reverse=True), sorted(set(taiwan), key=len, reverse=True)


def compile_re(terms: list[str]) -> re.Pattern:
    escaped = [re.escape(term) for term in terms if term]
    return re.compile("|".join(escaped), re.IGNORECASE) if escaped else re.compile(r"a^")


def unique_join(values: list[str], sep: str = ";") -> str:
    out: list[str] = []
    for value in values:
        value = value or ""
        for token in value.replace("|", ";").split(";"):
            token = token.strip()
            if token and token not in out:
                out.append(token)
    return sep.join(out)


def extract_windows(text: str, dish_re: re.Pattern, taiwan_re: re.Pattern, context_chars: int) -> list[dict]:
    rows = []
    for match in dish_re.finditer(text or ""):
        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)
        window = text[start:end]
        rows.append(
            {
                "dish_marker": match.group(0),
                "taiwan_marker": ";".join(sorted(set(taiwan_re.findall(window)))),
                "window_text": window,
                "window_start": str(start),
                "window_end": str(end),
            }
        )
    return rows


def record_key(record: dict) -> tuple[str, str]:
    capture = (
        record.get("capture_id")
        or record.get("source_url")
        or record.get("source_ref")
        or record.get("source_id")
        or ""
    )
    page = str(record.get("page_number", record.get("page_num", "")))
    return capture, page


def main() -> None:
    args = parse_args()
    dish_terms, taiwan_terms = load_markers(args.lexicon)
    dish_re = compile_re(dish_terms)
    taiwan_re = compile_re(taiwan_terms)
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    metadata: dict[tuple[str, str], dict] = {}

    with Path(args.ocr_jsonl).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            text = record.get("text") or record.get("ocr_text") or ""
            windows = extract_windows(text, dish_re, taiwan_re, args.context_chars)
            if not windows:
                continue
            key = record_key(record)
            grouped[key].extend(windows)
            metadata[key] = record

    fields = [
        "capture_id",
        "source_id",
        "source_ref",
        "page_number",
        "extraction_method",
        "attestation_type",
        "dish_marker",
        "taiwan_marker",
        "original_text",
        "window_start",
        "window_end",
    ]
    rows: list[dict] = []
    for key, windows in sorted(grouped.items()):
        record = metadata[key]
        rows.append(
            {
                "capture_id": record.get("capture_id", key[0]),
                "source_id": record.get("source_id", ""),
                "source_ref": record.get("source_ref", record.get("source_url", "")),
                "page_number": str(record.get("page_number", record.get("page_num", key[1]))),
                "extraction_method": record.get("extraction_method", record.get("engine", "")),
                "attestation_type": "extracted_text",
                "dish_marker": unique_join([w["dish_marker"] for w in windows]),
                "taiwan_marker": unique_join([w["taiwan_marker"] for w in windows]),
                "original_text": " || ".join(dict.fromkeys(w["window_text"] for w in windows if w["window_text"])),
                "window_start": min(w["window_start"] for w in windows),
                "window_end": max(w["window_end"] for w in windows),
            }
        )

    out = Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"rows": len(rows), "out": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
