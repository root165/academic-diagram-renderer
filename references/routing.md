# Diagram routing

Select the model according to the question the reader must answer. A renderer is an implementation choice, not a diagram type. Read [authority-map.md](authority-map.md) for source levels and example evidence.

## Term triage: six figures that are commonly confused

| User's term | Model type | Core question | Do not silently turn it into |
| --- | --- | --- | --- |
| 系统结构图 / SC 图 / 模块结构图 | `structure_chart` | Which modules call which modules, and what data/control couples pass? | 系统功能结构图、流程图、状态图 |
| 系统功能结构图 | `functional_decomposition` | How is a capability decomposed into sub-functions? | SC 的调用箭头、数据/控制偶、执行顺序 || 系统逻辑架构图 | `logical_architecture` | What logical layers/components exist, what are their responsibilities, and which dependencies are allowed? | 部署节点、IP/端口、服务器拓扑 |
| 基本业务流程图 | `business_flow` (`flow_variant: basic`) | One role processes one business matter in what activity/decision order? | 多角色泳道、程序控制流、DFD |
| 跨职能业务流程图 | `business_flow` (`flow_variant: cross_functional`) | Multiple roles/departments hand off a business matter in what order? | 单角色流程、模块调用图、纯组织架构图 |
| 部署架构图 | `deployment` | Which runtime nodes, execution environments, artifacts, and communication paths exist? | 逻辑分层、业务流程图、模块调用图 |

If the user says “SC 图”, ask whether they mean **Structure Chart** or **Statechart** before drawing. If they say “结构图”, ask whether they mean **module/call structure** (SC) or **functional decomposition** (功能结构图); the two look similar but carry different semantics.

When the answer is Structure Chart and the DFD has a clear input → processing → output shape, **default to a transform-type SC** (input branch + central transform + output branch). Use a transaction-type SC only when the DFD has a transaction centre/dispatch-by-type structure. Functional structure charts default to a **top-down vertical tree**, not a left-to-right horizontal tree.

## General routing

| Reader's question | Diagram | Exclude |
| --- | --- | --- |
| What business things exist, what business facts describe them, and how are they related? | Conceptual Chen ERD | PK/FK columns, SQL types, join tables, flow arrows |
| Which tables implement the model, and how are PK/FK linked? | Logical Crow's Foot ERD | Chen diamonds as the primary relationship symbol, unresolved M:N |
| Where does data enter, get transformed, persist, and leave? | DFD | Timing, branches, program control |
| What happens next in an algorithm or procedure? | Program flowchart | ER cardinality and PK/FK |
| What business events, gateways and roles perform a process? | BPMN or business flow | Arbitrary flowchart substitutions |
| Who can use which system capability? | UML use case | Database tables, control logic |
| Which messages occur between lifelines over time? | UML sequence | Decision diamonds |
| Which modules call or coordinate submodules? | Structure Chart | Temporal workflow |
| What stable states and event-triggered transitions exist? | UML state machine / Statechart | Call hierarchy |
| How are capabilities decomposed? | Functional decomposition / WBS | Calls, loops, data/control couples |
| Which logical layers/components and dependencies exist? | Logical architecture | Runtime nodes, IPs, deployment topology |
| Which deployable pieces communicate across runtime nodes? | UML component/deployment or deployment architecture | Business control flow |
| Which roles hand off a business process? | Cross-functional business flow / BPMN collaboration | Single-role procedure |

## Document-section routing

When the request names a report section, route by the section before choosing a renderer. Read [section-contract.md](section-contract.md) for the full contract.

| Section | Model | Notation |
| --- | --- | --- |
| 概念结构设计 / 概念模型 / 数据需求 | `conceptual_er` | `chen` |
| 逻辑结构设计 / 数据库表设计 / 表结构设计 | `logical_relational` | `crow_foot_ie` |
| 物理结构设计 / 索引与存储设计 | `physical_schema` | `crow_foot_ie` or documented physical notation |
| 系统结构设计 / 模块设计 | `structure_chart` | `structure_chart` (SC), transform/transaction variant |
| 系统功能结构设计 | `functional_decomposition` | `functional_decomposition` |
| 系统逻辑架构设计 | `logical_architecture` | `layered_architecture`, `uml_2_5_1_component`, or documented C4 |
| 业务流程设计 | `business_flow` | `bpmn_2_0_2`, `iso_5807`, or documented swimlane |
| 部署设计 | `deployment` | `uml_2_5_1_deployment`, `c4_deployment`, or documented cloud view |

If a report contains both the conceptual and logical sections, produce two figures. Do not reuse one figure in both sections. Record the target section in the IR as `section`.

## Clarify before model selection

Ask only if the ambiguity changes notation or semantics. Typical examples: whether `SC` means Structure Chart or Statechart; whether “结构图” means module/call SC or functional decomposition; whether an ERD is conceptual or a physical schema; whether a “process diagram” means BPMN, DFD, or a program flowchart; whether “架构图” means logical architecture or deployment. If a report template specifies a notation, use it and record the template as the source of that choice.

## Output record

Every IR starts with a model declaration:

```json
{
  "title": "订单数据模型",
  "section": "数据库表设计",
  "purpose": "说明订单与客户的表关系及主外键",
  "diagram_type": "erd",
  "semantic_level": "logical_relational",
  "notation": "crow_foot_ie",
  "visual_style": {"palette": "monochrome", "background": "#FFFFFF", "foreground": "#111111", "color_usage": "none"},
  "source_requirements": ["R-03", "R-07"],
  "assumptions": [],
  "tbd": []
}
```

Do not quietly turn `TBD` into an asserted fact during source generation. Do not omit `visual_style`: the default is monochrome, and the declaration is how the handoff proves it. For business flows, add `flow_variant: basic|cross_functional`; for architecture views, add `viewpoint: logical|deployment`.
