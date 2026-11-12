# Document-section contract for data models

A report often contains two different data-model sections. They answer different questions and therefore must not reuse the same figure. Read this file before placing an ERD, and record the target section in the IR as `section`.

## Section-to-model mapping

| Report section (and common variants) | Question the figure answers | Required model | Required notation | Must not contain |
| --- | --- | --- | --- | --- |
| 概念结构设计、概念模型、概念设计、数据需求、业务实体关系 | What business things exist, what business facts describe them, and how are they related? | `conceptual_er` | `chen` | Foreign keys, table names, column types, indexes, join tables, `_id` columns, implementation-only status fields |
| 逻辑结构设计、逻辑模型、数据库表设计、表结构设计、表关系设计 | Which relations/tables implement the model, and how are primary and foreign keys linked? | `logical_relational` | `crow_foot_ie` | Chen diamonds as the primary relationship symbol, unresolved M:N relationships |
| 物理结构设计、物理模型、索引与存储设计 | How is the logical model implemented in a specific DBMS? | `physical_schema` | `crow_foot_ie` or a documented physical notation | Business relationship diamonds |

If a section is named `数据库设计`, use its subheadings to decide. `数据库 E-R 图设计` followed by `数据表设计` normally means a Chen conceptual figure first and a Crow's Foot logical figure later. Record that interpretation in `assumptions` when the heading is ambiguous.

## The two required figures

When the document contains both a conceptual section and a logical/table-design section, produce both figures as a pair:

1. **Conceptual Chen ERD** in 概念结构设计 (or the conceptual data-model subsection).
2. **Logical Crow's Foot ERD** in 逻辑结构设计 / 数据库表设计 (or immediately before the table dictionary).

Do not place the Crow's Foot figure in the conceptual section merely because it looks more "database-like". Do not place the Chen figure in the table-design section as a decorative repeat. One section, one model, one notation.

## Conceptual Chen checklist

- Rectangles are entity sets named with stable business nouns.
- Ovals are **business attributes** that a domain reader would recognise: 设备编码, 运行状态, 检查结果, 紧急程度. They are not columns copied from a DDL.
- Diamonds are relationship sets named with readable verbs or verb phrases: 包含, 覆盖, 生成, 发现, 转报修, 形成, 领用.
- Put cardinality labels on both ends of every relationship (`1`, `N`, or `M`). If the report needs participation, state the minimum separately in the figure note or in the relationship table; a bare `1:N` is only a maximum.
- M:N is allowed and should remain M:N at this level. Do not pre-join it with an associative entity.
- Relationship attributes (for example 领用数量, 领用单价, 金额小计 on 维修工单—备件) belong on the diamond, not arbitrarily on either entity.
- No foreign keys, no `_id` columns, no data types, no nullability, no indexes, no table prefixes. A business identifier (设备编码) may be underlined as the entity identifier; that is not a foreign key.
- If support entities (用户, 角色, 字典) are omitted, say so in `assumptions`; do not silently imply the model is complete.

## Logical Crow's Foot checklist

- Every box is a relation/table with a physical table name.
- Every table has a primary key. Mark it `PK` in the attribute list rather than relying on bold or colour alone.
- Every foreign key is marked `FK` and names its target table and target key (`eq_equipment.category_id → eq_category.id`). A bare `_id` without a target is not a validated FK.
- Resolve every conceptual M:N into an associative table with two 1:N links. Keep the relationship attributes as columns on the associative table.
- Show optionality at both ends: `0..1`, `1..1`, `0..N`, `1..N`. A crow's foot alone shows maximum cardinality; the circle/bar shows minimum. Because Crow's Foot is a de facto convention rather than a single ISO standard, put the endpoint legend in the figure note or caption.
- Follow the project's real constraint. If a business rule says one repair generates at most one work order, do not draw `0..N` just because the table has an `id`.
- If physical FKs are intentionally not created (for example, the project uses Service-layer integrity), still show the logical FK and state the physical exception in the figure note. Logical FK ≠ physical constraint.

## Pair-consistency check

Before handoff, compare the two IRs:

| Check | Pass condition |
| --- | --- |
| Entity coverage | Every conceptual entity that owns data has a logical table, or the omission is listed in `assumptions`. |
| Relationship coverage | Every conceptual 1:N/M:N becomes a logical FK or associative table. |
| M:N resolution | Each conceptual M:N names the associative table that implements it (`resolves_to`). |
| Attribute promotion | Conceptual relationship attributes appear as columns on the associative table. |
| Cardinality | Logical optionality does not contradict the conceptual minimum/maximum. |
| Naming | The logical table's business name and the conceptual entity name are recognisably the same thing. |
| Style | Both IRs declare `visual_style.palette: monochrome` (or a documented template exception). |

## Size control

A conceptual Chen figure is not a database catalogue. Keep it readable at the intended page size:

- A4 portrait: about 5–7 entities and 8–15 attributes; split a second business chain into a separate figure.
- A3 landscape: about 7–10 entities; use fixed coordinates and a deliberate two-row snake rather than letting an automatic layout produce a tall strip.
- Give each entity 1–3 business attributes, not every column. If a relationship has attributes, show them on the diamond; if there are more than four, summarise the rest in the relationship table.

When a figure is scoped to a core chain, say which chains/entities are omitted in `assumptions` and in the figure note. Do not let omission look like completeness.

## Caption and note pattern

Use captions that state the model level and notation, so a reader cannot mistake one figure for the other:

- `图 5-1  核心业务概念 E-R 图（Chen 记法；矩形为实体，椭圆为业务属性，菱形为联系；本图不表示主键、外键或表结构）`
- `图 5-2  核心业务表关系图（Crow's Foot 记法；PK/FK 为逻辑主外键；本项目物理层不建外键约束，完整性由 Service 层保证）`

Put exclusions and scope limits in a note below the figure, not in the figure title. Keep the figure title short enough for a Word caption.

## Evidence

The notation and level distinctions above are grounded in the sources listed in [notation-evidence.md](notation-evidence.md). If a school template or client standard mandates a different notation, the template wins; record it in `source_requirements` and explain the deviation in the figure note.
