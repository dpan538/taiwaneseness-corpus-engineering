#!/usr/bin/env python3
"""Convert registry/trademark/manual company rows into ownership events."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = [
    "event_id",
    "brand",
    "operating_company",
    "event_year",
    "event_date",
    "event_type",
    "founder_origin",
    "ownership_category",
    "capital_origin",
    "mainland_entry_city",
    "registry_source",
    "evidence_text",
    "verification_level",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="data/ownership_capital_events.csv")
    return parser.parse_args()


def text(row: dict, fields: list[str]) -> str:
    return " ".join(row.get(f, "") or "" for f in fields)


def classify(row: dict) -> tuple[str, str]:
    official = text(row, ["company_name", "operating_company", "trademark_applicant", "registered_address", "address"])
    evidence = text(row, ["founder_origin", "founder_bio", "evidence_text", "notes"])
    theme = text(row, ["brand", "shop_name", "merchant_description"])
    if any(k in official for k in ["台灣", "臺灣", "台湾", "Taiwan", "台北", "臺北"]):
        return "Taiwan_capital", "official Taiwan-linked company/trademark/address evidence"
    if any(k in evidence for k in ["台资", "台資", "台湾资本", "台灣資本", "来自台湾", "來自台灣"]):
        return "Taiwan_capital", "explicit founder/capital evidence"
    if any(k in official for k in ["香港", "Hong Kong", "开曼", "開曼", "Cayman", "BVI", "英属维尔京", "英屬維京"]):
        return "HK_intermediary", "third-place intermediary clue; needs corroboration"
    if any(k in theme for k in ["台湾", "台灣", "台式", "台味", "宝岛", "寶島", "古早味"]):
        return "mainland_Taiwan_themed", "Taiwan theme in brand/merchant language without capital proof"
    return "unknown", "no discriminative capital-origin evidence"


def main() -> None:
    args = parse_args()
    with Path(args.input).open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out_rows = []
    for i, row in enumerate(rows, 1):
        category, rule_note = classify(row)
        evidence = row.get("evidence_text") or row.get("notes") or rule_note
        out_rows.append(
            {
                "event_id": row.get("event_id") or f"OWN_{i:06d}",
                "brand": row.get("brand") or row.get("shop_name") or "",
                "operating_company": row.get("operating_company") or row.get("company_name") or "",
                "event_year": row.get("event_year") or row.get("registration_year") or "",
                "event_date": row.get("event_date") or row.get("registration_date") or "",
                "event_type": row.get("event_type") or "incorporated",
                "founder_origin": row.get("founder_origin") or "",
                "ownership_category": row.get("ownership_category") or category,
                "capital_origin": row.get("capital_origin") or "",
                "mainland_entry_city": row.get("mainland_entry_city") or row.get("city") or "",
                "registry_source": row.get("registry_source") or row.get("source_id") or "",
                "evidence_text": evidence,
                "verification_level": row.get("verification_level") or "candidate",
            }
        )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"wrote {len(out_rows)} rows to {out}")


if __name__ == "__main__":
    main()

