#!/usr/bin/env python3
"""Compute historical lexical/branding/ownership binding indices."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", required=True)
    parser.add_argument("--ownership", default="")
    parser.add_argument("--out-dir", default="reports/binding")
    return parser.parse_args()


def usable(row: dict) -> bool:
    return (row.get("verification_level") or "verified").lower() in {"verified", "probable", ""}


def read_csv(path: str) -> list[dict]:
    if not path or not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def main() -> None:
    args = parse_args()
    attest = [r for r in read_csv(args.attestations) if usable(r)]
    ownership = read_csv(args.ownership)
    owner_by_brand = {
        (r.get("brand") or "").strip().lower(): r.get("ownership_category", "")
        for r in ownership
        if r.get("brand")
    }
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in attest:
        period = row.get("period") or ""
        corridor = row.get("corridor") or row.get("region") or ""
        groups[(period, corridor)].append(row)

    rows = []
    for (period, corridor), group_rows in sorted(groups.items()):
        lexical = []
        branding = []
        owning = []
        for row in group_rows:
            dish_present = 1.0 if (row.get("dish_marker") or row.get("matched_dish_markers") or "").strip() else 0.0
            taiwan_present = 1.0 if (row.get("taiwan_marker") or row.get("matched_taiwan_markers") or "").strip() else 0.0
            try:
                proximity = float(row.get("lexical_proximity") or "")
            except ValueError:
                proximity = 1.0 if dish_present and taiwan_present else 0.0
            lexical.append(dish_present * taiwan_present * proximity)
            brand = (row.get("brand_or_category") or "").lower()
            branding.append(1.0 if taiwan_present and any(k in brand for k in ["台", "taiwan", "formosa", "寶島", "宝岛"]) else 0.0)
            owner = owner_by_brand.get(brand, row.get("ownership_category") or "")
            owning.append(1.0 if owner == "Taiwan_capital" else 0.0)
        lexical_index = mean(lexical)
        branding_index = mean(branding)
        ownership_index = mean(owning)
        rows.append(
            {
                "period": period,
                "corridor": corridor,
                "n_attestations": len(group_rows),
                "lexical_binding_index": f"{lexical_index:.4f}",
                "branding_binding_index": f"{branding_index:.4f}",
                "ownership_binding_index": f"{ownership_index:.4f}",
                "historical_binding_index": f"{(0.5 * lexical_index + 0.25 * branding_index + 0.25 * ownership_index):.4f}",
            }
        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "historical_binding_index.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["period", "corridor", "n_attestations", "lexical_binding_index", "branding_binding_index", "ownership_binding_index", "historical_binding_index"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()

