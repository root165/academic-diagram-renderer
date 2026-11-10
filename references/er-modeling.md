# ER and relational-model rules

## State the level and notation

`conceptual_er` models business entity sets and relationship sets. `logical_relational` models relations/tables, keys, and integrity constraints. `physical_schema` additionally models implementation-specific data types, indexes, storage, defaults, and database dialect. Never present a physical schema as a Chen conceptual ERD.

Choose exactly one notation for one figure:

- **Chen**: entity sets are rectangles, relationship sets diamonds, and attributes ovals. Use for conceptual analysis.
- **Crow's Foot / IE**: entity/table boxes and endpoint cardinality/optionality marks. Use for logical relational views.
- **IDEF1X**: use only when the required template or audience specifically calls for it.

PlantUML's `entity` syntax implements Information Engineering notation, not Chen notation. Its endpoint symbols are renderer syntax and are only generated after the IR has precise minimum/maximum information.

## Cardinality and participation

For every binary relationship preserve the two natural-language statements. Example:

```yaml
Customer -> Order: a customer creates 0..N orders
Order -> Customer: an order belongs to exactly 1 customer
```

The maximum portion may summarize as `1:N`, but it does not say whether an entity participates optionally. Record `min` (0 or 1) and `max` (1 or N) in each direction. Do not encode one direction's values on the other direction in the IR.

In a conceptual Chen ERD, `1:1`, `1:N`/`N:1`, and `M:N` are valid binary mapping cardinalities. An `M:N` relationship with attributes is valid conceptually. In a logical relational model or physical schema, resolve it as an associative relation/table with two `1:N` links and retain relationship attributes there.

## Semantic checks

- Entity and table names are stable nouns; Chen relationship names are readable verbs or verb phrases.
- An attribute that depends on the combination of related entities belongs to the relationship/associative entity, not arbitrarily to one endpoint.
- Every relationship endpoint names an existing entity/table.
- Do not turn an n-ary relationship into unrelated binary relationships without evidence of equivalence.
- A physical FK must target an existing candidate/primary key and nullability must agree with the intended minimum participation when that constraint is claimed.
- Do not invent keys, FKs, datatypes, or cardinalities. Use `TBD` where requirements are silent.

## References

- P. P.-S. Chen, *The Entity-Relationship Model—Toward a Unified View of Data* (1976): https://dl.acm.org/doi/10.1145/320434.320440
- PlantUML, Information Engineering diagrams: https://plantuml.com/ie-diagram
