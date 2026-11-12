#!/usr/bin/env python3
"""Render a prevalidated source file; this script never downloads or installs tools."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def graphviz_executable() -> str | None:
    """Resolve the real Graphviz binary; Scoop shims can mangle directed-edge args."""
    override = os.environ.get("GRAPHVIZ_DOT")
    if override:
        return override
    executable = shutil.which("dot")
    if executable and platform.system() == "Windows":
        candidate = Path(executable).parent.parent / "apps" / "graphviz" / "current" / "bin" / "dot.exe"
        if candidate.exists():
            return str(candidate)
    return executable


def command_for(source: Path, output: Path, fmt: str, engine: str = "dot", fixed: bool = False) -> list[str]:
    suffix = source.suffix.lower()
    if suffix == ".puml":
        executable = shutil.which("plantuml")
        if not executable:
            raise RuntimeError("PlantUML command is unavailable. Run discover-tools.ps1; do not install automatically.")
        return [executable, f"-t{fmt}", "-o", str(output.parent), str(source)]
    if suffix == ".dot":
        executable = graphviz_executable()
        if not executable:
            raise RuntimeError("Graphviz dot is unavailable. Run discover-tools.ps1; do not install automatically.")
        # Use `dot -K<engine>` rather than the engine-specific shim: on Windows,
        # Scoop shims for neato/sfdp can accidentally dispatch to dot and silently
        # ignore fixed positions. `dot -Kneato -n2` keeps the requested engine.
        command = [executable, f"-K{engine}"]
        if engine == "neato" and fixed:
            command.append("-n2")
        command.extend([f"-T{fmt}", "-o", str(output), str(source)])
        return command
    if suffix == ".mmd":
        executable = shutil.which("mmdc")
        if not executable:
            raise RuntimeError("Mermaid CLI mmdc is unavailable. Run discover-tools.ps1; do not install automatically.")
        return [executable, "-i", str(source), "-o", str(output)]
    if suffix == ".drawio":
        executable = shutil.which("drawio") or shutil.which("draw.io")
        if not executable:
            raise RuntimeError("Draw.io CLI is unavailable. Run discover-tools.ps1; do not install automatically.")
        return [executable, "--headless", "--export", "--format", fmt, "--output", str(output), str(source)]
    raise RuntimeError(f"Unsupported source suffix {suffix!r}; use .puml, .dot, .mmd, or .drawio.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--format", choices=("svg", "pdf", "png"), default="svg")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--engine", choices=("dot", "neato", "sfdp", "fdp", "circo"), default="dot")
    parser.add_argument("--fixed", action="store_true", help="For neato: honour pos attributes with -n2.")
    args = parser.parse_args()
    source = args.source.resolve()
    output = (args.output or source.with_suffix(f".{args.format}")).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        command = command_for(source, output, args.format, args.engine, args.fixed)
    except RuntimeError as exc:
        print(json_error(str(exc)), file=sys.stderr)
        return 2
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout)
    if completed.returncode:
        print(completed.stderr, file=sys.stderr)
        return completed.returncode
    if not output.exists() and source.suffix.lower() == ".puml":
        generated = source.with_suffix(f".{args.format}")
        if generated.exists() and generated != output:
            generated.replace(output)
    if not output.exists() or output.stat().st_size == 0:
        print(json_error("Renderer returned success but no non-empty output appeared."), file=sys.stderr)
        return 3
    print(output)
    return 0


def json_error(message: str) -> str:
    return '{"rendered": false, "error": ' + repr(message) + '}'


if __name__ == "__main__":
    raise SystemExit(main())
