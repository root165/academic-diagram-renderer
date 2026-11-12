# Visual baseline: monochrome academic diagrams

Every diagram produced by this skill declares its visual policy in the IR and renders in the most basic tone by default. The default is **pure monochrome**: white background, black/dark-grey ink, white or light-grey fills, no hue. This is not an aesthetic preference. Academic reports are printed, photocopied, and read in grayscale; a diagram whose meaning depends on colour becomes unreadable in those conditions, and colour can imply a classification that the model does not actually contain.

## Required declaration

Include this object in every IR:

```json
"visual_style": {
  "palette": "monochrome",
  "background": "#FFFFFF",
  "foreground": "#111111",
  "fills": ["#FFFFFF", "#F2F2F2"],
  "color_usage": "none"
}
```

`validate_ir.py` warns when the declaration is missing and rejects a chromatic palette. A school/journal template that requires colour is the only override; use `palette: "template"`, add `template_reference`, and keep the figure legible in grayscale.

## Palette

| Role | Value | Use |
| --- | --- | --- |
| Paper | `#FFFFFF` | Canvas and shape interiors |
| Ink | `#111111` | Shape outlines, text, key symbols |
| Secondary ink | `#333333` | Relationship lines, cardinality labels |
| Muted ink | `#666666` | Figure notes, non-key annotations |
| Light fill | `#F2F2F2` | Table header or a single emphasis band |
| Mid fill | `#D9D9D9` | Only when a second fill level is genuinely needed |

Do not introduce red, blue, green, amber, or any other hue. Do not use gradients, drop shadows, bevels, glow, transparency-as-meaning, or coloured status badges. If two categories must be distinguished, use shape, line style (solid/dashed), line weight, a text label, or a legend — never colour alone. This also satisfies the WCAG 2.2 principle that colour must not be the only visual means of conveying information (SC 1.4.1).

## Notation-specific rules

### Chen ERD

- Entity: white rectangle, `#111111` 1.2 pt outline, black label.
- Attribute: white ellipse, `#111111` 0.9 pt outline; identifier attribute underlined, not coloured.
- Relationship: white diamond, `#111111` 1.1 pt outline; verb label inside.
- Connector: `#333333` 1.0 pt solid; cardinality label near the endpoint.
- Relationship attributes attach to the diamond, not to an entity.

### Crow's Foot / IE table diagram

- Table: white rectangle; header band `#F2F2F2`; `#111111` outline.
- PK/FK: print `PK` / `FK` text in the row, optionally bold. Never rely on a coloured key icon.
- Relationship: `#333333` 1.0–1.2 pt; crow's foot and optionality circle/bar at the correct ends.
- Dashed line only for a documented non-identifying or logical-only relationship; explain it in the legend.

### Flowchart, DFD, UML, structure chart

Use the same ink/paper palette. Shape and line conventions carry meaning; colour does not. A single light-grey fill may distinguish a background band or a legend panel, but not a semantic category that has no label.

## Typography and print checks

- Use a CJK-capable sans-serif for diagram labels (Microsoft YaHei / Noto Sans CJK SC) at 8–11 pt; keep one typeface family.
- Keep labels horizontal; avoid rotated text except for a short axis label.
- Check at 100% print size, then in grayscale. Text must remain readable at A4 width; if it does not, split the figure rather than shrinking it below 8 pt.
- Use vector SVG/PDF for the report. PNG is only for compatibility and must be exported at ≥ 200 dpi.

## Renderer settings

Graphviz:

```dot
graph [bgcolor="white", color="#111111", fontcolor="#111111"];
node  [style="filled", fillcolor="#FFFFFF", color="#111111", fontcolor="#111111"];
edge  [color="#333333", fontcolor="#333333"];
```

PlantUML:

```plantuml
skinparam monochrome true
skinparam backgroundColor #FFFFFF
skinparam defaultFontColor #111111
skinparam shadowing false
skinparam roundcorner 0
```

Mermaid: set `theme: neutral`, `themeVariables` to white/black/grey, and `lineColor` to `#333333`. Draw.io: use the `Sketch`/`Minimal` monochrome palette and disable shadows.

## Verification

After rendering to SVG, run:

```powershell
python scripts/check_monochrome.py output.svg --report output-monochrome.json
```

The checker reports every non-grayscale colour token. Fix the source and re-render; do not post-process the SVG by hand. PDF output should be generated from the same monochrome source, and the SVG check is the acceptance evidence. If a renderer emits an anti-aliasing or metadata colour that is not visually meaningful, record it and confirm it is outside the drawn content; do not silently ignore a visible hue.

## Evidence

The print/grayscale requirement is a house rule for academic deliverables, reinforced by WCAG 2.2 SC 1.4.1 (Use of Color). The notation conventions are sourced in [notation-evidence.md](notation-evidence.md).
