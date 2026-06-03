#!/usr/bin/env python3
"""Extract historical attestation candidate windows from OCR JSONL."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocr-jsonl", required=True)
    parser.add_argument("--lexicon", default="config/taiwaneseness_lexicon.json")
    parser.add_argument("--context-chars", type=int, default=80)
    parser.add_argument("--out", default="interim/extracted_windows/attestation_candidates.csv")
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


def windows(text: str, dish_re: re.Pattern, taiwan_re: re.Pattern, context_chars: int) -> list[dict]:
    out = []
    for match in dish_re.finditer(text or ""):
        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)
        window = text[start:end]
        taiwan_hits = sorted(set(taiwan_re.findall(window)))
        out.append(
            {
                "original_text": window,
                "dish_marker": match.group(0),
                "taiwan_marker": "|".join(taiwan_hits),
                "window_start": str(start),
                "window_end": str(end),
            }
        )
    return out


def main() -> None:
    args = parse_args()
    dish, taiwan = load_markers(args.lexicon)
    dish_re = compile_re(dish)
    taiwan_re = compile_re(taiwan)
    rows = []
    with Path(args.ocr_jsonl).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            text = record.get("text") or record.get("ocr_text") or ""
            for row in windows(text, dish_re, taiwan_re, args.context_chars):
                row["capture_id"] = record.get("capture_id", "")
                row["source_id"] = record.get("source_id", "")
                row["page_number"] = str(record.get("page_number", record.get("page_num", "")))
                row["extraction_method"] = record.get("extraction_method", record.get("engine", ""))
                rows.append(row)

    fields = ["capture_id", "source_id", "page_number", "extraction_method", "original_text", "dish_marker", "taiwan_marker", "window_start", "window_end"]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"rows": len(rows), "out": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

