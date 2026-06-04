#!/usr/bin/env python3
"""Validate whether a batch task CSV contains executable, reachable URLs.

This is a hard gate for corpus harvesting. Search instructions such as
"Search Taiwan newspaper archive for ..." are counted as non-executable
planning tasks, not progress. Only direct HTTP(S) URLs that return substantial
non-blocked content can pass.
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
from datetime import datetime
from pathlib import Path


URL_FIELDS = ("url", "source_url", "url_or_command", "source_url_or_archive_ref")
BLOCKED_MARKERS = (
    "captcha",
    "验证码",
    "請通過安全驗證",
    "请通过安全验证",
    "access denied",
    "blocked",
    "forbidden",
)


def task_target(row: dict[str, str]) -> str:
    for field in URL_FIELDS:
        value = (row.get(field) or "").strip()
        if value:
            return value
    return ""


def is_direct_url(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def normalize_iri_url(url: str) -> str:
    """Encode non-ASCII and spaces in an IRI so urllib can request it."""
    split = urllib.parse.urlsplit(url.strip())
    path = urllib.parse.quote(split.path, safe="/%")
    query = urllib.parse.quote(split.query, safe="=&%")
    return urllib.parse.urlunsplit((split.scheme, split.netloc, path, query, split.fragment))


def check_url(url: str, timeout: int) -> dict[str, object]:
    normalized_url = normalize_iri_url(url)
    request = urllib.request.Request(
        normalized_url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; corpus-batch-validator/1.0; academic-local-check)"
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(300_000)
            text = raw.decode("utf-8", errors="ignore")
            lowered = text.lower()
            status = getattr(response, "status", None)
            is_blocked = any(marker in lowered for marker in BLOCKED_MARKERS)
            is_empty = len(raw) < 500
            ok = bool(status and 200 <= int(status) < 400 and not is_blocked and not is_empty)
            return {
                "status": status,
                "content_length": len(raw),
                "is_blocked": is_blocked,
                "is_empty": is_empty,
                "ok": ok,
                "error": "",
                "normalized_url": normalized_url,
                "snippet": text[:160].replace("\n", " "),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(8192).decode("utf-8", errors="ignore")
        is_blocked = exc.code in (401, 403, 429) or any(marker in body.lower() for marker in BLOCKED_MARKERS)
        return {
            "status": exc.code,
            "content_length": len(body),
            "is_blocked": is_blocked,
            "is_empty": len(body) < 500,
            "ok": False,
            "error": f"HTTPError: {exc}",
            "normalized_url": normalized_url,
            "snippet": body[:160].replace("\n", " "),
        }
    except Exception as exc:  # noqa: BLE001 - this validator records broad failure causes
        return {
            "status": "",
            "content_length": 0,
            "is_blocked": False,
            "is_empty": True,
            "ok": False,
            "error": repr(exc),
            "normalized_url": normalized_url,
            "snippet": "",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate executable URL reality in a batch task CSV.")
    parser.add_argument("--task-csv", required=True)
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--min-direct-url-ratio", type=float, default=0.20)
    parser.add_argument("--min-ok-rate", type=float, default=0.80)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--out-report", default="reports/batch_validation_report.json")
    parser.add_argument("--out-csv", default="reports/batch_validation_samples.csv")
    parser.add_argument("--out-execution-log", default="")
    args = parser.parse_args()

    with Path(args.task_csv).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("No tasks found in task CSV.")

    for row in rows:
        row["_target"] = task_target(row)
        row["_is_direct_url"] = is_direct_url(row["_target"])

    direct_tasks = [row for row in rows if row["_is_direct_url"]]
    non_executable = [row for row in rows if not row["_is_direct_url"]]
    direct_ratio = len(direct_tasks) / len(rows)

    random.seed(args.seed)
    sample = random.sample(direct_tasks, min(args.sample_size, len(direct_tasks))) if direct_tasks else []

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_row = {executor.submit(check_url, row["_target"], args.timeout): row for row in sample}
        for future in as_completed(future_to_row):
            row = future_to_row[future]
            checked = future.result()
            status = "success" if checked["ok"] else "failure"
            failure_reason = ""
            if not checked["ok"]:
                if checked.get("error"):
                    failure_reason = str(checked["error"])
                elif checked.get("is_blocked"):
                    failure_reason = "blocked_or_access_denied"
                elif checked.get("is_empty"):
                    failure_reason = "empty_or_short_page"
                else:
                    failure_reason = f"http_status_{checked.get('status')}"
            results.append(
                {
                    "task_id": row.get("task_id", ""),
                    "target": row["_target"],
                    "normalized_target": checked["normalized_url"],
                    "execution_status": status,
                    "status": checked["status"],
                    "content_length": checked["content_length"],
                    "is_blocked": checked["is_blocked"],
                    "is_empty": checked["is_empty"],
                    "ok": checked["ok"],
                    "failure_reason": failure_reason,
                    "source": row.get("source") or row.get("source_name", ""),
                    "keyword": row.get("keyword", ""),
                    "year": row.get("year", ""),
                    "corridor": row.get("corridor", ""),
                    "snippet": checked["snippet"],
                }
            )

    ok_count = sum(1 for row in results if row["ok"])
    blocked_count = sum(1 for row in results if row["is_blocked"])
    empty_count = sum(1 for row in results if row["is_empty"] and not row["is_blocked"])
    other_failure_count = len(results) - ok_count - blocked_count - empty_count
    ok_rate = ok_count / len(results) if results else 0.0

    critical_reasons: list[str] = []
    if not direct_tasks:
        critical_reasons.append("no_executable_urls")
    if direct_ratio < args.min_direct_url_ratio:
        critical_reasons.append("direct_url_ratio_below_threshold")
    if results and ok_rate < args.min_ok_rate:
        critical_reasons.append("sampled_ok_rate_below_threshold")
    if results and ok_count == 0:
        critical_reasons.append("no_working_urls_in_sample")

    summary = {
        "task_csv": args.task_csv,
        "validated_at": datetime.now().isoformat(timespec="seconds"),
        "total_tasks": len(rows),
        "direct_url_count": len(direct_tasks),
        "non_executable_count": len(non_executable),
        "direct_url_ratio": round(direct_ratio, 4),
        "sampled_count": len(results),
        "sampled_ok_count": ok_count,
        "sampled_ok_rate": round(ok_rate, 4),
        "sampled_blocked_count": blocked_count,
        "sampled_empty_count": empty_count,
        "sampled_other_failure_count": other_failure_count,
        "critical_failure": bool(critical_reasons),
        "critical_reasons": critical_reasons,
        "recommendation": (
            "STOP - task batch is not executable/reachable enough to count as harvesting progress."
            if critical_reasons
            else "PASS - batch has enough reachable direct URLs to proceed with actual harvesting."
        ),
    }

    Path(args.out_report).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_report).open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    fieldnames = [
        "task_id",
        "target",
        "normalized_target",
        "execution_status",
        "status",
        "content_length",
        "is_blocked",
        "is_empty",
        "ok",
        "failure_reason",
        "source",
        "keyword",
        "year",
        "corridor",
        "snippet",
    ]
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)

    if args.out_execution_log:
        Path(args.out_execution_log).parent.mkdir(parents=True, exist_ok=True)
        log_fields = [
            "task_id",
            "executed_at",
            "execution_status",
            "result_count",
            "accepted_attestation_id",
            "failure_reason",
            "target",
            "status",
            "content_length",
        ]
        with Path(args.out_execution_log).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=log_fields, lineterminator="\n")
            writer.writeheader()
            for row in results:
                writer.writerow(
                    {
                        "task_id": row["task_id"],
                        "executed_at": summary["validated_at"],
                        "execution_status": row["execution_status"],
                        "result_count": 1 if row["ok"] else 0,
                        "accepted_attestation_id": "",
                        "failure_reason": row["failure_reason"],
                        "target": row["target"],
                        "status": row["status"],
                        "content_length": row["content_length"],
                    }
                )

    print(
        f"Validated {len(rows)} tasks: {len(direct_tasks)} direct URLs "
        f"({direct_ratio:.1%}), sampled {len(results)}, OK {ok_count} ({ok_rate:.1%})."
    )
    print(summary["recommendation"])
    if critical_reasons:
        print("Critical reasons: " + ", ".join(critical_reasons))
        sys.exit(2)


if __name__ == "__main__":
    main()
