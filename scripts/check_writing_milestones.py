#!/usr/bin/env python3
"""Check which paper sections are write-ready from current corpus files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestations", default="data/harvested/combined_attestations_working.csv")
    parser.add_argument("--source-registry", default="data/source_registry.csv")
    parser.add_argument("--manifest", default="raw/manifests/raw_capture_manifest.jsonl")
    parser.add_argument("--negative", default="data/negative_searches.csv")
    parser.add_argument("--ownership", default="data/ownership_capital_events.csv")
    parser.add_argument("--merchants", default="data/merchant_platform_records.csv")
    parser.add_argument("--reviews", default="data/consumer_reviews.csv")
    parser.add_argument("--out-csv", default="reports/writing_milestones.csv")
    parser.add_argument("--out-md", default="reports/writing_milestones.md")
    return parser.parse_args()


def read_csv(path: str) -> list[dict]:
    if not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_jsonl(path: str) -> int:
    if not Path(path).exists():
        return 0
    with Path(path).open(encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def usable(row: dict) -> bool:
    return (row.get("verification_level") or "verified").lower() in {"verified", "probable", ""}


def year(row: dict) -> int | None:
    try:
        return int(float(row.get("year") or ""))
    except ValueError:
        return None


def phase(row: dict) -> str:
    y = year(row)
    if y is not None:
        if 1946 <= y <= 1987:
            return "1946_1987"
        if 1988 <= y <= 2014:
            return "1987_2015"
        if 2015 <= y <= 2025:
            return "2015_2025"
    p = row.get("period") or ""
    if "1946" in p and "1987" in p:
        return "1946_1987"
    if "1987" in p and "2015" in p:
        return "1987_2015"
    if "2015" in p and "2025" in p:
        return "2015_2025"
    return p


def time_bin(row: dict) -> str:
    y = year(row)
    if y is None:
        return "UNKNOWN"
    if 1946 <= y <= 1959:
        return "1946-1959"
    if 1960 <= y <= 1969:
        return "1960-1969"
    if 1970 <= y <= 1979:
        return "1970-1979"
    if 1980 <= y <= 1987:
        return "1980-1987"
    if 1988 <= y <= 1995:
        return "1988-1995"
    if 1996 <= y <= 2005:
        return "1996-2005"
    if 2006 <= y <= 2014:
        return "2006-2014"
    if 2015 <= y <= 2017:
        return "2015-2017"
    if 2018 <= y <= 2020:
        return "2018-2020"
    if 2021 <= y <= 2025:
        return "2021-2025"
    return "OUT_OF_SCOPE"


def city(row: dict) -> str:
    return row.get("city") or row.get("province") or ""


def write_rows(path: str, rows: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fields = ["milestone", "status", "metric", "value", "threshold", "notes"]
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows: list[dict]) -> str:
    fields = ["milestone", "status", "metric", "value", "threshold", "notes"]
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    attest = read_csv(args.attestations)
    usable_rows = [r for r in attest if usable(r)]
    sources = read_csv(args.source_registry)
    negative = read_csv(args.negative)
    ownership = read_csv(args.ownership)
    merchants = read_csv(args.merchants)
    reviews = read_csv(args.reviews)

    rows: list[dict] = []

    def add(milestone: str, passed: bool, metric: str, value, threshold, notes: str = "") -> None:
        rows.append(
            {
                "milestone": milestone,
                "status": "pass" if passed else "fail",
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "notes": notes,
            }
        )

    negative_corridors = {r.get("corridor") for r in negative}
    add("M1_method_write_ready", len(sources) >= 15, "source_registry_records", len(sources), ">=15")
    add("M1_method_write_ready", count_jsonl(args.manifest) >= 50, "raw_manifest_records", count_jsonl(args.manifest), ">=50")
    for corridor in ["Korea", "Vietnam", "Latin America"]:
        add(
            "M1_method_write_ready",
            corridor in negative_corridors,
            f"negative_search_{corridor}",
            "present" if corridor in negative_corridors else "missing",
            "present",
        )

    hist = [r for r in usable_rows if phase(r) == "1946_1987"]
    hist_bins = Counter(time_bin(r) for r in hist)
    hist_cities = Counter(city(r) for r in hist)
    add("M2_1946_1987_exploratory_ready", len(hist) >= 350, "usable_1946_1987", len(hist), ">=350")
    verification_share = len(usable_rows) / len(attest) * 100 if attest else 0
    add("M2_1946_1987_exploratory_ready", verification_share >= 60, "verified_probable_share", f"{verification_share:.2f}", ">=60%")
    bins_over_20 = sum(1 for b in ["1946-1959", "1960-1969", "1970-1979", "1980-1987"] if hist_bins[b] >= 20)
    add("M2_1946_1987_exploratory_ready", bins_over_20 >= 3, "time_bins_ge_20", bins_over_20, ">=3")
    for c in ["Taipei", "Tainan", "Kaohsiung"]:
        add("M2_1946_1987_exploratory_ready", hist_cities[c] >= 30, f"{c}_records", hist_cities[c], ">=30")

    add("M2b_1946_1987_stronger_claim_ready", len(hist) >= 600, "usable_1946_1987", len(hist), ">=600")
    add("M2b_1946_1987_stronger_claim_ready", verification_share >= 80, "verified_probable_share", f"{verification_share:.2f}", ">=80%")
    add("M2b_1946_1987_stronger_claim_ready", all(hist_bins[b] >= 20 for b in ["1946-1959", "1960-1969", "1970-1979", "1980-1987"]), "all_time_bins_ge_20", dict(hist_bins), "all four >=20")

    mobility = [r for r in usable_rows if phase(r) == "1987_2015"]
    mobility_bins = Counter(time_bin(r) for r in mobility)
    mobility_corridors = Counter(r.get("corridor") or r.get("region") or "" for r in mobility)
    add("M3_1987_2015_exploratory_ready", len(mobility) >= 400, "usable_1987_2015", len(mobility), ">=400")
    add("M3_1987_2015_exploratory_ready", sum(1 for _, n in mobility_corridors.items() if n >= 50) >= 3, "mainland_corridors_ge_50", dict(mobility_corridors), ">=3 corridors")
    add("M3_1987_2015_exploratory_ready", sum(1 for b in ["1988-1995", "1996-2005", "2006-2014"] if mobility_bins[b] >= 100) >= 2, "time_bins_ge_100", dict(mobility_bins), ">=2 bins")

    platform_target = [m for m in merchants if (m.get("experimental_group") or "") == "target_taiwan_lu_rou_fan"]
    control_a = [m for m in merchants if (m.get("experimental_group") or "") == "control_same_dish_no_taiwan"]
    control_b = [m for m in merchants if (m.get("experimental_group") or "") == "control_taiwan_other_dish"]
    ownership_brands = {(r.get("brand") or r.get("brand_or_category") or "").strip().lower() for r in ownership if (r.get("brand") or r.get("brand_or_category") or "").strip()}
    merchant_brands = {(m.get("shop_name") or m.get("brand") or "").strip().lower() for m in merchants if (m.get("shop_name") or m.get("brand") or "").strip()}
    own_match = len(merchant_brands & ownership_brands) / len(merchant_brands) * 100 if merchant_brands else 0
    add("M4_platform_reference_ready", len(platform_target) >= 60, "target_merchants", len(platform_target), ">=60")
    add("M4_platform_reference_ready", len(control_a) >= 30, "control_a_merchants", len(control_a), ">=30")
    add("M4_platform_reference_ready", len(control_b) >= 30, "control_b_merchants", len(control_b), ">=30")
    add("M4_platform_reference_ready", len(reviews) >= 800, "reviews", len(reviews), ">=800")
    add("M4_platform_reference_ready", own_match >= 40, "platform_ownership_matching_rate", f"{own_match:.2f}", ">=40%")

    write_rows(args.out_csv, rows)
    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text(
        "# Writing Milestones\n\n"
        + md_table(rows)
        + "\n\n## Interpretation\n\n"
        + "- A failed milestone does not stop writing entirely; it limits what kind of claims can be written.\n"
        + "- If M2 passes but M2b fails, the 1946-1987 chapter should be explicitly exploratory.\n"
        + "- If M3 fails after sustained collection, downgrade 1987-2015 to a transition/case-discussion layer.\n",
        encoding="utf-8",
    )
    print(json.dumps({"out_csv": args.out_csv, "out_md": args.out_md, "checks": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

