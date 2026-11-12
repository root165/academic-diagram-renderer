---
name: academic-diagram-renderer
description: Create, review, validate, render, or place semantically correct diagrams and restrained academic tables for Chinese theses, graduation projects, project reports, requirements analysis, and system-design documents. Use whenever a request involves ER/ERD, conceptual vs logical database design, 概念结构设计, 逻辑结构设计, 数据库表设计, 系统结构图/SC, 系统功能结构图, 系统逻辑架构图, 业务流程图, 跨职能泳道图, 部署架构图, DFD, flowchart, BPMN, Structure Chart/SC, Statechart, UML, architecture, database schema, functional decomposition, or report-table design, especially when diagram notation, cardinality, symbols, arrows, section placement, monochrome/print style, or reproducible rendering matters. Do not use for decorative illustrations or ordinary Office shape drawing.
---

# Academic Diagram Renderer

Create figures whose meaning can be checked before they are styled. Treat a diagram as a model, not as decoration: preserve the user's domain facts, choose one diagram notation, record its source requirements, validate the model, then render it with a deterministic tool.

## Start: identify the model

First determine the diagram's **purpose**, **semantic level**, and **notation**. Read [routing.md](references/routing.md) before choosing a diagram type. If the phrase `SC 图` is used, ask whether it means **Structure Chart** or **Statechart**; do not guess.

When a material fact is absent, record a `TBD` or an explicit `assumption` with its impact. Ask one focused question only when the unknown changes the core model. Never manufacture entities, fields, cardinalities, process steps, states, metrics, or data.

Create an IR file before renderer source. JSON is the portable default; YAML is allowed when PyYAML is installed. Use [diagram-ir.schema.json](schemas/diagram-ir.schema.json) and the matching file in `templates/` as the starting point.

## Document-section contract

A report's section name tells you which model to build. Read [section-contract.md](references/section-contract.md) before placing an ERD.

| Section | Required model | Required notation | What proves the point |
| --- | --- | --- | --- |
| 概念结构设计 / 概念模型 / 数据需求 | `conceptual_er` | `chen` | Rectangles, **business attributes**, verb-labelled diamonds, M:N allowed, **no FK** |
| 逻辑结构设计 / 数据库表设计 / 表结构设计 | `logical_relational` | `crow_foot_ie` | Tables with **PK/FK**, associative tables, resolved M:N |
| 物理结构设计 / 索引与存储设计 | `physical_schema` | `crow_foot_ie` or documented physical notation | SQL types, indexes, physical constraints |

When both the conceptual and logical sections exist, produce **two separate figures**: a Chen ERD in the conceptual section and a Crow's Foot ERD in the logical/table-design section. Do not reuse one figure in both places, and do not put foreign keys into the Chen figure to "make it more complete". A conceptual figure with `_id` columns or join tables has collapsed the levels and no longer proves business understanding.

Record the target section in the IR as `section`. For a paired delivery, validate both IRs and check the pair-consistency table in [section-contract.md](references/section-contract.md): every conceptual M:N must name its associative table (`resolves_to`), and every relationship attribute must reappear as a column there.

## Visual baseline: monochrome by default

Every diagram declares its visual policy in the IR and uses the most basic tone:

```json
"visual_style": {
  "palette": "monochrome",
  "background": "#FFFFFF",
  "foreground": "#111111",
  "fills": ["#FFFFFF", "#F2F2F2"],
  "color_usage": "none"
}
```

Use black/dark-grey ink on white, at most one light-grey fill, no hue, no gradients, no shadows. Shape, line style, line weight, and text labels carry meaning; colour does not. A school/journal template that requires colour is the only override: use `palette: "template"`, record `template_reference`, and keep the figure legible in grayscale. Read [visual-style.md](references/visual-style.md) for the palette, notation-specific styling, renderer settings, and the print check.

默认单色：白底、黑/深灰线条与文字、至多一个浅灰填充；不使用彩色、渐变或阴影。每张图的 IR 都必须写出 `visual_style`，并在渲染后用 `check_monochrome.py` 验收，不能只在口头上说“用了单色”。

## Term triage: do not collapse different views

Chinese report terms that look similar often mean different models. Read [authority-map.md](references/authority-map.md) before choosing a notation.

| User's term | Model type | Core question | Do not silently turn it into |
| --- | --- | --- | --- |
| 系统结构图 / SC 图 / 模块结构图 | `structure_chart` | Which modules call which modules, and what data/control couples pass? | 系统功能结构图、流程图、状态图 |
| 系统功能结构图 | `functional_decomposition` | How is a capability decomposed into sub-functions? | SC 的调用箭头、数据/控制偶、执行顺序 |
| 系统逻辑架构图 | `logical_architecture` | What logical layers/components exist, what are their responsibilities, and which dependencies are allowed? | 部署节点、IP/端口、服务器拓扑 |
| 基本业务流程图 | `business_flow` (`flow_variant: basic`) | One role processes one business matter in what activity/decision order? | 多角色泳道、程序控制流、DFD |
| 跨职能业务流程图 | `business_flow` (`flow_variant: cross_functional`) | Multiple roles/departments hand off a business matter in what order? | 单角色流程、模块调用图、纯组织架构图 |
| 部署架构图 | `deployment` | Which runtime nodes, execution environments, artifacts, and communication paths exist? | 逻辑分层、业务流程图、模块调用图 |

`SC` alone is ambiguous: ask whether it means **Structure Chart** or **Statechart**. `结构图` alone is also ambiguous: ask whether it means **module/call SC** or **functional decomposition**. A figure with call arrows and data/control couples is an SC; a figure with only parent–child function lines is a functional decomposition.

When the user asks for a **系统结构图 / SC** and the DFD has a clear input → processing → output shape, **default to a transform-type SC**: input/afferent branch, central transform, output/efferent branch. Use a transaction-type SC only when the DFD has a transaction centre or the user explicitly asks for transaction analysis. A **系统功能结构图** defaults to a **top-down vertical tree** (root above, children below), not a left-to-right horizontal tree.

## Route to the appropriate reference

- ERD, database, entities, PK/FK, cardinality: read [er-modeling.md](references/er-modeling.md).
- Section placement, conceptual/logical pair: read [section-contract.md](references/section-contract.md).
- Normative basis and citations: read [notation-evidence.md](references/notation-evidence.md).
- Monochrome palette and renderer settings: read [visual-style.md](references/visual-style.md).
- Program or algorithm flow: read [flowchart-iso5807.md](references/flowchart-iso5807.md).
- External actors, processes, stores, and data movement: read [dfd.md](references/dfd.md).
- Use case, sequence, activity, state machine, component, or deployment: read [uml.md](references/uml.md).
- Structure Chart (SC), functional decomposition: read [structure-chart.md](references/structure-chart.md).
- Logical architecture, deployment architecture: read [architecture-views.md](references/architecture-views.md).
- Basic or cross-functional business flow: read [business-flow.md](references/business-flow.md).
- Source levels, P1–P6 example evidence, authoritative images: read [authority-map.md](references/authority-map.md).
- Academic/report tables: read [table-style.md](references/table-style.md).

## Required workflow

1. Produce `diagram.ir.json` (or YAML) with title, purpose, `section`, `diagram_type`, `semantic_level`, `notation`, `visual_style`, sources, assumptions/TBDs, and model elements. For `business_flow`, add `flow_variant: basic|cross_functional`; for `logical_architecture`/`deployment`, add `viewpoint: logical|deployment`.
2. Validate it before rendering:

   ```powershell
   python scripts/validate_ir.py diagram.ir.json --report validation.json
   ```

   Resolve errors without inventing facts. Warnings may remain only if disclosed in the figure note or handoff. The validator rejects FK metadata in a conceptual Chen model, unresolved M:N in a logical model, a Crow's Foot model placed in a conceptual section, and a chromatic palette.
3. Select the renderer from the notation, not convenience. PlantUML is preferred for UML and IE ERD; Graphviz for Chen ERD, hierarchy, and layout-sensitive figures; Mermaid only when its notation is adequate; Draw.io when BPMN stencils or a hand-editable layout are required. Read [tooling.md](references/tooling.md) before tool discovery or installation.
   If the chosen renderer is absent, run the planning mode below and ask the user for installation authorization before any download, installation, bucket change, or execution-policy change:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/install-renderer.ps1 -Plan -Renderer plantuml
   ```

   State the missing command, why that renderer is required, proposed Scoop location/buckets/packages, dependencies, network/disk side effects, and the safe fallback (source + validation report only). End with one explicit question: `是否授权安装上述工具？` Stop for the answer. A reply such as “可以/同意” authorizes only the stated plan; a different package, bucket, location, or elevation level requires a new request.
4. Generate editable renderer source adjacent to the IR (`.puml`, `.dot`, `.mmd`, or `.drawio`), preserving traceability to the IR. Set the monochrome palette explicitly in the source; do not rely on a renderer default. For a Chen ERD with fixed `pos="x,y!"` coordinates, render with `--engine neato --fixed` so Graphviz honours the layout instead of reflowing it into a tall strip.
5. Render to SVG or PDF first. Generate PNG only for document compatibility. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/discover-tools.ps1
   python scripts/render.py source.puml --format svg
   python scripts/inspect_output.py output.svg --report output-inspection.json
   python scripts/check_monochrome.py output.svg --report output-monochrome.json
   ```

   The monochrome check is part of acceptance, not an optional extra. If it reports a hue, fix the source and re-render; do not hand-edit the SVG.
6. Inspect the rendered image at normal reading size, then in grayscale. Correct clipping, overlap, ambiguous arrows, unreadable labels, and unjustified visual complexity in source, then re-render. A screenshot is not a deliverable; it may only assist visual QA.
7. Hand off the IR, source, SVG/PDF, optional PNG, validation report, inspection report, monochrome report, notation, renderer version, and unresolved assumptions. For a conceptual/logical pair, state the section placement and the M:N mapping explicitly. For structural/architecture/process figures, state the source level: formal standard, canonical textbook, government guide, or de facto convention.

## Non-negotiable modeling boundaries

- Do not mix Chen, Crow's Foot/IE, and IDEF1X in one ERD.
- A relationship maximum (`1:N`) is not participation. Retain each direction's minimum and maximum separately.
- A conceptual Chen ERD may show `M:N` directly. A logical relation model or physical schema resolves it with an associative entity/table and two `1:N` relationships.
- A conceptual Chen ERD contains business attributes but no foreign keys, table prefixes, SQL types, or physical indexes.
- A logical Crow's Foot ERD contains PK/FK and resolved M:N; it does not use Chen diamonds as its primary relationship symbol.
- A Structure Chart describes module hierarchy/calls and data/control couples; it is not a functional decomposition tree, a flowchart, or a Statechart.
- A call arrow means control transfer; a data/control couple is a **separate additional arrow** with an open/filled circle. Do not label the call arrow `D:`/`C:` and omit the couple arrow.
- When a “系统结构图” has no explicit variant and the DFD is input–process–output shaped, default to a transform-type SC, not a transaction-type SC. Use transaction analysis only with a transaction centre/dispatch-by-type structure.
- A functional decomposition shows only `is composed of` hierarchy; it must not acquire call arrows, data/control couples, loops, or decisions. Its default layout is a top-down vertical tree with **portrait function boxes** (height ≥ width), not wide landscape bars or a left-to-right horizontal tree.
- A logical architecture shows layers/components/responsibilities/dependencies; it must not contain runtime nodes, IPs, ports, or deployment topology.
- A deployment view shows runtime nodes, execution environments, artifacts, and communication paths; it must not contain business activities or logical layer bands.
- A basic business flow has one role and an activity/decision order; a cross-functional business flow has multiple roles/lanes and explicit handoffs. Neither is a program flowchart.
- A DFD describes data movement, not sequence or control decisions. A program flowchart describes control flow, not data stores and external data interfaces.
- A Statechart describes states and event-triggered transitions; it is not a call hierarchy or a flowchart.
- Office/WPS/POI may insert validated graphics or create a styled native table; it must not be the primary semantic drawing engine.
- Do not use colour as the only carrier of meaning; the default palette is monochrome.

## Validation and recovery

`validate_ir.py` validates the common schema plus ER, DFD, flowchart, SC/functional decomposition, logical/deployment architecture, business-flow, state-machine, and table invariants. It deliberately treats uncertain facts as warnings, not invented values. Renderer failures are separate from semantic validation; preserve both reports.

Attempt at most two mechanical repair rounds for syntax, layout, or mapping mistakes. If the remaining problem needs new business facts, stop and state the exact question or `TBD`; never claim the figure is correct.

## Tables

Apply [table-style.md](references/table-style.md) before creating a table. A school, journal, client, or supplied document template overrides the default. Otherwise use a restrained three-line academic table where appropriate, not a default blue-header dashboard style.

## Tool installation

Only inspect tools by default. When a required renderer is absent, proactively present the approval request described in [tooling.md](references/tooling.md), then stop. Do not download software, alter PowerShell policy, add Scoop buckets, or install dependencies unless the user explicitly authorizes the displayed plan. On Windows, use `scripts/install-renderer.ps1` only after approval; it rechecks package names, performs the permitted action, rediscovers commands, and runs no render until a source file is explicitly supplied.
