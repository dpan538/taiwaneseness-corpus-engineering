#!/usr/bin/env python3
"""Rule-based ownership classifier with evidence traces.

This is a heuristic triage tool, not a final capital-origin proof. It avoids
surname-based inference because surnames are not discriminative evidence.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


TAIWAN_EVIDENCE = [
    "台灣",
    "台湾",
    "臺灣",
    "Taiwan",
    "Taipei",
    "台北",
    "臺北",
    "高雄",
    "台中",
    "臺中",
    "台南",
    "臺南",
]

THEME_ONLY_TERMS = [
    "台湾小吃",
    "台灣小吃",
    "台式",
    "台味",
    "宝岛",
    "寶島",
    "夜市",
    "古早味",
]

INTERMEDIARY_TERMS = ["香港", "Hong Kong", "开曼", "開曼", "Cayman", "英属维尔京", "英屬維京", "BVI"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify merchant/company ownership heuristically.")
    parser.add_argument("--input", required=True, help="CSV with company/registry fields.")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms if term)


def classify(row: dict[str, str]) -> tuple[str, float, list[str]]:
    company = row.get("operating_company") or row.get("company_name") or ""
    applicant = row.get("trademark_applicant") or ""
    founder = row.get("founder_origin") or row.get("founder_bio") or ""
    shareholders = row.get("shareholder_names") or ""
    address = row.get("registration_addr") or row.get("registered_address") or ""
    evidence = row.get("evidence_text") or ""
    brand_text = " ".join(
        [
            row.get("brand") or "",
            row.get("shop_name") or "",
            row.get("merchant_description") or "",
        ]
    )

    rules: list[str] = []
    score = 0

    if has_any(" ".join([applicant, address, company]), TAIWAN_EVIDENCE):
        score += 45
        rules.append("official_company_or_trademark_taiwan_evidence")
    if has_any(founder, TAIWAN_EVIDENCE):
        score += 35
        rules.append("founder_biography_taiwan_evidence")
    if has_any(evidence, ["台资", "台資", "台湾资本", "台灣資本", "Taiwan capital"]):
        score += 35
        rules.append("explicit_taiwan_capital_text")
    if has_any(" ".join([shareholders, applicant, address]), INTERMEDIARY_TERMS):
        score += 10
        rules.append("third_place_intermediary_weak_signal")
    if has_any(brand_text, THEME_ONLY_TERMS):
        score += 15
        rules.append("taiwan_theme_branding_only")

    if score >= 70 and any("official" in r or "capital" in r for r in rules):
        return "Taiwan_capital", min(score / 100, 1.0), rules
    if "third_place_intermediary_weak_signal" in rules and score >= 45:
        return "HK_intermediary", min(score / 100, 1.0), rules
    if "taiwan_theme_branding_only" in rules and score < 70:
        return "mainland_Taiwan_themed", min(score / 100, 1.0), rules
    return "unknown", min(score / 100, 1.0), rules


def main() -> None:
    args = parse_args()
    with Path(args.input).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_rows = []
    for row in rows:
        category, confidence, rules = classify(row)
        enriched = dict(row)
        enriched["ownership_category_predicted"] = category
        enriched["ownership_confidence"] = f"{confidence:.3f}"
        enriched["ownership_rules_fired"] = "|".join(rules)
        out_rows.append(enriched)

    fields = fieldnames + [
        "ownership_category_predicted",
        "ownership_confidence",
        "ownership_rules_fired",
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)


if __name__ == "__main__":
    main()

