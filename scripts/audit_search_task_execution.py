#!/usr/bin/env python3
"""Audit whether queued search tasks are actually executable URLs.

The Round 008/009 task plans intentionally contain a mix of direct URLs and
manual search commands. This audit makes that visible instead of treating a
"Search ..." instruction as a completed fetch.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


BLOCKED_MARKERS = ("captcha", "验证码", "blocked", "access denied", "forbidden")


def task_target(row: dict) -> str:
    for field in ("url", "source_url", "url_or_command", "source_url_or_archive_ref"):
        value = (row.get(field) or "").strip()
        if value:
            return value
    return ""


def is_http_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def normalize_iri_url(url: str) -> str:
    """Encode non-ASCII and spaces in an IRI so urllib can request it."""
    split = urllib.parse.urlsplit(url.strip())
    path = urllib.parse.quote(split.path, safe="/%")
    query = urllib.parse.quote(split.query, safe="=&%")
    return urllib.parse.urlunsplit((split.scheme, split.netloc, path, query, split.fragment))


def check_url(url: str, timeout: int = 10) -> dict:
    normalized_url = normalize_iri_url(url)
    req = urllib.request.Request(
        normalized_url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; corpus-audit/1.0; academic-local-check)"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(200_000)
            text = raw.decode("utf-8", errors="ignore")
            lowered = text.lower()
            return {
                "status": getattr(resp, "status", None),
                "content_length": len(raw),
                "blocked": any(marker in lowered for marker in BLOCKED_MARKERS),
                "snippet": text[:160].replace("\n", " "),
                "error": "",
                "normalized_url": normalized_url,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="ignore")
        return {
            "status": exc.code,
            "content_length": len(body),
            "blocked": exc.code in (401, 403, 429) or any(m in body.lower() for m in BLOCKED_MARKERS),
            "snippet": body[:160].replace("\n", " "),
            "error": f"HTTPError: {exc}",
            "normalized_url": normalized_url,
        }
    except Exception as exc:  # noqa: BLE001 - audit should record broad failures
        return {
            "status": "",
            "content_length": 0,
            "blocked": True,
            "snippet": "",
            "error": repr(exc),
            "normalized_url": normalized_url,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit task execution reality for search plans.")
    parser.add_argument("--task-csv", required=True)
    parser.add_argument("--sample-size", type=int, default=80)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out-report", default="reports/execution_audit.csv")
    parser.add_argument("--out-json", default="reports/execution_audit.json")
    args = parser.parse_args()

    with Path(args.task_csv).open(encoding="utf-8-sig", newline="") as handle:
        tasks = list(csv.DictReader(handle))

    if not tasks:
        raise SystemExit("No tasks found in task CSV.")

    for row in tasks:
        row["_target"] = task_target(row)
        row["_is_url"] = is_http_url(row["_target"])

    url_tasks = [row for row in tasks if row["_is_url"]]
    non_url_tasks = [row for row in tasks if not row["_is_url"]]

    random.seed(args.seed)
    sample = random.sample(url_tasks, min(args.sample_size, len(url_tasks))) if url_tasks else []

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_url, row["_target"]): row for row in sample}
        for future in as_completed(futures):
            row = futures[future]
            checked = future.result()
            results.append(
                {
                    "task_id": row.get("task_id", ""),
                    "target": row["_target"],
                    "normalized_target": checked["normalized_url"],
                    "target_type": "url",
                    "status": checked["status"],
                    "content_length": checked["content_length"],
                    "blocked": checked["blocked"],
                    "error": checked["error"],
                    "snippet": checked["snippet"],
                    "source": row.get("source") or row.get("source_name", ""),
                    "keyword": row.get("keyword", ""),
                    "year": row.get("year", ""),
                    "corridor": row.get("corridor", ""),
                }
            )

    # Include a deterministic preview of non-URL tasks in the report.
    for row in non_url_tasks[: min(50, len(non_url_tasks))]:
        results.append(
            {
                "task_id": row.get("task_id", ""),
                "target": row["_target"],
                "normalized_target": "",
                "target_type": "non_url_task",
                "status": "",
                "content_length": 0,
                "blocked": "",
                "error": "not_fetchable_url",
                "snippet": row["_target"][:160],
                "source": row.get("source") or row.get("source_name", ""),
                "keyword": row.get("keyword", ""),
                "year": row.get("year", ""),
                "corridor": row.get("corridor", ""),
            }
        )

    total_checked = len(sample)
    error_count = sum(1 for row in results if row["target_type"] == "url" and (not row["status"] or int(row["status"]) >= 400))
    blocked_count = sum(1 for row in results if row["target_type"] == "url" and row["blocked"] is True)
    empty_count = sum(1 for row in results if row["target_type"] == "url" and int(row["content_length"] or 0) < 500)
    executable_url_ratio = len(url_tasks) / len(tasks)

    if executable_url_ratio < 0.05:
        health = "critical_queue_not_executable"
    elif total_checked and error_count / total_checked > 0.3:
        health = "critical_url_failures"
    elif total_checked and error_count / total_checked > 0.1:
        health = "warning_url_failures"
    else:
        health = "ok"

    summary = {
        "task_csv": args.task_csv,
        "total_tasks": len(tasks),
        "url_tasks": len(url_tasks),
        "non_url_tasks": len(non_url_tasks),
        "executable_url_ratio": round(executable_url_ratio, 4),
        "url_tasks_checked": total_checked,
        "error_rate_among_checked_urls": round(error_count / total_checked, 4) if total_checked else None,
        "blocked_rate_among_checked_urls": round(blocked_count / total_checked, 4) if total_checked else None,
        "empty_page_rate_among_checked_urls": round(empty_count / total_checked, 4) if total_checked else None,
        "health_assessment": health,
    }

    Path(args.out_report).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task_id",
        "target",
        "normalized_target",
        "target_type",
        "status",
        "content_length",
        "blocked",
        "error",
        "snippet",
        "source",
        "keyword",
        "year",
        "corridor",
    ]
    with Path(args.out_report).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)

    with Path(args.out_json).open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    print(
        "Checked task queue: "
        f"{len(tasks)} tasks, {len(url_tasks)} direct URLs, {len(non_url_tasks)} non-URL commands. "
        f"Health: {health}."
    )
    if health.startswith("critical"):
        sys.exit(2)


if __name__ == "__main__":
    main()
