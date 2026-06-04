#!/usr/bin/env python3
"""
Build a local JCA-oriented readiness pack from existing analysis outputs.

The script does not recompute the research analysis. It inventories figures,
tables, sample-size gates, reproducibility links, and anonymization risks so
the project can be turned into a double-anonymous replication package later.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


FIGURE_RULES = [
    (
        "change_point_candidate_map",
        "Corridor-specific source and semantic regime shifts; use to argue against a single global turning point.",
        "main_text",
        "analysis/change_authority_novelty_outputs/change_point_candidates.csv",
        "scripts/change_point_authority_novelty_analysis.py",
    ),
    (
        "change_points_taiwan_source_structure",
        "Taiwan-side evidence visibility changes by source structure; use to show archive/source-system change.",
        "main_text",
        "analysis/change_authority_novelty_outputs/change_point_candidates.csv",
        "scripts/change_point_authority_novelty_analysis.py",
    ),
    (
        "semantic_family_by_corridor",
        "Different corridors assemble Taiwaneseness through different semantic families.",
        "main_text",
        "analysis/semantic_propagation_live_outputs/semantic_family_by_corridor.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "semantic_family_over_time",
        "Shift from dish attestation toward cuisine/platform labels over time.",
        "main_text",
        "analysis/semantic_propagation_live_outputs/semantic_family_by_time.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "low_binding_time_corridor_heatmap",
        "Weak-binding pockets across time and geography; use as control evidence, not noise.",
        "main_text",
        "analysis/producer_consumer_outliers_outputs/low_binding_outliers.csv",
        "scripts/producer_consumer_outlier_analysis.py",
    ),
    (
        "low_binding_outliers_scatter",
        "Concrete low-binding outliers for close reading and negative/control evidence.",
        "appendix_or_casebook",
        "analysis/producer_consumer_outliers_outputs/low_binding_outliers.csv",
        "scripts/producer_consumer_outlier_analysis.py",
    ),
    (
        "low_binding_pockets",
        "Largest period/corridor/source pockets where attachment is weak.",
        "main_text_if_n_ok",
        "analysis/semantic_propagation_live_outputs/low_binding_pockets.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "leave_one_source_type_out",
        "Sensitivity to source regimes; use to show which evidence systems inflate or suppress binding.",
        "main_text",
        "analysis/semantic_propagation_live_outputs/leave_one_source_type_out.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "weak_binding_share_heatmap",
        "Where weak/no-binding cases cluster by period and corridor.",
        "main_text_if_n_ok",
        "analysis/change_authority_novelty_outputs/binding_bucket_by_corridor_period.csv",
        "scripts/change_point_authority_novelty_analysis.py",
    ),
    (
        "corridor_time_record_volume",
        "Corpus support by corridor and time; use as sample-size warning figure.",
        "appendix",
        "analysis/semantic_propagation_live_outputs/corridor_time_summary.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "corridor_time_primary_share",
        "Primary-source share by corridor and time; use as evidence-quality warning figure.",
        "appendix",
        "analysis/semantic_propagation_live_outputs/corridor_time_summary.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "first_appearance_timeline",
        "First observed appearances by semantic family and corridor; exploratory timing evidence.",
        "main_text_if_n_ok",
        "analysis/semantic_propagation_live_outputs/semantic_first_appearance.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "semantic_entropy_by_corridor",
        "Semantic diversity by corridor; use to distinguish stable labels from mixed discourse.",
        "appendix_or_secondary",
        "analysis/semantic_propagation_live_outputs/corridor_time_summary.csv",
        "analysis/semantic_propagation_live.py",
    ),
    (
        "authority_novelty",
        "Authority-novelty tradeoff; use as methodological robustness and source-bias diagnostic.",
        "appendix_or_methods",
        "analysis/change_authority_novelty_outputs/authority_novelty_empirical_bins.csv",
        "scripts/change_point_authority_novelty_analysis.py",
    ),
    (
        "violin_binding_by_corridor_period",
        "Distribution of binding by corridor and period; useful for showing saturation and uneven variance.",
        "appendix_or_secondary",
        "analysis/change_authority_novelty_outputs/violin_plot_rows.csv",
        "scripts/change_point_authority_novelty_analysis.py",
    ),
    (
        "producer_consumer",
        "Producer-consumer marker transfer; only use if platform linkage and n are documented.",
        "appendix_or_secondary",
        "analysis/producer_consumer_outliers_outputs/producer_consumer_flow.csv",
        "scripts/producer_consumer_outlier_analysis.py",
    ),
]


BASE_ANON_PATTERNS = [
    ("local_user_path", re.compile(r"/Users/[^,\s)]*|/home/[^,\s)]*|/private/var/[^,\s)]*")),
    ("github_url", re.compile(r"https?://github\.com/[^\s)]+", re.IGNORECASE)),
    ("email", re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")),
]


TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".json",
    ".yml",
    ".yaml",
    ".csv",
    ".gitignore",
    ".gitattributes",
}


def read_csv_summary(path: Path) -> tuple[int, list[str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = 0
            for _ in reader:
                rows += 1
            return rows, list(reader.fieldnames or [])
    except Exception:
        return 0, []


def classify_figure(path: Path) -> dict[str, str]:
    name = path.stem
    for needle, claim, placement, input_table, script in FIGURE_RULES:
        if needle in name:
            return {
                "interpretive_claim": claim,
                "recommended_placement": placement,
                "primary_input_table": input_table,
                "source_script": script,
            }
    return {
        "interpretive_claim": "Exploratory figure; inspect manually before using in main text.",
        "recommended_placement": "appendix_or_drop",
        "primary_input_table": "",
        "source_script": "",
    }


def figure_inventory(root: Path) -> list[dict[str, str]]:
    figure_paths = sorted(
        list(root.glob("analysis/**/*.[Pp][Nn][Gg]"))
        + list(root.glob("reports/figures/**/*.[Pp][Nn][Gg]"))
    )
    by_name: dict[str, list[Path]] = {}
    for path in figure_paths:
        by_name.setdefault(path.name, []).append(path)

    def figure_priority(path: Path) -> tuple[int, str]:
        path_str = str(path)
        if "semantic_propagation_live_outputs" in path_str:
            return (0, path_str)
        if "change_authority_novelty_outputs" in path_str:
            return (1, path_str)
        if "producer_consumer_outliers_outputs" in path_str:
            return (2, path_str)
        return (3, path_str)

    rows = []
    for paths in by_name.values():
        path = sorted(paths, key=figure_priority)[0]
        meta = classify_figure(path)
        rows.append(
            {
                "figure_file": str(path.relative_to(root)),
                "figure_name": path.stem,
                "source_script": meta["source_script"],
                "primary_input_table": meta["primary_input_table"],
                "variables_or_view": infer_variables(path.stem),
                "interpretive_claim": meta["interpretive_claim"],
                "recommended_placement": meta["recommended_placement"],
                "status": "candidate",
            }
        )
    return rows


def infer_variables(name: str) -> str:
    parts = []
    if "corridor" in name:
        parts.append("corridor")
    if "time" in name or "year" in name or "appearance" in name or "change" in name:
        parts.append("time")
    if "semantic" in name:
        parts.append("semantic_family")
    if "binding" in name:
        parts.append("binding_index")
    if "source" in name or "authority" in name:
        parts.append("source_regime")
    if "novelty" in name:
        parts.append("novelty_score")
    if "producer" in name or "consumer" in name:
        parts.append("producer_consumer_transfer")
    return "; ".join(parts) if parts else "manual_review_needed"


def table_inventory(root: Path) -> list[dict[str, str]]:
    patterns = [
        "analysis/**/*.[Cc][Ss][Vv]",
        "analysis/**/*.[Jj][Ss][Oo][Nn]",
        "frozen_data_v2/**/*.[Cc][Ss][Vv]",
        "frozen_data_v2/**/*.[Jj][Ss][Oo][Nn]",
        "outputs/**/*.[Cc][Ss][Vv]",
        "reports/trend_diagnosis*/**/*.[Cc][Ss][Vv]",
        "reports/trend_diagnosis*/**/*.[Jj][Ss][Oo][Nn]",
    ]
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(root.glob(pattern))
    rows = []
    for path in sorted(set(paths)):
        if path.suffix.lower() == ".csv":
            count, columns = read_csv_summary(path)
            row_count = str(count)
            column_names = ";".join(columns)
        else:
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
                row_count = "1"
                column_names = ";".join(obj.keys()) if isinstance(obj, dict) else "json_array"
            except Exception:
                row_count = "0"
                column_names = ""
        rows.append(
            {
                "table_file": str(path.relative_to(root)),
                "row_count": row_count,
                "columns": column_names,
                "likely_use": infer_table_use(path),
            }
        )
    return rows


def infer_table_use(path: Path) -> str:
    name = path.name
    parent = path.parent.name
    if "semantic_propagation_cube" in name:
        return "core semantic/time/corridor cube"
    if "corridor_time_summary" in name:
        return "sample-size and source-quality gate"
    if "change_point" in name:
        return "change-point candidate evidence"
    if "low_binding" in name:
        return "weak-binding controls and close-reading candidates"
    if "producer_consumer" in name:
        return "producer-consumer transfer analysis"
    if "binding_by_period" in name or "binding_by_year" in name:
        return "frozen binding index table"
    if "authority_novelty" in name:
        return "source authority and novelty sensitivity"
    if parent.startswith("trend_diagnosis"):
        return "trend diagnostic output"
    return "supporting or audit table"


def gate_label(row_count: int, unique_sources: int | None, grain: str) -> tuple[str, str]:
    if row_count >= 30 and (unique_sources is None or unique_sources >= 5):
        return "main_text_ok", "large enough for descriptive main-text claim"
    if row_count >= 15 and (unique_sources is None or unique_sources >= 3):
        return "main_text_cautious", "usable for cautious descriptive claim"
    if row_count >= 5:
        return "appendix_or_case_context", "show as context; avoid strong inference"
    return "do_not_infer", f"too sparse for {grain} inference"


def sample_size_gate(root: Path) -> list[dict[str, str]]:
    rows = []
    sources = [
        (root / "analysis/semantic_propagation_live_outputs/semantic_propagation_cube.csv", "semantic_cube"),
        (root / "analysis/semantic_propagation_live_outputs/corridor_time_summary.csv", "corridor_time"),
        (root / "frozen_data_v2/binding_by_period_corridor.csv", "period_corridor"),
    ]
    for path, grain in sources:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for rec in reader:
                try:
                    n = int(float(rec.get("row_count", "0") or 0))
                except ValueError:
                    n = 0
                try:
                    unique_sources = int(float(rec.get("unique_sources", ""))) if rec.get("unique_sources") else None
                except ValueError:
                    unique_sources = None
                gate, reason = gate_label(n, unique_sources, grain)
                rows.append(
                    {
                        "input_table": str(path.relative_to(root)),
                        "grain": grain,
                        "period": rec.get("period", ""),
                        "five_year_bin": rec.get("five_year_bin", ""),
                        "corridor": rec.get("corridor", ""),
                        "semantic_family": rec.get("semantic_family", ""),
                        "source_or_discourse_frame": rec.get("discourse_frame", rec.get("source_type", "")),
                        "row_count": str(n),
                        "unique_sources": "" if unique_sources is None else str(unique_sources),
                        "weight_sum": rec.get("weight_sum", ""),
                        "binding_index": rec.get("binding_index", rec.get("weighted_binding_index", "")),
                        "gate": gate,
                        "reason": reason,
                    }
                )
    return rows


def build_anon_patterns(identity_terms: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    patterns = list(BASE_ANON_PATTERNS)
    for term in identity_terms:
        term = term.strip()
        if not term:
            continue
        label = "identity_term"
        patterns.append((label, re.compile(re.escape(term), re.IGNORECASE)))
    return patterns


def redact_text(text: str, patterns: list[tuple[str, re.Pattern[str]]]) -> str:
    redacted = text
    for label, pattern in patterns:
        redacted = pattern.sub(f"<redacted:{label}>", redacted)
    return redacted


def anonymization_scan(
    root: Path,
    patterns: list[tuple[str, re.Pattern[str]]],
    max_findings: int,
    max_findings_per_file: int,
) -> list[dict[str, str]]:
    scan_dirs = ["README.md", "docs", "scripts", "config", "configs", "analysis", "reports", "working"]
    paths: list[Path] = []
    for item in scan_dirs:
        p = root / item
        if p.is_file():
            paths.append(p)
        elif p.is_dir():
            paths.extend(x for x in p.rglob("*") if x.is_file())
    rows = []
    for path in sorted(paths):
        if len(rows) >= max_findings:
            break
        rel = path.relative_to(root)
        if str(rel) == "scripts/build_jca_readiness_pack.py":
            continue
        if str(rel).startswith("reports/jca_readiness/"):
            continue
        if path.suffix and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        file_findings = 0
        for label, pattern in patterns:
            for match in pattern.finditer(text):
                if len(rows) >= max_findings or file_findings >= max_findings_per_file:
                    break
                start = max(0, match.start() - 60)
                end = min(len(text), match.end() + 60)
                snippet = " ".join(redact_text(text[start:end], patterns).split())
                rows.append(
                    {
                        "file": str(path.relative_to(root)),
                        "risk_type": label,
                        "match": f"<redacted:{label}>",
                        "snippet": snippet,
                        "action": "remove_or_replace_for_anonymous_review",
                    }
                )
                file_findings += 1
            if len(rows) >= max_findings or file_findings >= max_findings_per_file:
                break
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text_files(out_dir: Path, figures: list[dict[str, str]], tables: list[dict[str, str]], gates: list[dict[str, str]], anon: list[dict[str, str]]) -> None:
    main_figs = [r for r in figures if r["recommended_placement"].startswith("main_text")]
    sparse = [r for r in gates if r["gate"] == "do_not_infer"]
    cautious = [r for r in gates if r["gate"] in {"main_text_cautious", "appendix_or_case_context"}]

    readiness = f"""# JCA Readiness Report

This local report turns existing outputs into a paper-oriented evidence chain.

## Counts

- Candidate figures inventoried: {len(figures)}
- Tables/results inventoried: {len(tables)}
- Sample-size gate rows: {len(gates)}
- Main-text candidate figures: {len(main_figs)}
- Anonymization risks found: {len(anon)}

## Main-Text Figure Candidates

"""
    for row in main_figs:
        readiness += f"- `{row['figure_file']}`: {row['interpretive_claim']}\n"

    readiness += f"""
## Sample-Size Caution

- Sparse cells marked `do_not_infer`: {len(sparse)}
- Cautious/context cells: {len(cautious)}

Use `sample_size_gate.csv` before making any corridor/time/family claim. The default rule is:

- `main_text_ok`: n >= 30 and at least 5 unique sources when available.
- `main_text_cautious`: n >= 15 and at least 3 unique sources when available.
- `appendix_or_case_context`: n >= 5.
- `do_not_infer`: n < 5.

## Proposed Evidence Chain

1. Define the object as marker binding, not culinary authenticity.
2. Establish corpus/source regimes and evidence gates.
3. Show that shifts are corridor-specific rather than a single global event.
4. Use Taiwan-side source structure to show that evidence visibility changes.
5. Use semantic-family heatmaps to show different assemblies of Taiwaneseness by corridor.
6. Use low-binding controls to distinguish Taiwan-related discourse from attached dish signs.
7. Use source sensitivity and authority/novelty figures as robustness diagnostics.

## Immediate Manuscript Risk

For double-anonymous review, do not cite the public GitHub repository or include author-identifying paths. Build an anonymous replication package from the files listed here.
"""
    (out_dir / "JCA_READINESS.md").write_text(readiness, encoding="utf-8")

    anon_readme = """# Anonymous Replication Package Draft

This is a draft structure for anonymous peer review. Remove author names, personal GitHub handles, local filesystem paths, institution-specific identifiers, and screenshots with account information.

## Contents

- `scripts/`: reproducible processing and analysis scripts.
- `config/`: lexicons, period definitions, and pipeline configuration.
- `data_public_or_sample/`: public metadata or sample rows only, excluding restricted raw captures.
- `figures/`: argument-ready figures.
- `tables/`: derived aggregate tables.
- `reproducibility_manifest.csv`: maps figures/tables to scripts and inputs.
- `data_access_statement.md`: explains what is public, restricted, or derived.
- `ai_use_disclosure.md`: records AI-assisted coding, visualization, and design support.

## Review Note

The public repository and author-identifying archive should be disclosed only after review, or through the journal's required data deposit workflow.
"""
    (out_dir / "README_ANON_DRAFT.md").write_text(anon_readme, encoding="utf-8")

    data_statement = """# Data Access Statement Draft

The replication package provides source metadata, derived aggregate tables, scripts, configuration files, and figures needed to reproduce the computational analysis. Some raw source artifacts are not redistributed because they may be subject to archive access restrictions, platform terms, copyright limitations, or unstable public URLs.

For restricted materials, the package provides source identifiers, source URLs or archive references, dates, source types, search protocols, and derived non-substitutive metadata. The analysis is designed to be auditable through provenance fields, source registry records, negative search logs, and sample-size gates rather than through republication of all raw artifacts.
"""
    (out_dir / "data_access_statement_draft.md").write_text(data_statement, encoding="utf-8")

    ai_statement = """# AI Use Disclosure Draft

AI assistance was used for code review, pipeline design discussion, debugging, analysis planning, and generation or refinement of reproducibility scaffolding. AI assistance was not used as an autonomous source of historical evidence. All accepted records, source classifications, and interpretive claims remain subject to human review.

Before submission, replace this draft with a dated log listing:

- tool/model used;
- dates or date range;
- tasks assisted;
- scripts or notebooks affected;
- human verification steps.
"""
    (out_dir / "ai_use_disclosure_draft.md").write_text(ai_statement, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out-dir", default="reports/jca_readiness")
    parser.add_argument(
        "--identity-term",
        action="append",
        default=[],
        help="Project-specific identity string to flag and redact, e.g. author name or handle. May be repeated.",
    )
    parser.add_argument("--max-anon-findings", type=int, default=200)
    parser.add_argument("--max-anon-findings-per-file", type=int, default=20)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    anon_patterns = build_anon_patterns(args.identity_term)

    figures = figure_inventory(root)
    tables = table_inventory(root)
    gates = sample_size_gate(root)
    anon = anonymization_scan(root, anon_patterns, args.max_anon_findings, args.max_anon_findings_per_file)

    write_csv(
        out_dir / "figure_inventory.csv",
        figures,
        [
            "figure_file",
            "figure_name",
            "source_script",
            "primary_input_table",
            "variables_or_view",
            "interpretive_claim",
            "recommended_placement",
            "status",
        ],
    )
    write_csv(out_dir / "table_inventory.csv", tables, ["table_file", "row_count", "columns", "likely_use"])
    write_csv(
        out_dir / "sample_size_gate.csv",
        gates,
        [
            "input_table",
            "grain",
            "period",
            "five_year_bin",
            "corridor",
            "semantic_family",
            "source_or_discourse_frame",
            "row_count",
            "unique_sources",
            "weight_sum",
            "binding_index",
            "gate",
            "reason",
        ],
    )
    write_csv(out_dir / "anonymization_scan.csv", anon, ["file", "risk_type", "match", "snippet", "action"])

    repro_rows = [
        {
            "artifact": row["figure_file"],
            "artifact_type": "figure",
            "source_script": row["source_script"],
            "primary_input": row["primary_input_table"],
            "claim": row["interpretive_claim"],
            "placement": row["recommended_placement"],
        }
        for row in figures
    ]
    write_csv(
        out_dir / "reproducibility_manifest.csv",
        repro_rows,
        ["artifact", "artifact_type", "source_script", "primary_input", "claim", "placement"],
    )

    write_text_files(out_dir, figures, tables, gates, anon)

    summary = {
        "figure_count": len(figures),
        "table_count": len(tables),
        "sample_gate_rows": len(gates),
        "anonymization_risk_count": len(anon),
        "out_dir": str(out_dir.relative_to(root)),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
