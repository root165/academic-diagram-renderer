# Structure Chart and decomposition rules

## First disambiguate `SC`

`SC` may mean **Structure Chart**, a structured-design module hierarchy, or **Statechart**, a state machine. Ask when the user has not expanded the abbreviation.

## Structure Chart

A Structure Chart depicts a module hierarchy and module invocation/control relationship. It may show data couples, control couples, iteration, or selection only when those design facts are known and requested. It does not narrate chronological user steps and does not use flowchart decision diamonds as module nodes.

Use modules as stable responsibilities, keep caller/callee hierarchy readable, and distinguish data passed from control signals. Do not infer coupling merely from matching names.

## Functional decomposition / WBS

Use this only to show `is composed of` hierarchy. It does not represent invocation, data transfer, loops, decisions, or state transitions. Keep sibling labels at a comparable abstraction level; use a cross-link only when the report explicitly needs a non-tree dependency.
