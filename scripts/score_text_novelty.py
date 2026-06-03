#!/usr/bin/env python3
"""Score per-record text novelty within brand or source groups.

Novelty is defined as 1 - average similarity to comparable records. Low novelty
means the record's evidence prose is close to other records in the same group,
which is useful for down-weighting template-like narratives.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import re
from collections import defaultdict
from pathlib import Path


TEXT_FIELDS = ("original_text", "text_for_scoring", "window_text_concatenated", "notes")
CHECKPOINT_TOKEN_RE = re.compile(
    r"(\b(?:checkpoint|batch|topup)\b|[_\-\s]?(?:W|X|Y|Z|AA|AB|AC|AD)\d{1,3}\b)",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute text novelty scores for attestation rows.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument(
        "--group-by",
        default="brand_or_category",
        choices=["brand_or_category", "source_id", "source_ref"],
    )
    parser.add_argument("--similarity-metric", default="jaccard", choices=["jaccard", "seqmatcher"])
    parser.add_argument("--max-comparisons-per-record", type=int, default=200)
    parser.add_argument("--no-normalize-brand", action="store_true")
    parser.add_argument("--out-csv", default="reports/novelty_scores.csv")
    return parser.parse_args()


def read_csv(path: str) -> tuple[list[str], list[dict]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: str, fieldnames: list[str], rows: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_ref(row: dict) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or row.get("source_name")
        or ""
    ).strip()


def normalize_text(text: str) -> str:
    text = re.sub(r"https?://\S+", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def evidence_text(row: dict) -> str:
    for field in TEXT_FIELDS:
        value = normalize_text(row.get(field, ""))
        if value:
            return value
    return ""


def normalize_brand(brand: str, enabled: bool) -> str:
    brand = re.sub(r"\s+", " ", brand or "").strip()
    if not enabled:
        return brand
    brand = CHECKPOINT_TOKEN_RE.sub(" ", brand)
    brand = re.sub(r"\s+", " ", brand).strip(" _-/")
    return brand


def grouping_key(row: dict, group_by: str, normalize_brand_enabled: bool) -> str:
    if group_by == "source_ref":
        return source_ref(row)
    if group_by == "source_id":
        return (row.get("source_id") or source_ref(row)).strip()
    return normalize_brand((row.get("brand_or_category") or row.get("brand") or "").strip(), normalize_brand_enabled)


def token_jaccard(left: str, right: str) -> float:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def similarity(left: str, right: str, metric: str) -> float:
    if metric == "seqmatcher":
        return difflib.SequenceMatcher(None, left, right).ratio()
    return token_jaccard(left, right)


def main() -> None:
    args = parse_args()
    input_fields, records = read_csv(args.attestations)
    normalize_brand_enabled = not args.no_normalize_brand

    groups: dict[str, list[int]] = defaultdict(list)
    texts: list[str] = []
    for idx, record in enumerate(records):
        texts.append(evidence_text(record))
        key = grouping_key(record, args.group_by, normalize_brand_enabled)
        if key:
            groups[key].append(idx)

    for idx, record in enumerate(records):
        key = grouping_key(record, args.group_by, normalize_brand_enabled)
        peers = [peer for peer in groups.get(key, []) if peer != idx and texts[peer]]
        text = texts[idx]
        if not text:
            record["novelty_score"] = "0.5000"
            record["avg_text_similarity"] = ""
            record["novelty_group_size"] = str(len(groups.get(key, [])))
            record["novelty_group_key"] = key
            continue
        if not peers:
            record["novelty_score"] = "1.0000"
            record["avg_text_similarity"] = "0.0000"
            record["novelty_group_size"] = str(len(groups.get(key, [])))
            record["novelty_group_key"] = key
            continue
        if len(peers) > args.max_comparisons_per_record:
            peers = peers[: args.max_comparisons_per_record]
        sims = [similarity(text, texts[peer], args.similarity_metric) for peer in peers]
        avg_sim = sum(sims) / len(sims) if sims else 0.0
        record["novelty_score"] = f"{max(0.0, min(1.0, 1.0 - avg_sim)):.4f}"
        record["avg_text_similarity"] = f"{avg_sim:.4f}"
        record["novelty_group_size"] = str(len(groups.get(key, [])))
        record["novelty_group_key"] = key

    out_fields = list(input_fields)
    for field in ("novelty_score", "avg_text_similarity", "novelty_group_size", "novelty_group_key"):
        if field not in out_fields:
            out_fields.append(field)
    write_csv(args.out_csv, out_fields, records)

    low_novelty = sum(1 for row in records if float(row.get("novelty_score") or 0.0) < 0.35)
    print(
        f"Novelty scores saved to {args.out_csv}. "
        f"Records={len(records)}, low_novelty_lt_0.35={low_novelty}."
    )


if __name__ == "__main__":
    main()
