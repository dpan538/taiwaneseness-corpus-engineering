#!/usr/bin/env python3
"""Fetch TCMB-style JSON API results into raw/json and a manifest.

This is a generic manifesting wrapper. Actual TCMB access may require an API
key, fixed IP, or endpoint adjustment; failures are explicit and should be
logged rather than treated as absence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="https://tcmb.culture.tw/zh-tw/OpenApi")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--keywords", default="魯肉飯,滷肉飯,肉燥飯")
    parser.add_argument("--year-start", type=int, default=1946)
    parser.add_argument("--year-end", type=int, default=1987)
    parser.add_argument("--out-dir", default="raw/json/tcmb")
    parser.add_argument("--manifest", default="raw/manifests/raw_capture_manifest.jsonl")
    parser.add_argument("--delay", type=float, default=1.5)
    return parser.parse_args()


def fetch_json(endpoint: str, params: dict[str, str]) -> dict:
    url = endpoint + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "TaiwanesenessCorpusResearch/0.1"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = Path(args.manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    written = 0

    with manifest.open("a", encoding="utf-8") as mf:
        for keyword in keywords:
            params = {
                "q": keyword,
                "start_date": f"{args.year_start}-01-01",
                "end_date": f"{args.year_end}-12-31",
            }
            if args.api_key:
                params["api_key"] = args.api_key
            data = fetch_json(args.endpoint, params)
            digest = hashlib.sha1(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
            path = out_dir / f"tcmb_{digest}.json"
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            mf.write(
                json.dumps(
                    {
                        "capture_id": f"TCMB_{digest}",
                        "source_id": "TCMB",
                        "search_id": "",
                        "capture_date": date.today().isoformat(),
                        "artifact_type": "json",
                        "local_path": str(path),
                        "sha256": digest,
                        "http_status": 200,
                        "content_type": "application/json",
                        "page_or_frame": "",
                        "ocr_confidence_mean": "",
                        "notes": f"keyword={keyword}; years={args.year_start}-{args.year_end}",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            written += 1
            time.sleep(args.delay)
    print(json.dumps({"json_files": written, "manifest": str(manifest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

