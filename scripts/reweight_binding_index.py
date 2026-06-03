#!/usr/bin/env python3
"""Recompute binding indices with novelty and authority weights."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute novelty/authority-adjusted binding indices.")
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--ownership", default="")
    parser.add_argument("--out-dir", default="reports/binding")
    return parser.parse_args()


def read_csv(path: str) -> list[dict]:
    if not path or not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def usable(row: dict) -> bool:
    return (row.get("verification_level") or "verified").strip().lower() in {"verified", "probable", ""}


def float_value(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def authority_weight(row: dict) -> float:
    if row.get("authority_weight"):
        return float_value(row.get("authority_weight"), 0.5)
    return {"primary": 1.2, "secondary": 0.7, "tertiary": 0.2}.get(
        (row.get("authority_level") or "secondary").strip().lower(),
        0.3,
    )


def analysis_weight(row: dict) -> float:
    novelty = max(0.0, min(1.0, float_value(row.get("novelty_score"), 0.5)))
    authority = max(0.0, min(1.2, authority_weight(row)))
    return (0.7 * novelty) + (0.3 * authority)


def marker_present(row: dict, *fields: str) -> bool:
    return any((row.get(field) or "").strip() for field in fields)


def brand_has_taiwan(row: dict) -> bool:
    brand = (row.get("brand_or_category") or row.get("brand") or "").lower()
    return any(token in brand for token in ("台", "taiwan", "formosa", "寶島", "宝岛"))


def ownership_lookup(rows: list[dict]) -> dict[str, str]:
    out = {}
    for row in rows:
        brand = (row.get("brand") or row.get("brand_or_category") or "").strip().lower()
        if not brand:
            continue
        out[brand] = row.get("ownership_category", "")
    return out


def main() -> None:
    args = parse_args()
    records = [row for row in read_csv(args.attestations) if usable(row)]
    ownership_by_brand = ownership_lookup(read_csv(args.ownership))

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in records:
        period = row.get("period") or ""
        corridor = row.get("corridor") or row.get("region") or ""
        if period and corridor:
            groups[(period, corridor)].append(row)

    out_rows: list[dict] = []
    for (period, corridor), group in sorted(groups.items()):
        lexical_sum = 0.0
        branding_sum = 0.0
        ownership_sum = 0.0
        weight_sum = 0.0
        raw_lexical_sum = 0.0
        raw_branding_sum = 0.0
        raw_ownership_sum = 0.0
        for row in group:
            weight = analysis_weight(row)
            dish = 1.0 if marker_present(row, "dish_marker", "matched_dish_markers") else 0.0
            taiwan = 1.0 if marker_present(row, "taiwan_marker", "matched_taiwan_markers") else 0.0
            proximity = float_value(row.get("lexical_proximity"), 1.0 if dish and taiwan else 0.0)
            lexical = dish * taiwan * proximity
            branding = 1.0 if taiwan and brand_has_taiwan(row) else 0.0
            brand = (row.get("brand_or_category") or row.get("brand") or "").strip().lower()
            owner = ownership_by_brand.get(brand, row.get("ownership_category", ""))
            ownership = 1.0 if owner == "Taiwan_capital" else 0.0

            lexical_sum += lexical * weight
            branding_sum += branding * weight
            ownership_sum += ownership * weight
            weight_sum += weight
            raw_lexical_sum += lexical
            raw_branding_sum += branding
            raw_ownership_sum += ownership

        if weight_sum <= 0:
            continue
        weighted_lexical = lexical_sum / weight_sum
        weighted_branding = branding_sum / weight_sum
        weighted_ownership = ownership_sum / weight_sum
        raw_n = len(group)
        raw_historical = (
            0.5 * (raw_lexical_sum / raw_n)
            + 0.25 * (raw_branding_sum / raw_n)
            + 0.25 * (raw_ownership_sum / raw_n)
            if raw_n
            else 0.0
        )
        weighted_historical = 0.5 * weighted_lexical + 0.25 * weighted_branding + 0.25 * weighted_ownership
        out_rows.append(
            {
                "period": period,
                "corridor": corridor,
                "n_attestations": str(raw_n),
                "effective_n_weighted": f"{weight_sum:.2f}",
                "mean_analysis_weight": f"{(weight_sum / raw_n) if raw_n else 0.0:.4f}",
                "weighted_lexical_binding": f"{weighted_lexical:.4f}",
                "weighted_branding_binding": f"{weighted_branding:.4f}",
                "weighted_ownership_binding": f"{weighted_ownership:.4f}",
                "weighted_historical_binding": f"{weighted_historical:.4f}",
                "unweighted_historical_binding_recomputed": f"{raw_historical:.4f}",
                "weight_delta": f"{(weighted_historical - raw_historical):.4f}",
            }
        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "adjusted_binding_index.csv"
    fields = [
        "period",
        "corridor",
        "n_attestations",
        "effective_n_weighted",
        "mean_analysis_weight",
        "weighted_lexical_binding",
        "weighted_branding_binding",
        "weighted_ownership_binding",
        "weighted_historical_binding",
        "unweighted_historical_binding_recomputed",
        "weight_delta",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Adjusted binding indices saved to {out_path}. Rows={len(out_rows)}.")


if __name__ == "__main__":
    main()
