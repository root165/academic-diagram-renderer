#!/usr/bin/env python3
"""Validate the portable JSON/YAML intermediate representation for this skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_ir(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise ValueError("YAML needs PyYAML. Use JSON, or install PyYAML with explicit approval.") from exc
    value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("IR root must be an object.")
    return value


class Report:
    def __init__(self) -> None:
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []

    def error(self, rule: str, message: str) -> None:
        self.errors.append({"rule": rule, "message": message})

    def warn(self, rule: str, message: str) -> None:
        self.warnings.append({"rule": rule, "message": message})

    def payload(self, path: Path) -> dict[str, Any]:
        return {
            "input": str(path),
            "valid": not self.errors,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {"errors": len(self.errors), "warnings": len(self.warnings)},
        }


REQUIRED = ("title", "purpose", "diagram_type", "semantic_level", "notation", "source_requirements")
KNOWN_TYPES = {
    "erd", "flowchart", "dfd", "bpmn", "use_case", "sequence", "activity",
    "state_machine", "structure_chart", "functional_decomposition", "component",
    "deployment", "table",
}


def source_present(item: dict[str, Any]) -> bool:
    value = item.get("source_requirement", item.get("source_requirements"))
    return bool(value)


def ids(items: Any, report: Report, label: str) -> set[str]:
    seen: set[str] = set()
    if not isinstance(items, list):
        report.error("IR-100", f"{label} must be an array.")
        return seen
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            report.error("IR-101", f"{label}[{index}] needs a non-empty id.")
            continue
        ident = item["id"]
        if ident in seen:
            report.error("IR-102", f"Duplicate {label} id: {ident}.")
        seen.add(ident)
        if not source_present(item):
            report.warn("IR-103", f"{label}[{ident}] has no source_requirement; retain a traceability note.")
    return seen


def multiplicity(value: Any, path: str, report: Report) -> None:
    if not isinstance(value, dict):
        report.error("ER-210", f"{path} must be an object with min and max.")
        return
    minimum, maximum = value.get("min"), value.get("max")
    if minimum not in (0, 1):
        report.error("ER-211", f"{path}.min must be 0 or 1, not {minimum!r}.")
    if maximum not in (1, "N"):
        report.error("ER-212", f"{path}.max must be 1 or N, not {maximum!r}.")
    if maximum == 1 and minimum == 1 and not value.get("meaning"):
        report.warn("ER-213", f"{path} is exact-one but has no natural-language meaning.")


def validate_erd(ir: dict[str, Any], report: Report) -> None:
    level = ir.get("semantic_level")
    notation = ir.get("notation")
    if level not in {"conceptual_er", "logical_relational", "physical_schema"}:
        report.error("ER-200", "ERD semantic_level must be conceptual_er, logical_relational, or physical_schema.")
    if notation not in {"chen", "crow_foot_ie", "idef1x"}:
        report.error("ER-201", "ERD notation must be chen, crow_foot_ie, or idef1x.")
    if level == "conceptual_er" and notation != "chen":
        report.warn("ER-202", "Conceptual ER is usually clearest in Chen notation; record why another notation is required.")
    if level in {"logical_relational", "physical_schema"} and notation == "chen":
        report.warn("ER-203", "Chen notation may hide relation/table keys; confirm it matches the deliverable's intent.")
    entities = ids(ir.get("entities"), report, "entities")
    relationships = ir.get("relationships", [])
    if not isinstance(relationships, list) or not relationships:
        report.error("ER-204", "ERD needs at least one relationship.")
        return
    for index, relationship in enumerate(relationships):
        prefix = f"relationships[{index}]"
        if not isinstance(relationship, dict):
            report.error("ER-205", f"{prefix} must be an object.")
            continue
        left, right = relationship.get("left_entity"), relationship.get("right_entity")
        if left not in entities or right not in entities:
            report.error("ER-206", f"{prefix} endpoints must reference declared entities.")
        multiplicity(relationship.get("left_to_right"), f"{prefix}.left_to_right", report)
        multiplicity(relationship.get("right_to_left"), f"{prefix}.right_to_left", report)
        if not source_present(relationship):
            report.warn("ER-207", f"{prefix} has no source_requirement.")
        lr, rl = relationship.get("left_to_right", {}), relationship.get("right_to_left", {})
        is_many_to_many = isinstance(lr, dict) and isinstance(rl, dict) and lr.get("max") == "N" and rl.get("max") == "N"
        if is_many_to_many and level in {"logical_relational", "physical_schema"}:
            report.error("ER-208", f"{prefix} remains M:N in a {level}; model an associative entity/table with two 1:N relationships.")
        if is_many_to_many and level == "conceptual_er":
            report.warn("ER-209", f"{prefix} is conceptually M:N; document its associative relation when mapping to a relational schema.")


def validate_flowchart(ir: dict[str, Any], report: Report) -> None:
    if ir.get("notation") != "iso_5807":
        report.warn("FC-200", "Record ISO 5807-compatible notation or explain the required alternative.")
    nodes = ir.get("nodes", [])
    node_ids = ids(nodes, report, "nodes")
    entries = [node for node in nodes if isinstance(node, dict) and node.get("type") == "start"]
    exits = [node for node in nodes if isinstance(node, dict) and node.get("type") == "end"]
    if not entries:
        report.error("FC-201", "Flowchart needs an explicit start node or a documented exception.")
    if not exits:
        report.error("FC-202", "Flowchart needs an explicit end node or a documented exception.")
    outgoing: dict[str, list[dict[str, Any]]] = {ident: [] for ident in node_ids}
    for index, edge in enumerate(ir.get("edges", [])):
        if not isinstance(edge, dict) or edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            report.error("FC-203", f"edges[{index}] must connect declared nodes.")
            continue
        outgoing[edge["from"]].append(edge)
    for node in nodes:
        if not isinstance(node, dict) or node.get("id") not in node_ids:
            continue
        ident, kind = node["id"], node.get("type")
        if kind != "end" and not outgoing[ident]:
            report.error("FC-204", f"Node {ident} has no outgoing edge.")
        if kind == "decision":
            branches = outgoing[ident]
            if len(branches) < 2:
                report.error("FC-205", f"Decision {ident} needs at least two labelled outcomes.")
            elif any(not edge.get("label") for edge in branches):
                report.error("FC-206", f"Every decision outcome from {ident} needs a label.")


def validate_dfd(ir: dict[str, Any], report: Report) -> None:
    if ir.get("notation") not in {"yourdon_demarco", "gane_sarson"}:
        report.error("DFD-200", "DFD notation must be yourdon_demarco or gane_sarson.")
    nodes = ir.get("nodes", [])
    node_ids = ids(nodes, report, "nodes")
    kinds: dict[str, str] = {}
    for node in nodes:
        if isinstance(node, dict) and node.get("id") in node_ids:
            kind = node.get("type")
            kinds[node["id"]] = kind
            if kind not in {"external_entity", "process", "data_store"}:
                report.error("DFD-201", f"Node {node['id']} has unsupported DFD type {kind!r}.")
    flows = ir.get("data_flows", [])
    if not flows:
        report.error("DFD-202", "DFD needs at least one data flow.")
    for index, flow in enumerate(flows):
        if not isinstance(flow, dict) or flow.get("from") not in node_ids or flow.get("to") not in node_ids:
            report.error("DFD-203", f"data_flows[{index}] must connect declared nodes.")
            continue
        label = str(flow.get("label", "")).strip()
        if not label:
            report.error("DFD-204", f"data_flows[{index}] needs a data-noun label.")
        if label.lower() in {"yes", "no", "next", "retry", "是", "否", "下一步", "重试"}:
            report.error("DFD-205", f"data_flows[{index}] looks like control flow, not data: {label!r}.")
        if kinds.get(flow["from"]) == "data_store" and kinds.get(flow["to"]) == "data_store":
            report.error("DFD-206", "A DFD must not connect one data store directly to another.")


def validate_common(ir: dict[str, Any], report: Report) -> None:
    for field in REQUIRED:
        value = ir.get(field)
        if value is None or value == "" or value == []:
            report.error("IR-001", f"Missing required field: {field}.")
    if ir.get("diagram_type") not in KNOWN_TYPES:
        report.error("IR-002", f"Unknown diagram_type: {ir.get('diagram_type')!r}.")
    for field in ("assumptions", "tbd"):
        if field in ir and not isinstance(ir[field], list):
            report.error("IR-003", f"{field} must be an array.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = Report()
    try:
        ir = load_ir(args.input)
        if not isinstance(ir, dict):
            raise ValueError("IR root must be an object.")
        validate_common(ir, report)
        validator = {"erd": validate_erd, "flowchart": validate_flowchart, "dfd": validate_dfd}.get(ir.get("diagram_type"))
        if validator:
            validator(ir, report)
        else:
            report.warn("IR-900", f"No deterministic validator is bundled yet for {ir.get('diagram_type')!r}; inspect the routed reference.")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report.error("IR-000", str(exc))
    payload = report.payload(args.input)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
