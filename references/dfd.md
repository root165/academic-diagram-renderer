# Data-flow diagrams

Use a DFD to model data movement between external entities, processes, data stores, and data flows. Select either Yourdon–DeMarco or Gane–Sarson before drawing; never combine their symbol systems in one figure.

## Naming and scope

- External entities and data stores are nouns.
- Processes are verb phrases that transform data.
- Data flows are named data nouns, not controls such as `Yes`, `Retry`, or `next`.
- A DFD does not show timing, algorithms, branching diamonds, PK/FK design, or control sequencing.

## Balancing

When decomposing a process, its child DFD must preserve the parent process's external input/output flows. Internal stores and sub-processes may be added, but the boundary interface must not be silently changed.

## Checks

Every flow connects permitted model elements, every process has meaningful data input/output unless explicitly a source/sink conversion, and all node IDs resolve. Use a separate process model when the reader needs control order.
