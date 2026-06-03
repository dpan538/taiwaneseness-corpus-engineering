#!/usr/bin/env python3
"""Filter highly similar same-brand records for sensitivity analysis."""

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
    parser = argparse.ArgumentParser(description="Remove template-like duplicate narratives within brand groups.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--similarity-threshold", type=float, default=0.85)
    parser.add_argument("--out-csv", default="data/attestations_filtered.csv")
    parser.add_argument("--dropped-csv", default="reports/template_contamination_dropped.csv")
    parser.add_argument("--no-normalize-brand", action="store_true")
    return parser.parse_args()


def read_csv(path: str) -> tuple[list[str], list[dict]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


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
    return brand or "__no_brand__"


def float_value(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def confidence_rank(value: str) -> float:
    value = (value or "").strip().lower()
    if value in {"high", "verified"}:
        return 0.9
    if value in {"medium", "probable"}:
        return 0.6
    if value in {"low", "candidate"}:
        return 0.25
    return float_value(value, 0.5)


def authority_rank(value: str) -> int:
    return {"primary": 3, "secondary": 2, "tertiary": 1}.get((value or "").strip().lower(), 2)


def record_score(row: dict) -> tuple:
    return (
        authority_rank(row.get("authority_level", "")),
        float_value(row.get("novelty_score", ""), 0.5),
        confidence_rank(row.get("confidence", "")),
        len(evidence_text(row)),
    )


def connected_components(n: int, edges: dict[int, set[int]]) -> list[list[int]]:
    seen: set[int] = set()
    components: list[list[int]] = []
    for start in range(n):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in edges.get(current, set()):
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                stack.append(neighbor)
        components.append(component)
    return components


def main() -> None:
    args = parse_args()
    fields, records = read_csv(args.attestations)
    normalize = not args.no_normalize_brand

    groups: dict[str, list[dict]] = defaultdict(list)
    for row in records:
        brand = row.get("brand_or_category") or row.get("brand") or ""
        groups[normalize_brand(brand, normalize)].append(row)

    kept: list[dict] = []
    dropped: list[dict] = []
    for brand, group in sorted(groups.items()):
        if len(group) <= 1:
            kept.extend(group)
            continue
        texts = [evidence_text(row) for row in group]
        edges: dict[int, set[int]] = defaultdict(set)
        for i, left in enumerate(texts):
            if not left:
                continue
            for j in range(i + 1, len(group)):
                right = texts[j]
                if not right:
                    continue
                sim = difflib.SequenceMatcher(None, left, right).ratio()
                if sim >= args.similarity_threshold:
                    edges[i].add(j)
                    edges[j].add(i)

        for component in connected_components(len(group), edges):
            if len(component) == 1:
                kept.append(group[component[0]])
                continue
            best_idx = max(component, key=lambda idx: record_score(group[idx]))
            best_id = group[best_idx].get("attestation_id", "")
            best_row = dict(group[best_idx])
            best_row["template_component_size"] = str(len(component))
            best_row["template_component_brand"] = brand
            kept.append(best_row)
            for idx in component:
                if idx == best_idx:
                    continue
                item = dict(group[idx])
                item["template_component_brand"] = brand
                item["template_component_size"] = str(len(component))
                item["kept_attestation_id"] = best_id
                item["drop_reason"] = "same_brand_high_text_similarity"
                dropped.append(item)

    out_fields = list(fields)
    for field in ("template_component_size", "template_component_brand"):
        if field not in out_fields:
            out_fields.append(field)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(kept)

    dropped_fields = list(fields)
    for field in ("template_component_brand", "template_component_size", "kept_attestation_id", "drop_reason"):
        if field not in dropped_fields:
            dropped_fields.append(field)
    Path(args.dropped_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.dropped_csv).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=dropped_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(dropped)

    print(
        f"Filtered from {len(records)} to {len(kept)} records. "
        f"Dropped={len(dropped)}. Output: {args.out_csv}"
    )


if __name__ == "__main__":
    main()
