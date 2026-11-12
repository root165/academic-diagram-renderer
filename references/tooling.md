# Tool discovery, rendering, and installation

## Tool choice

| Need | Preferred renderer |
| --- | --- |
| UML or IE/Crow's Foot ERD | PlantUML |
| Chen ERD with a hand-tuned layout | Graphviz `neato -n2` |
| Hierarchy, orthogonal tree, special layout | Graphviz `dot` |
| Simple supported flow/sequence | Mermaid CLI |
| BPMN stencil or editable manual layout | Draw.io desktop CLI |

PlantUML and Graphviz should render SVG/PDF whenever practical. Mermaid and Draw.io outputs must also be tested; their available CLI options can vary by installation.

For a Chen ERD, `scripts/render.py` accepts `--engine neato --fixed`; this invokes `dot -Kneato -n2`, which honours `pos="x,y!"` coordinates. Use fixed coordinates when the automatic layout would turn a business chain into a tall, unreadable strip. For ordinary Graphviz diagrams, keep the default `dot` engine.

## Discovery first

Run `scripts/discover-tools.ps1`. It only reports command availability and versions. Do not promise a particular tool is installed based on a package manager listing.

## Installation authorization gate

If a required tool is absent, the skill must not silently downgrade to a hand-authored SVG, nor merely say “please install it”. It must run the planning mode, then present an actionable authorization request:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-renderer.ps1 -Plan -Renderer plantuml
```

Use this response shape, replacing values from the generated plan:

> 未检测到 `<command>`，因此无法将 `<diagram type>` 进行确定性渲染和视觉验收。建议安装 `<renderer>`（以及 `<dependencies>`），使用 Scoop `<scoop root>`，可能新增 bucket：`<buckets>`，需要下载软件包并写入本机。也可以先只交付已校验的 IR 和源码。是否授权按上述方案安装？

Stop after asking. `可以`/`同意` authorizes only this exact plan. If the user requests a different drive, global install, elevation, package, or bucket, create a new plan and ask again. A refusal, missing reply, or unavailable network leaves the result in source-only state with the block recorded.

After approval, search the relevant manifest, execute the explicitly approved plan, rerun `discover-tools.ps1`, and render one minimal source to a temporary SVG before declaring the renderer available. Do not claim success merely because Scoop returned a package listing.

For Windows Scoop, use the official installer documentation. Scoop's default per-user location is under the user profile; for this skill, a new requested installation defaults to `D:\Scoop` and uses Scoop's advanced installer with an explicit absolute `-ScoopDir`. An existing Scoop installation is reused; never migrate it without a separate user request. Verify actual package names first with `scoop search`; `main` is built in, while GUI packages may require a bucket such as `extras`.

Never change execution policy, install Scoop, add a bucket, or use elevated/global installation without explicit approval. `install-renderer.ps1` requires `-Approved` for any side effect and may bootstrap Scoop only when `-InstallScoop` is also explicitly provided. After any installation, rerun discovery and render a minimal test source.

References:

- Scoop installation: https://github.com/ScoopInstaller/Scoop
- PlantUML command line: https://plantuml.com/command-line
- Graphviz command line: https://graphviz.org/doc/info/command.html
