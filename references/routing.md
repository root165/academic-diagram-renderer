# Diagram routing

Select the model according to the question the reader must answer. A renderer is an implementation choice, not a diagram type.

| Reader's question | Diagram | Exclude |
| --- | --- | --- |
| What data things exist and how are they related? | Conceptual ERD or logical relational model | Flow arrows, decision diamonds |
| Where does data enter, get transformed, persist, and leave? | DFD | Timing, branches, program control |
| What happens next in an algorithm or procedure? | Program flowchart | ER cardinality and PK/FK |
| What business events, gateways and roles perform a process? | BPMN | Arbitrary flowchart substitutions |
| Who can use which system capability? | UML use case | Database tables, control logic |
| Which messages occur between lifelines over time? | UML sequence | Decision diamonds |
| Which modules call or coordinate submodules? | Structure Chart | Temporal workflow |
| What stable states and event-triggered transitions exist? | UML state machine | Call hierarchy |
| How are capabilities decomposed? | Functional decomposition / WBS | Calls, loops, data/control couples |
| Which deployable pieces communicate across runtime nodes? | UML component/deployment | Business control flow |

## Clarify before model selection

Ask only if the ambiguity changes notation or semantics. Typical examples: whether `SC` means Structure Chart or Statechart; whether an ERD is conceptual or a physical schema; whether a "process diagram" means BPMN, DFD, or a program flowchart. If a report template specifies a notation, use it and record the template as the source of that choice.

## Output record

Every IR starts with a model declaration:

```json
{
  "title": "订单数据模型",
  "purpose": "说明订单与客户的业务数据关系",
  "diagram_type": "erd",
  "semantic_level": "logical_relational",
  "notation": "crow_foot_ie",
  "source_requirements": ["R-03", "R-07"],
  "assumptions": [],
  "tbd": []
}
```

Do not quietly turn `TBD` into an asserted fact during source generation.
