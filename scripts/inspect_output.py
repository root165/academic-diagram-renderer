#!/usr/bin/env python3
"""Perform lightweight, dependency-free artifact checks; visual QA remains human/agent work."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def inspect(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    result: dict[str, object] = {"input": str(path), "exists": path.exists(), "bytes": len(data), "valid": bool(data), "checks": []}
    suffix = path.suffix.lower()
    if suffix == ".svg":
        head = data[:2048].decode("utf-8", errors="ignore")
        is_svg = "<svg" in head
        result["checks"].append({"name": "svg-root", "passed": is_svg})
        result["valid"] = bool(result["valid"] and is_svg)
        text = data.decode("utf-8", errors="ignore")
        result["text_nodes"] = len(re.findall(r"<text(?:\\s|>)", text))
    elif suffix == ".pdf":
        passed = data.startswith(b"%PDF-")
        result["checks"].append({"name": "pdf-header", "passed": passed})
        result["valid"] = bool(result["valid"] and passed)
    elif suffix == ".png":
        passed = data.startswith(b"\x89PNG\r\n\x1a\n")
        result["checks"].append({"name": "png-header", "passed": passed})
        result["valid"] = bool(result["valid"] and passed)
    else:
        result["checks"].append({"name": "known-format", "passed": False})
        result["valid"] = False
    result["visual_review_required"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = inspect(args.input)
    content = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(content + "\n", encoding="utf-8")
    print(content)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
