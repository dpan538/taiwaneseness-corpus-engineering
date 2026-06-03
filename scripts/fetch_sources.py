#!/usr/bin/env python3
"""Fetch allowed public URLs with robots.txt checks and source logging.

This is a conservative acquisition scaffold, not a bypass tool. It does not
handle logins, captchas, hidden APIs, or anti-bot circumvention. Use it for
public pages whose terms and robots rules permit automated access.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path


DEFAULT_USER_AGENT = "TaiwanesenessLuRouFanResearchBot/0.1 contact: local-research"


def safe_filename(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.replace(":", "_") or "unknown-host"
    return f"{host}_{digest}.html"


def robots_url_for(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))


def allowed_by_robots(url: str, user_agent: str) -> tuple[bool, str]:
    robots_url = robots_url_for(url)
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception:
        return False, f"robots_unreadable:{robots_url}"
    return parser.can_fetch(user_agent, url), robots_url


def fetch(url: str, user_agent: str, timeout: int) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        return int(status), response.read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", required=True, help="CSV with source_url column")
    parser.add_argument("--output-dir", default="data/raw/fetched_pages")
    parser.add_argument("--log", default="data/data_log_fetches.csv")
    parser.add_argument("--delay", type=float, default=5.0)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    args = parser.parse_args()

    sources_path = Path(args.sources)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with sources_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        if "source_url" not in (reader.fieldnames or []):
            raise SystemExit("Sources CSV must include source_url")
        source_rows = list(reader)

    log_rows: list[dict] = []
    for row in source_rows:
        url = (row.get("source_url") or "").strip()
        if not url:
            continue

        allowed, robots_ref = allowed_by_robots(url, args.user_agent)
        log = {
            "source_url": url,
            "capture_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "robots_ref": robots_ref,
            "robots_allowed": "1" if allowed else "0",
            "status": "",
            "output_path": "",
            "error": "",
        }

        if not allowed:
            log["error"] = "blocked_or_unreadable_by_robots"
            log_rows.append(log)
            continue

        try:
            status, body = fetch(url, args.user_agent, args.timeout)
            filename = safe_filename(url)
            out_path = output_dir / filename
            out_path.write_bytes(body)
            log["status"] = str(status)
            log["output_path"] = str(out_path)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            log["error"] = repr(exc)
        log_rows.append(log)
        time.sleep(args.delay)

    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source_url",
        "capture_time",
        "robots_ref",
        "robots_allowed",
        "status",
        "output_path",
        "error",
    ]
    with log_path.open("w", encoding="utf-8", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(log_rows)


if __name__ == "__main__":
    main()
