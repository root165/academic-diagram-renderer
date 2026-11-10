---
name: academic-diagram-renderer
description: Create, review, validate, render, or place semantically correct diagrams and restrained academic tables for Chinese theses, graduation projects, project reports, requirements analysis, and system-design documents. Use whenever a request involves ER/ERD, DFD, flowchart, BPMN, Structure Chart/SC, UML, architecture, database schema, functional decomposition, or report-table design, especially when diagram notation, cardinality, symbols, arrows, or reproducible rendering matters. Do not use for decorative illustrations or ordinary Office shape drawing.
---

# Academic Diagram Renderer

Create figures whose meaning can be checked before they are styled. Treat a diagram as a model, not as decoration: preserve the user's domain facts, choose one diagram notation, record its source requirements, validate the model, then render it with a deterministic tool.

## Start: identify the model

First determine the diagram's **purpose**, **semantic level**, and **notation**. Read [routing.md](references/routing.md) before choosing a diagram type. If the phrase `SC 图` is used, ask whether it means **Structure Chart** or **Statechart**; do not guess.

When a material fact is absent, record a `TBD` or an explicit `assumption` with its impact. Ask one focused question only when the unknown changes the core model. Never manufacture entities, fields, cardinalities, process steps, states, metrics, or data.

Create an IR file before renderer source. JSON is the portable default; YAML is allowed when PyYAML is installed. Use [diagram-ir.schema.json](schemas/diagram-ir.schema.json) and the matching file in `templates/` as the starting point.

## Route to the appropriate reference

- ERD, database, entities, PK/FK, cardinality: read [er-modeling.md](references/er-modeling.md).
- Program or algorithm flow: read [flowchart-iso5807.md](references/flowchart-iso5807.md).
- External actors, processes, stores, and data movement: read [dfd.md](references/dfd.md).
- Use case, sequence, activity, state machine, component, or deployment: read [uml.md](references/uml.md).
- Structure Chart, functional decomposition, or WBS: read [structure-chart.md](references/structure-chart.md).
- Academic/report tables: read [table-style.md](references/table-style.md).

## Required workflow

1. Produce `diagram.ir.json` (or YAML) with title, purpose, `diagram_type`, `semantic_level`, `notation`, sources, assumptions/TBDs, and model elements.
2. Validate it before rendering:

   ```powershell
   python scripts/validate_ir.py diagram.ir.json --report validation.json
   ```

   Resolve errors without inventing facts. Warnings may remain only if disclosed in the figure note or handoff.
3. Select the renderer from the notation, not convenience. PlantUML is preferred for UML and IE ERD; Graphviz for hierarchy/layout; Mermaid only when its notation is adequate; Draw.io when BPMN stencils or a hand-editable layout are required. Read [tooling.md](references/tooling.md) before tool discovery or installation.
   If the chosen renderer is absent, run the planning mode below and ask the user for installation authorization before any download, installation, bucket change, or execution-policy change:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/install-renderer.ps1 -Plan -Renderer plantuml
   ```

   State the missing command, why that renderer is required, proposed Scoop location/buckets/packages, dependencies, network/disk side effects, and the safe fallback (source + validation report only). End with one explicit question: `是否授权安装上述工具？` Stop for the answer. A reply such as “可以/同意” authorizes only the stated plan; a different package, bucket, location, or elevation level requires a new request.
4. Generate editable renderer source adjacent to the IR (`.puml`, `.dot`, `.mmd`, or `.drawio`), preserving traceability to the IR.
5. Render to SVG or PDF first. Generate PNG only for document compatibility. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/discover-tools.ps1
   python scripts/render.py source.puml --format svg
   python scripts/inspect_output.py output.svg --report output-inspection.json
   ```

6. Inspect the rendered image at normal reading size. Correct clipping, overlap, ambiguous arrows, unreadable labels, and unjustified visual complexity in source, then re-render. A screenshot is not a deliverable; it may only assist visual QA.
7. Hand off the IR, source, SVG/PDF, optional PNG, validation report, inspection report, notation, renderer version, and unresolved assumptions.

## Non-negotiable modeling boundaries

- Do not mix Chen, Crow's Foot/IE, and IDEF1X in one ERD.
- A relationship maximum (`1:N`) is not participation. Retain each direction's minimum and maximum separately.
- A conceptual Chen ERD may show `M:N` directly. A logical relation model or physical schema resolves it with an associative entity/table and two `1:N` relationships.
- A DFD describes data movement, not sequence or control decisions. A program flowchart describes control flow, not data stores and external data interfaces.
- A Structure Chart describes module hierarchy/coupling; it is not a flowchart. A Statechart describes states and event-triggered transitions.
- Office/WPS/POI may insert validated graphics or create a styled native table; it must not be the primary semantic drawing engine.

## Validation and recovery

`validate_ir.py` validates the common schema plus ER, DFD, and flowchart invariants. It deliberately treats uncertain facts as warnings, not invented values. Renderer failures are separate from semantic validation; preserve both reports.

Attempt at most two mechanical repair rounds for syntax, layout, or mapping mistakes. If the remaining problem needs new business facts, stop and state the exact question or `TBD`; never claim the figure is correct.

## Tables

Apply [table-style.md](references/table-style.md) before creating a table. A school, journal, client, or supplied document template overrides the default. Otherwise use a restrained three-line academic table where appropriate, not a default blue-header dashboard style.

## Tool installation

Only inspect tools by default. When a required renderer is absent, proactively present the approval request described in [tooling.md](references/tooling.md), then stop. Do not download software, alter PowerShell policy, add Scoop buckets, or install dependencies unless the user explicitly authorizes the displayed plan. On Windows, use `scripts/install-renderer.ps1` only after approval; it rechecks package names, performs the permitted action, rediscovers commands, and runs no render until a source file is explicitly supplied.
