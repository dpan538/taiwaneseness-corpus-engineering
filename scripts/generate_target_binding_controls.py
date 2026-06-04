#!/usr/bin/env python3
"""Build target-dish weak/no-binding controls from existing attestations.

This does not fabricate negative evidence. It re-labels already captured
Taiwan-context rows for a narrower analytical question: whether the target
dish family (lu rou fan / rouzao fan) is explicitly bound to Taiwaneseness.

Rows with Taiwan context but no target dish term become controls
(`target_binding_raw = 0`). Rows with both Taiwan context and a target dish
term become positives (`target_binding_raw = 1`). The original attestation CSV
is left untouched; outputs are analysis overlays.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_PERIOD = "1946-1987_taiwan_side_formation"
DEFAULT_TARGET_REGEX = (
    r"滷肉飯|卤肉饭|魯肉飯|鲁肉饭|肉燥飯|肉燥饭|肉臊飯|肉臊饭|"
    r"lu\s*rou\s*fan|rou\s*zao|rouzao|luroufan|ルーローハン|魯肉"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate target-dish controls and analysis overlay.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--period", default=DEFAULT_PERIOD)
    parser.add_argument("--target-regex", default=DEFAULT_TARGET_REGEX)
    parser.add_argument("--max-controls", type=int, default=100)
    parser.add_argument("--prefer-primary", action="store_true", default=True)
    parser.add_argument("--include-corridors", nargs="*", default=[])
    parser.add_argument("--out-controls", default="working/historical_target_controls_round_011_candidates.csv")
    parser.add_argument("--out-analysis", default="working/round_011_target_binding_analysis_dataset.csv")
    parser.add_argument("--out-summary-json", default="reports/round_011_target_controls_summary.json")
    parser.add_argument("--out-summary-md", default="reports/round_011_target_controls_summary.md")
    return parser.parse_args()


def period_matches(value: str, requested: str) -> bool:
    if not requested:
        return True
    value = value or ""
    return value == requested or requested in value or value in requested


def parse_year(row: dict[str, str]) -> int:
    try:
        return int(float((row.get("year") or "").strip()))
    except ValueError:
        return 9999


def source_ref(row: dict[str, str]) -> str:
    return (
        row.get("source_url")
        or row.get("source_url_or_archive_ref")
        or row.get("source_ref")
        or row.get("source_id")
        or ""
    ).strip()


def text_blob(row: dict[str, str]) -> str:
    fields = [
        "brand_or_category",
        "original_text",
        "text_for_scoring",
        "dish_marker",
        "taiwan_marker",
        "notes",
        "source_name",
    ]
    return " ".join((row.get(field) or "") for field in fields)


def has_taiwan_context(row: dict[str, str]) -> bool:
    explicit = (row.get("taiwan_marker") or "").strip()
    if explicit:
        return True
    blob = text_blob(row).lower()
    return any(
        marker in blob
        for marker in [
            "taiwan",
            "taiwanese",
            "formosa",
            "台灣",
            "台湾",
            "台菜",
            "台式",
            "臺灣",
            "台湾料理",
            "taipei",
            "台北",
            "台南",
            "tainan",
            "kaohsiung",
            "高雄",
        ]
    )


def dedupe_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        source_ref(row).lower().rstrip("/"),
        (row.get("year") or "").strip(),
        (row.get("brand_or_category") or "").strip().lower(),
    )


def stratified_controls(candidates: list[dict[str, str]], max_controls: int) -> list[dict[str, str]]:
    """Select controls across year bins and corridors while prioritizing primary rows."""
    def score(row: dict[str, str]) -> tuple[int, int, str, str]:
        authority = (row.get("authority_level") or "").lower()
        primary_rank = 0 if authority == "primary" else 1
        source_type = (row.get("source_type") or "").lower()
        archive_rank = 0 if any(x in source_type for x in ["newspaper", "archive", "scan", "photo"]) else 1
        return (primary_rank, archive_rank, f"{parse_year(row):04d}", source_ref(row))

    buckets: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in sorted(candidates, key=score):
        year_bin = (parse_year(row) // 5) * 5
        buckets[((row.get("corridor") or "unknown"), year_bin)].append(row)

    selected: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    while len(selected) < max_controls:
        changed = False
        for key in sorted(buckets):
            if len(selected) >= max_controls:
                break
            bucket = buckets[key]
            while bucket:
                row = bucket.pop(0)
                dkey = dedupe_key(row)
                if dkey in seen:
                    continue
                seen.add(dkey)
                selected.append(row)
                changed = True
                break
        if not changed:
            break
    return selected


def write_csv(path: str, fields: list[str], rows: list[dict[str, str]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    target_re = re.compile(args.target_regex, re.IGNORECASE)
    with Path(args.attestations).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        source_rows = list(reader)

    positives: list[dict[str, str]] = []
    control_candidates: list[dict[str, str]] = []
    for row in source_rows:
        if args.period and not period_matches(row.get("period", ""), args.period):
            continue
        if args.include_corridors and (row.get("corridor") or "") not in args.include_corridors:
            continue
        if not has_taiwan_context(row):
            continue
        blob = text_blob(row)
        is_target = bool(target_re.search(blob))
        item = dict(row)
        if is_target:
            item["target_binding_raw"] = "1.0000"
            item["target_control_type"] = "target_positive"
            item["historical_binding_raw"] = "1.0000"
            positives.append(item)
        else:
            item["target_binding_raw"] = "0.0000"
            item["target_control_type"] = "target_dish_absent_taiwan_context"
            item["negative_type"] = "target_dish_absent_taiwan_context"
            item["historical_binding_raw"] = "0.0000"
            item["weighted_historical_binding"] = "0.0000"
            control_candidates.append(item)

    controls = stratified_controls(control_candidates, args.max_controls)
    analysis_rows = positives + controls
    analysis_rows.sort(key=lambda row: (parse_year(row), row.get("corridor", ""), row.get("target_control_type", ""), source_ref(row)))

    out_fields = list(fields)
    for field in ("target_binding_raw", "target_control_type", "negative_type"):
        if field not in out_fields:
            out_fields.append(field)

    write_csv(args.out_controls, out_fields, controls)
    write_csv(args.out_analysis, out_fields, analysis_rows)

    summary = {
        "source_file": args.attestations,
        "period": args.period,
        "target_regex": args.target_regex,
        "positive_rows_available": len(positives),
        "control_candidates_available": len(control_candidates),
        "controls_selected": len(controls),
        "analysis_rows": len(analysis_rows),
        "controls_by_corridor": dict(Counter((row.get("corridor") or "unknown") for row in controls).most_common()),
        "controls_by_authority": dict(Counter((row.get("authority_level") or "unknown") for row in controls).most_common()),
        "controls_by_source_type": dict(Counter((row.get("source_type") or "unknown") for row in controls).most_common(12)),
        "positives_by_corridor": dict(Counter((row.get("corridor") or "unknown") for row in positives).most_common()),
    }
    Path(args.out_summary_json).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_summary_json).open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    md = [
        "# Round 011 Target-Binding Controls",
        "",
        f"Source file: `{args.attestations}`",
        f"Period: `{args.period}`",
        "",
        "## Counts",
        f"- Target positive rows available: {len(positives)}",
        f"- Taiwan-context control candidates available: {len(control_candidates)}",
        f"- Controls selected for this round: {len(controls)}",
        f"- Target analysis overlay rows: {len(analysis_rows)}",
        "",
        "## Control Composition",
        f"- By corridor: {summary['controls_by_corridor']}",
        f"- By authority: {summary['controls_by_authority']}",
        f"- By source type: {summary['controls_by_source_type']}",
        "",
        "## Interpretation",
        "These rows are not new positive evidence. They are already captured Taiwan-context artifacts that do not explicitly bind the target lu rou fan / rouzao fan dish family. They should be used as analytical controls for the target-dish trend and kept separate from the master attestation count.",
    ]
    Path(args.out_summary_md).write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Selected {len(controls)} target controls: {args.out_controls}")
    print(f"Built {len(analysis_rows)} target analysis rows: {args.out_analysis}")
    print(f"Summary written to {args.out_summary_md}")


if __name__ == "__main__":
    main()
