#!/usr/bin/env python3
"""OCR newspaper PDFs listed in a raw capture manifest.

Heavy OCR dependencies are imported lazily so --help works in a fresh env.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", default="raw/ocr/ocr_pages.jsonl")
    parser.add_argument("--max-pages", type=int, default=0, help="0 means all pages")
    return parser.parse_args()


def native_or_ocr_pdf(pdf_path: Path, max_pages: int = 0) -> list[dict]:
    import numpy as np  # type: ignore
    import pdfplumber  # type: ignore

    paddle = None
    try:
        from paddleocr import PaddleOCR  # type: ignore

        paddle = PaddleOCR(lang="ch", use_angle_cls=True, use_gpu=False)
    except Exception:
        paddle = None

    out = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        page_count = len(pdf.pages) if not max_pages else min(max_pages, len(pdf.pages))
        for i in range(page_count):
            page = pdf.pages[i]
            text = page.extract_text() or ""
            engine = "native_pdf_text"
            confidence = ""
            if len(text.strip()) < 50 and paddle is not None:
                image = page.to_image(resolution=300).original
                result = paddle.ocr(np.array(image), cls=True)
                parts = []
                scores = []
                for block in result or []:
                    for line in block or []:
                        if len(line) >= 2:
                            parts.append(line[1][0])
                            scores.append(float(line[1][1]))
                text = " ".join(parts)
                engine = "paddleocr"
                confidence = f"{sum(scores) / len(scores):.3f}" if scores else ""
            out.append({"page_number": i, "engine": engine, "text": text, "ocr_confidence_mean": confidence})
    return out


def main() -> None:
    args = parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with Path(args.manifest).open(encoding="utf-8") as f, out.open("a", encoding="utf-8") as dst:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry.get("artifact_type") != "pdf":
                continue
            pdf_path = Path(entry.get("local_path", ""))
            if not pdf_path.exists():
                continue
            for page in native_or_ocr_pdf(pdf_path, args.max_pages):
                record = {
                    "capture_id": entry.get("capture_id", ""),
                    "source_id": entry.get("source_id", ""),
                    "page_number": page["page_number"],
                    "engine": page["engine"],
                    "text": page["text"],
                    "ocr_confidence_mean": page["ocr_confidence_mean"],
                    "source_ref": str(pdf_path),
                }
                dst.write(json.dumps(record, ensure_ascii=False) + "\n")
                written += 1
    print(json.dumps({"pages_written": written, "out": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

