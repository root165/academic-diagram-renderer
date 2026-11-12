#!/usr/bin/env python3
"""Check that an SVG diagram uses only grayscale colours.

The checker is intentionally renderer-agnostic: it reads colour tokens from the
SVG rather than trusting the source file. It is an acceptance check, not a
replacement for visual inspection.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HEX_RE = re.compile(r"#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})\b")
RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})")
COLOR_ATTR_RE = re.compile(
    r"(?:fill|stroke|stop-color|flood-color|lighting-color|color|background(?:-color)?)\s*[:=]\s*[\"']?([A-Za-z]+)",
    re.IGNORECASE,
)
GRAY_NAMES = {
    "white", "black", "gray", "grey", "silver", "gainsboro", "whitesmoke",
    "transparent", "none", "currentcolor", "inherit",
}
CHROMATIC_NAMES = {
    "red", "blue", "green", "yellow", "orange", "purple", "pink", "brown",
    "cyan", "magenta", "lime", "teal", "navy", "maroon", "olive", "aqua",
    "fuchsia", "gold", "coral", "salmon", "violet", "indigo", "turquoise",
}


def normalize_hex(token: str) -> str | None:
    value = token.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) == 8:
        value = value[:6]
    if len(value) != 6:
        return None
    return f"#{value.upper()}"


def rgb_from_hex(value: str) -> tuple[int, int, int]:
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.input.suffix.lower() != ".svg":
        print(json.dumps({"checked": False, "error": "check_monochrome.py currently accepts SVG only."}, ensure_ascii=False))
        return 2
    try:
        text = args.input.read_text(encoding="utf-8")
    except OSError as exc:
        print(json.dumps({"checked": False, "error": str(exc)}, ensure_ascii=False))
        return 2

    counts: Counter[str] = Counter()
    for token in HEX_RE.findall(text):
        normalized = normalize_hex(token)
        if normalized:
            counts[normalized] += 1
    for match in RGB_RE.findall(text):
        try:
            r, g, b = (int(part) for part in match)
        except ValueError:
            continue
        if all(0 <= value <= 255 for value in (r, g, b)):
            counts[f"#{r:02X}{g:02X}{b:02X}"] += 1
    for name in COLOR_ATTR_RE.findall(text):
        lowered = name.lower()
        if lowered in CHROMATIC_NAMES:
            counts[f"named:{lowered}"] += 1
        elif lowered in GRAY_NAMES:
            continue

    violations: list[dict[str, object]] = []
    for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        if value.startswith("named:"):
            violations.append({"value": value, "count": count, "reason": "named chromatic colour"})
            continue
        r, g, b = rgb_from_hex(value)
        if not (r == g == b):
            violations.append({"value": value, "count": count, "reason": "non-grayscale RGB"})

    payload = {
        "input": str(args.input),
        "monochrome": not violations,
        "colors": [{"value": value, "count": count} for value, count in sorted(counts.items())],
        "violations": violations,
        "summary": {"distinct_colors": len(counts), "violations": len(violations)},
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
