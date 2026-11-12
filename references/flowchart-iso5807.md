# Program flowcharts

Use a program flowchart for algorithmic or procedural control flow. Use ISO 5807 conventions as the baseline: terminators identify entry/exit, process symbols represent processing, decision symbols represent a condition or selection, input/output symbols represent input or output, and connectors make long or cross-page jumps explicit.

## Checks

- Each independent flow normally has an explicit start and end; document an intentional exception such as an event loop or exception escape.
- Every non-terminal node has an outgoing route. Every ordinary node should be reachable from an entry unless it is intentionally isolated and explained.
- A binary decision has labelled outcomes that are mutually exclusive and collectively complete. A multi-way selection may have more than two named outcomes; do not force false `Yes/No` labels.
- Keep direction consistent, label non-obvious branches, and pair connector labels.
- Do not replace a decision with an unexplained arrow label or use a decision diamond for a data store/entity relationship.

## Reference

ISO 5807:1985, *Information processing — Documentation symbols and conventions for data, program and system flowcharts*: https://www.iso.org/standard/11955.html
