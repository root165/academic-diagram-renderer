#!/usr/bin/env python3
"""Validate the portable JSON/YAML intermediate representation for this skill."""
from __future__ import annotations

import argparse
import json
import re
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


REQUIRED = ("title", "purpose", "diagram_type", "semantic_level", "notation", "visual_style", "source_requirements")
KNOWN_TYPES = {
    "erd", "flowchart", "dfd", "bpmn", "use_case", "sequence", "activity",
    "state_machine", "structure_chart", "functional_decomposition",
    "logical_architecture", "business_flow", "component", "deployment", "table",
}
CONCEPTUAL_SECTIONS = ("概念结构设计", "概念模型", "概念设计", "数据需求", "业务实体关系")
LOGICAL_SECTIONS = ("逻辑结构设计", "逻辑模型", "数据库表设计", "表结构设计", "表关系设计")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def source_present(item: dict[str, Any]) -> bool:
    value = item.get("source_requirement", item.get("source_requirements"))
    return bool(value)


def ids(items: Any, report: Report, label: str, require_name: bool = False) -> set[str]:
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
        if require_name and not isinstance(item.get("name"), str):
            report.warn("IR-104", f"{label}[{ident}] has no display name; the renderer will use the id.")
    return seen


def parse_hex(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str) or not HEX_RE.match(value):
        return None
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def is_grayscale(value: Any) -> bool:
    rgb = parse_hex(value)
    return rgb is not None and rgb[0] == rgb[1] == rgb[2]


def validate_visual_style(ir: dict[str, Any], report: Report) -> None:
    style = ir.get("visual_style")
    if not isinstance(style, dict):
        report.error(
            "STYLE-001",
            "visual_style is required; declare palette 'monochrome' with white background and dark ink.",
        )
        return
    palette = style.get("palette")
    if palette not in {"monochrome", "template"}:
        report.error("STYLE-002", "visual_style.palette must be 'monochrome' (default) or 'template' with a rationale.")
    if palette == "template" and not style.get("template_reference"):
        report.error("STYLE-003", "A template palette needs template_reference; otherwise use monochrome.")
    for key in ("background", "foreground"):
        if not HEX_RE.match(str(style.get(key, ""))):
            report.error("STYLE-004", f"visual_style.{key} must be a 6-digit hex colour.")
    fills = style.get("fills", [])
    if not isinstance(fills, list):
        report.error("STYLE-005", "visual_style.fills must be an array of hex colours.")
        fills = []
    for index, fill in enumerate(fills):
        if not HEX_RE.match(str(fill)):
            report.error("STYLE-006", f"visual_style.fills[{index}] must be a 6-digit hex colour.")
    if palette == "monochrome":
        for key in ("background", "foreground"):
            if style.get(key) and not is_grayscale(style[key]):
                report.error("STYLE-007", f"visual_style.{key} must be grayscale when palette is monochrome.")
        for index, fill in enumerate(fills):
            if not is_grayscale(fill):
                report.error("STYLE-008", f"visual_style.fills[{index}] must be grayscale when palette is monochrome.")
    if style.get("color_usage") not in (None, "none", "template"):
        report.warn("STYLE-009", "Record color_usage as 'none' for monochrome output.")


def validate_section(ir: dict[str, Any], report: Report) -> None:
    if ir.get("diagram_type") == "table":
        return
    section = ir.get("section")
    if not isinstance(section, str) or not section.strip():
        return
    level, notation = ir.get("semantic_level"), ir.get("notation")
    if any(token in section for token in CONCEPTUAL_SECTIONS):
        if level != "conceptual_er" or notation != "chen":
            report.error(
                "SEC-001",
                f"Section {section!r} is conceptual; use semantic_level 'conceptual_er' and notation 'chen'.",
            )
    elif any(token in section for token in LOGICAL_SECTIONS):
        if level not in {"logical_relational", "physical_schema"} or notation == "chen":
            report.error(
                "SEC-002",
                f"Section {section!r} is logical/table design; use logical_relational or physical_schema and a non-Chen notation.",
            )
    elif "物理" in section:
        if level != "physical_schema":
            report.warn("SEC-003", f"Section {section!r} looks physical; record physical_schema if that is intended.")


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


def validate_attributes(
    owner: dict[str, Any],
    owner_label: str,
    level: Any,
    entity_map: dict[str, dict[str, Any]],
    report: Report,
) -> None:
    attributes = owner.get("attributes")
    if attributes is None:
        return
    if not isinstance(attributes, list):
        report.error("ER-230", f"{owner_label}.attributes must be an array.")
        return
    names: set[str] = set()
    for index, attribute in enumerate(attributes):
        prefix = f"{owner_label}.attributes[{index}]"
        if not isinstance(attribute, dict) or not isinstance(attribute.get("name"), str) or not attribute["name"].strip():
            report.error("ER-231", f"{prefix} needs a non-empty name.")
            continue
        name = attribute["name"].strip()
        if name in names:
            report.error("ER-232", f"{owner_label} has duplicate attribute {name!r}.")
        names.add(name)
        key = attribute.get("key")
        if key is not None and key not in {"PK", "FK", "UK"}:
            report.error("ER-233", f"{prefix}.key must be PK, FK, or UK, not {key!r}.")
        if level == "conceptual_er":
            if key == "FK":
                report.error("ER-234", f"{prefix} is a foreign key; conceptual Chen models must not contain FK metadata.")
            if attribute.get("references"):
                report.error("ER-235", f"{prefix} carries a physical reference; move it to the logical model.")
            for field in ("type", "nullable", "index", "default"):
                if field in attribute:
                    report.warn("ER-236", f"{prefix} carries physical metadata {field!r}; omit it from the conceptual model.")
            if name.endswith("_id"):
                report.warn("ER-237", f"{prefix} looks like a foreign-key column; use a business attribute name.")
        else:
            references = attribute.get("references")
            if key == "FK" and not isinstance(references, dict):
                report.error("ER-238", f"{prefix} is marked FK but has no references object with entity and attribute.")
            if isinstance(references, dict):
                target_id = references.get("entity")
                target_attr = references.get("attribute")
                target = entity_map.get(target_id)
                if target is None:
                    report.error("ER-239", f"{prefix} references unknown entity/table {target_id!r}.")
                else:
                    target_attributes = target.get("attributes", [])
                    match = next(
                        (a for a in target_attributes if isinstance(a, dict) and a.get("name") == target_attr),
                        None,
                    )
                    if match is None:
                        report.error("ER-240", f"{prefix} references unknown attribute {target_id}.{target_attr}.")
                    elif match.get("key") != "PK":
                        report.error("ER-241", f"{prefix} must reference a primary key, but {target_id}.{target_attr} is {match.get('key')!r}.")
                    if attribute.get("type") and match and match.get("type") and attribute["type"] != match["type"]:
                        report.warn("ER-242", f"{prefix} type {attribute['type']!r} differs from target type {match['type']!r}.")


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
        report.error("ER-203", "Chen notation hides relation/table keys; logical and physical models need PK/FK notation.")
    entities = ir.get("entities")
    entity_ids = ids(entities, report, "entities", require_name=True)
    entity_map = {
        e["id"]: e
        for e in entities
        if isinstance(e, dict) and isinstance(e.get("id"), str)
    } if isinstance(entities, list) else {}
    for entity in entities if isinstance(entities, list) else []:
        if not isinstance(entity, dict) or entity.get("id") not in entity_ids:
            continue
        validate_attributes(entity, f"entities[{entity['id']}]", level, entity_map, report)
        if level in {"logical_relational", "physical_schema"}:
            attributes = entity.get("attributes", [])
            if not any(isinstance(a, dict) and a.get("key") == "PK" for a in attributes):
                report.error("ER-220", f"Logical table {entity['id']!r} needs at least one PK attribute.")
        elif level == "conceptual_er" and isinstance(entity.get("attributes"), list) and not entity["attributes"]:
            report.warn("ER-214", f"Conceptual entity {entity['id']!r} has no business attributes.")

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
        if left not in entity_ids or right not in entity_ids:
            report.error("ER-206", f"{prefix} endpoints must reference declared entities.")
        if not isinstance(relationship.get("name"), str) or not relationship["name"].strip():
            if level == "conceptual_er":
                report.error("ER-216", f"{prefix} needs a verb/verb-phrase label for the Chen diamond.")
            else:
                report.warn("ER-217", f"{prefix} has no readable relationship name.")
        multiplicity(relationship.get("left_to_right"), f"{prefix}.left_to_right", report)
        multiplicity(relationship.get("right_to_left"), f"{prefix}.right_to_left", report)
        if not source_present(relationship):
            report.warn("ER-207", f"{prefix} has no source_requirement.")
        validate_attributes(relationship, prefix, level, entity_map, report)
        lr, rl = relationship.get("left_to_right", {}), relationship.get("right_to_left", {})
        is_many_to_many = isinstance(lr, dict) and isinstance(rl, dict) and lr.get("max") == "N" and rl.get("max") == "N"
        if is_many_to_many and level in {"logical_relational", "physical_schema"}:
            report.error("ER-208", f"{prefix} remains M:N in a {level}; model an associative entity/table with two 1:N relationships.")
        if is_many_to_many and level == "conceptual_er":
            if not relationship.get("resolves_to"):
                report.warn("ER-209", f"{prefix} is conceptually M:N; document its associative relation when mapping to a relational schema.")
                report.warn("ER-226", f"{prefix} is M:N but does not name the logical associative table in resolves_to.")
        if level in {"logical_relational", "physical_schema"} and relationship.get("attributes"):
            report.warn("ER-225", f"{prefix} has relationship attributes; place them as columns on the associative table.")


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


def _edge_endpoints(ir: dict[str, Any], node_ids: set[str], report: Report, rule: str) -> None:
    edges = ir.get("edges", [])
    if not isinstance(edges, list) or not edges:
        report.warn(rule, "No edges are declared; confirm that a single node is the intended figure.")
        return
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict) or edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            report.error(rule, f"edges[{index}] must connect declared nodes.")


def validate_architecture(ir: dict[str, Any], report: Report) -> None:
    """Lightweight checks for logical/deployment architecture views."""
    nodes = ir.get("nodes", [])
    node_ids = ids(nodes, report, "nodes")
    if not isinstance(nodes, list) or not nodes:
        report.error("ARC-001", "Architecture view needs at least one node.")
        return
    diagram_type = ir.get("diagram_type")
    allowed = {
        "layer", "component", "service", "gateway", "database", "cache",
        "external_system", "node", "execution_environment", "artifact",
        "container", "device", "queue",
    }
    for node in nodes:
        if not isinstance(node, dict) or node.get("id") not in node_ids:
            continue
        kind = node.get("type")
        if kind not in allowed:
            report.warn("ARC-002", f"Node {node['id']!r} has unsupported architecture type {kind!r}.")
        if not node.get("label") and not node.get("name"):
            report.warn("ARC-003", f"Node {node['id']!r} has no label.")
    _edge_endpoints(ir, node_ids, report, "ARC-004")
    if diagram_type == "logical_architecture":
        if not any(isinstance(n, dict) and n.get("type") in {"layer", "component", "service"} for n in nodes):
            report.warn("ARC-010", "Logical architecture should declare at least one layer/component/service.")
        if any(isinstance(n, dict) and n.get("type") in {"node", "execution_environment", "device"} for n in nodes):
            report.warn("ARC-011", "Logical architecture contains runtime nodes; move them to a deployment view.")
        if ir.get("viewpoint") not in (None, "logical"):
            report.warn("ARC-012", "Logical architecture should record viewpoint='logical'.")
    elif diagram_type == "deployment":
        if not any(isinstance(n, dict) and n.get("type") in {"node", "execution_environment", "device"} for n in nodes):
            report.warn("ARC-020", "Deployment view should contain at least one runtime node/execution environment.")
        if ir.get("viewpoint") not in (None, "deployment"):
            report.warn("ARC-021", "Deployment view should record viewpoint='deployment'.")
        for node in nodes:
            if isinstance(node, dict) and node.get("type") in {"activity", "decision", "task"}:
                report.error("ARC-022", f"Deployment view must not contain business activity node {node.get('id')!r}.")


def validate_business_flow(ir: dict[str, Any], report: Report) -> None:
    variant = ir.get("flow_variant")
    if variant not in {"basic", "cross_functional"}:
        report.error("BF-001", "business_flow needs flow_variant 'basic' or 'cross_functional'.")
    nodes = ir.get("nodes", [])
    node_ids = ids(nodes, report, "nodes")
    if not isinstance(nodes, list) or not nodes:
        report.error("BF-002", "Business flow needs at least one node.")
        return
    lanes = ir.get("lanes", [])
    lane_ids = {
        lane.get("id") for lane in lanes
        if isinstance(lane, dict) and isinstance(lane.get("id"), str)
    } if isinstance(lanes, list) else set()
    roles = set()
    for node in nodes:
        if not isinstance(node, dict) or node.get("id") not in node_ids:
            continue
        kind = node.get("type")
        if kind not in {"start", "end", "activity", "decision", "handoff"}:
            report.warn("BF-003", f"Node {node['id']!r} has unusual business-flow type {kind!r}.")
        lane = node.get("lane") or node.get("role")
        if lane:
            roles.add(lane)
            if lane_ids and lane not in lane_ids:
                report.warn("BF-004", f"Node {node['id']!r} uses undeclared lane/role {lane!r}.")
        elif variant == "cross_functional":
            report.warn("BF-005", f"Cross-functional node {node['id']!r} has no lane/role.")
    if variant == "cross_functional" and len(lane_ids or roles) < 2:
        report.error("BF-006", "Cross-functional flow needs at least two lanes/roles.")
    if variant == "basic" and len(lane_ids or roles) > 1:
        report.error("BF-007", "Basic flow has multiple lanes/roles; use flow_variant 'cross_functional'.")
    starts = [n for n in nodes if isinstance(n, dict) and n.get("type") == "start"]
    ends = [n for n in nodes if isinstance(n, dict) and n.get("type") == "end"]
    if not starts:
        report.warn("BF-010", "Business flow has no explicit start node.")
    if not ends:
        report.warn("BF-011", "Business flow has no explicit end node.")
    _edge_endpoints(ir, node_ids, report, "BF-012")
    for index, edge in enumerate(ir.get("edges", []) if isinstance(ir.get("edges", []), list) else []):
        if isinstance(edge, dict) and edge.get("from") in node_ids and edge.get("to") in node_ids:
            if edge.get("from") != edge.get("to") and not edge.get("label"):
                report.warn("BF-013", f"edges[{index}] has no label; label handoffs/decisions.")


def validate_structure_chart(ir: dict[str, Any], report: Report) -> None:
    nodes = ir.get("nodes", [])
    node_ids = ids(nodes, report, "nodes")
    if not isinstance(nodes, list) or not nodes:
        report.error("SC-001", "Structure Chart needs at least one module node.")
        return
    for node in nodes:
        if isinstance(node, dict) and node.get("id") in node_ids:
            if node.get("type") not in {"module", "controller", "library"}:
                report.warn("SC-002", f"Node {node['id']!r} is not a module/controller type.")
    edges = ir.get("edges", [])
    if not isinstance(edges, list) or not edges:
        report.error("SC-003", "Structure Chart needs at least one call edge.")
        return
    incoming = {ident: 0 for ident in node_ids}
    coupled = 0
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict) or edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            report.error("SC-004", f"edges[{index}] must connect declared modules.")
            continue
        incoming[edge["to"]] += 1
        if edge.get("data") or edge.get("control") or edge.get("couple"):
            coupled += 1
    roots = [ident for ident, count in incoming.items() if count == 0]
    if len(roots) != 1:
        report.warn("SC-005", f"Structure Chart should have one root module; found {len(roots)}: {roots}.")
    if coupled == 0:
        report.warn("SC-006", "No data/control couple is recorded; the figure proves hierarchy only, not interface design.")


def validate_functional_decomposition(ir: dict[str, Any], report: Report) -> None:
    nodes = ir.get("nodes", [])
    node_ids = ids(nodes, report, "nodes")
    if not isinstance(nodes, list) or not nodes:
        report.error("FD-001", "Functional decomposition needs at least one function node.")
        return
    edges = ir.get("edges", [])
    if not isinstance(edges, list) or not edges:
        report.error("FD-002", "Functional decomposition needs parent–child edges.")
        return
    incoming = {ident: 0 for ident in node_ids}
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict) or edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            report.error("FD-003", f"edges[{index}] must connect declared functions.")
            continue
        if edge.get("data") or edge.get("control"):
            report.error("FD-004", f"edges[{index}] carries a data/control couple; use a Structure Chart for calls/couples.")
        incoming[edge["to"]] += 1
    roots = [ident for ident, count in incoming.items() if count == 0]
    if len(roots) != 1:
        report.warn("FD-005", f"Functional decomposition should have one root function; found {len(roots)}: {roots}.")


def validate_state_machine(ir: dict[str, Any], report: Report) -> None:
    nodes = ir.get("nodes", [])
    node_ids = ids(nodes, report, "nodes")
    if not isinstance(nodes, list) or not nodes:
        report.error("SM-001", "State machine needs at least one state node.")
        return
    for node in nodes:
        if isinstance(node, dict) and node.get("id") in node_ids:
            if node.get("type") not in {"state", "initial", "final"}:
                report.warn("SM-002", f"Node {node['id']!r} has unusual state-machine type {node.get('type')!r}.")
    if not any(isinstance(n, dict) and n.get("type") == "initial" for n in nodes):
        report.warn("SM-003", "State machine has no explicit initial pseudostate.")
    if not any(isinstance(n, dict) and n.get("type") == "final" for n in nodes):
        report.warn("SM-004", "State machine has no explicit final pseudostate.")
    edges = ir.get("edges", [])
    if not isinstance(edges, list) or not edges:
        report.error("SM-005", "State machine needs at least one transition.")
        return
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict) or edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            report.error("SM-006", f"edges[{index}] must connect declared states.")
            continue
        if not edge.get("label") and not edge.get("event"):
            report.warn("SM-007", f"edges[{index}] has no event/transition label.")


def validate_table(ir: dict[str, Any], report: Report) -> None:
    columns = ir.get("columns", [])
    rows = ir.get("rows", [])
    if not isinstance(columns, list) or not columns:
        report.error("TAB-001", "Table needs at least one column.")
        return
    for index, column in enumerate(columns):
        if not isinstance(column, dict) or not isinstance(column.get("name"), str) or not column["name"].strip():
            report.error("TAB-002", f"columns[{index}] needs a non-empty name.")
    if not isinstance(rows, list) or not rows:
        report.warn("TAB-003", "Table has no data rows; confirm that an empty template is intended.")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(columns):
            report.error("TAB-004", f"rows[{index}] must have exactly {len(columns)} cells.")


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
    if "section" in ir and not isinstance(ir["section"], str):
        report.error("IR-004", "section must be a string.")
    validate_visual_style(ir, report)
    validate_section(ir, report)


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
        validator = {
            "erd": validate_erd,
            "flowchart": validate_flowchart,
            "dfd": validate_dfd,
            "structure_chart": validate_structure_chart,
            "functional_decomposition": validate_functional_decomposition,
            "state_machine": validate_state_machine,
            "logical_architecture": validate_architecture,
            "deployment": validate_architecture,
            "business_flow": validate_business_flow,
            "table": validate_table,
        }.get(ir.get("diagram_type"))
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
