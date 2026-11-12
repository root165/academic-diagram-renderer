# ER and relational-model rules

## State the level and notation

`conceptual_er` models business entity sets, business attributes, and relationship sets. `logical_relational` models relations/tables, keys, and integrity constraints. `physical_schema` additionally models implementation-specific data types, indexes, storage, defaults, and database dialect. Never present a physical schema as a Chen conceptual ERD.

Choose exactly one notation for one figure:

- **Chen**: entity sets are rectangles, relationship sets diamonds, and attributes ovals. Use for conceptual analysis. Business attributes are expected; foreign keys, table prefixes, data types, and indexes are not.
- **Crow's Foot / IE**: entity/table boxes and endpoint cardinality/optionality marks. Use for logical relational views. Primary and foreign keys are expected.
- **IDEF1X**: use only when the required template or audience specifically calls for it.

PlantUML's `entity` syntax implements Information Engineering notation, not Chen notation. Its endpoint symbols are renderer syntax and are only generated after the IR has precise minimum/maximum information.

## Conceptual Chen rules

A conceptual figure should let a domain reader confirm the business without reading a DDL.

- **Entity set**: a stable business noun (设备, 巡检计划, 维修工单). Use a rectangle.
- **Business attribute**: a fact the business records (设备编码, 运行状态, 检查结果). Use an oval. Prefer names that appear in requirements, not physical column names.
- **Identifier**: underline a business identifier such as 设备编码. A surrogate `id` is not required at this level.
- **Relationship set**: a readable verb or verb phrase (包含, 覆盖, 生成, 发现, 转报修, 形成, 领用). Use a diamond; put the verb inside.
- **Relationship attribute**: a fact that exists only because two entities are related (领用数量, 领用单价, 金额小计). Attach it to the diamond, not to one endpoint.
- **Cardinality**: label both ends (`1`, `N`, `M`). A bare `1:N` states maxima, not participation; record minimums separately when the report claims optionality.
- **M:N**: valid and expected at this level. Do not replace it with an associative entity merely to look “logical”.

Forbidden in a conceptual Chen figure: `FK`, `_id` foreign-key columns, table prefixes (`sys_`, `ins_`, `wo_`), SQL types, nullability, indexes, unique constraints, join tables. A primary-key/identifier attribute is not a foreign key; if it is a surrogate `id`, it is still a physical artefact and should normally be omitted.

## Logical Crow's Foot rules

A logical figure should let a developer create the tables.

- **Table**: physical table name (for example `eq_equipment`), drawn as a box.
- **Primary key**: every table has one; mark `PK` in the attribute row.
- **Foreign key**: mark `FK`, and record the target table and target key. A bare `customer_id` without a target is not enough.
- **Optionality**: show `0..1`, `1..1`, `0..N`, or `1..N` at both ends. The crow's foot is the many end; the circle is the optional end; the bar is the mandatory end.
- **M:N**: forbidden as an unresolved relationship. Replace it with an associative table and two 1:N links. Keep relationship attributes on the associative table.
- **Physical exception**: if the project deliberately does not create physical FK constraints (common in MyBatis-Plus/Service-layer integrity designs), still draw the logical FK and state the exception in the figure note. Do not hide the relationship.

## Cardinality and participation

For every binary relationship preserve the two natural-language statements. Example:

```yaml
Customer -> Order: a customer creates 0..N orders
Order -> Customer: an order belongs to exactly 1 customer
```

The maximum portion may summarize as `1:N`, but it does not say whether an entity participates optionally. Record `min` (0 or 1) and `max` (1 or N) in each direction. Do not encode one direction's values on the other direction in the IR.

In a conceptual Chen ERD, `1:1`, `1:N`/`N:1`, and `M:N` are valid binary mapping cardinalities. An `M:N` relationship with attributes is valid conceptually. In a logical relational model or physical schema, resolve it as an associative relation/table with two `1:N` links and retain relationship attributes there.

Business rules override a naive reading of the schema. If `wo_order.repair_id` is unique, the conceptual relationship is at most one work order per repair (`1:0..1`), not `1:N`, even though the table has an `id`.

## Attribute rules

| Level | Allowed attribute metadata | Forbidden |
| --- | --- | --- |
| `conceptual_er` | `name`, `business: true`, optional `note`; identifier may use `key: PK` | `key: FK`, `references`, `type`, `nullable`, `index`, `default` |
| `logical_relational` | `name`, `key` (`PK`/`FK`/`UK`), `references` for FK, `type`, `nullable` | An FK without a target key |
| `physical_schema` | logical metadata plus SQL type, nullability, default, index, storage | An FK that targets a non-key column |

Do not copy the DDL into the conceptual model. If a conceptual attribute name only makes sense to a developer (`status`, `deleted`, `created_time`), replace it with the business fact it represents (运行状态, 是否归档, 创建日期) or omit it.

## Semantic checks

- Entity and table names are stable nouns; Chen relationship names are readable verbs or verb phrases.
- An attribute that depends on the combination of related entities belongs to the relationship/associative entity, not arbitrarily to one endpoint.
- Every relationship endpoint names an existing entity/table.
- Do not turn an n-ary relationship into unrelated binary relationships without evidence of equivalence.
- A physical FK must target an existing candidate/primary key and nullability must agree with the intended minimum participation when that constraint is claimed.
- Do not invent keys, FKs, datatypes, or cardinalities. Use `TBD` where requirements are silent.
- A conceptual figure without any attributes is usually a diagram of boxes, not a business model; add the attributes the requirements actually mention, or record why they are unavailable.

## Section placement and evidence

Read [section-contract.md](section-contract.md) before placing the figure. Read [notation-evidence.md](notation-evidence.md) for the source of each claim. Apply [visual-style.md](visual-style.md); every ERD declares `visual_style.palette: monochrome` unless the document template requires otherwise.

## References

- P. P.-S. Chen, *The Entity-Relationship Model—Toward a Unified View of Data* (1976): https://doi.org/10.1145/320434.320440
- R. Elmasri and S. B. Navathe, *Fundamentals of Database Systems*, 7th ed., chs. 3 and 9.
- PlantUML, Information Engineering diagrams: https://plantuml.com/ie-diagram
