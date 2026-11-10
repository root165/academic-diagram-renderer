---
name: academic-diagram-renderer
description: 为中文论文、毕业设计、项目报告、需求分析和系统设计文档创建、审查、校验、渲染或插入语义正确的图与克制的学术表格。涉及 ER/ERD、DFD、流程图、BPMN、Structure Chart/SC、UML、架构图、数据库模式、功能分解或报告表格，且图例、基数、符号、箭头或可复现渲染很重要时使用；不用于装饰性插画或普通 Office 形状绘制。
---

# 学术图表渲染器

本文件是 [SKILL.md](SKILL.md) 的中文阅读版。为了兼容只识别固定 `SKILL.md` 名称的 Agent 宿主，运行时仍以英文 `SKILL.md` 为主入口；两份文件表达相同的工作流与边界。

把图视为可校验的模型，而不是装饰。先保留业务事实并选择一种图法，再校验结构并使用确定性渲染器输出。

## 开始前：识别模型

先确定图的**目的**、**语义层次**和**图形记法**，然后阅读 [references/routing.md](references/routing.md)。用户说“SC 图”时，必须确认其指的是 **Structure Chart（结构图）** 还是 **Statechart（状态机图）**，不可猜测。

材料缺少会改变核心模型的事实时，提出一个最小化澄清问题。其他未知内容写为 `TBD` 或 `assumption`，并说明影响。禁止补造实体、字段、基数、关系、过程步骤、状态、指标或数据。

先创建 IR，再创建渲染器源码。JSON 是无额外依赖的默认格式；安装了 PyYAML 时也可使用 YAML。参照 [schemas/diagram-ir.schema.json](schemas/diagram-ir.schema.json) 与 `templates/` 中的对应模板。

## 按图型读取规则

- ERD、数据库、实体、PK/FK、基数：读 [references/er-modeling.md](references/er-modeling.md)。
- 程序或算法控制流：读 [references/flowchart-iso5807.md](references/flowchart-iso5807.md)。
- 外部实体、处理、数据存储与数据移动：读 [references/dfd.md](references/dfd.md)。
- 用例、时序、活动、状态机、组件或部署：读 [references/uml.md](references/uml.md)。
- Structure Chart、功能分解、WBS：读 [references/structure-chart.md](references/structure-chart.md)。
- 论文/报告表格：读 [references/table-style.md](references/table-style.md)。

## 强制工作流

1. 生成 `diagram.ir.json`（或 YAML），必须写入图名、用途、`diagram_type`、`semantic_level`、`notation`、需求来源、假设与 TBD。
2. 渲染前校验：

   ```powershell
   python scripts/validate_ir.py diagram.ir.json --report validation.json
   ```

   只修复已知事实。警告只有在最终图注或交接说明中披露时才可保留。
3. 按图法选择渲染器，不能因为方便随意选择：PlantUML 优先用于 UML 与 IE ERD；Graphviz 用于层次和布局；Mermaid 只用于其记法足够的简单图；需要 BPMN 图元或人工可编辑排版时使用 Draw.io。
4. 生成 IR 可追溯的可编辑源码：`.puml`、`.dot`、`.mmd` 或 `.drawio`。
5. 优先输出 SVG/PDF，再按文档兼容性需要生成 PNG。示例：

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/discover-tools.ps1
   python scripts/render.py source.puml --format svg
   python scripts/inspect_output.py output.svg --report output-inspection.json
   ```

6. 在正常阅读尺寸下检查文字截断、重叠、箭头方向、标签遮挡和留白；修正源码后重新渲染。截图只能用于视觉 QA，不能替代交付图。
7. 交付 IR、源码、SVG/PDF、必要的 PNG、校验报告、检查报告、记法、渲染器版本和未决假设。

## 缺少渲染器时：先请求授权

默认只读探测，绝不自动下载或安装。所选渲染器缺失时，先生成计划：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-renderer.ps1 -Plan -Renderer plantuml
```

然后说明：缺少的命令、该渲染器为何必要、建议 Scoop 位置/bucket/包名、依赖、网络和磁盘副作用，以及不安装时“只交付 IR + 源码 + 阻塞说明”的后备方案。最后只问一个明确问题：

> 是否授权按上述方案安装？

收到“可以/同意”只授权已展示的计划。改变包、bucket、安装位置、全局安装或提升权限时，必须重新展示计划并再次征得同意。安装后重新探测命令，并渲染一个最小 SVG 测试，不能仅因 Scoop 显示包名就宣称工具可用。

## 不可跨越的建模边界

- 一张 ERD 不混用 Chen、Crow's Foot/IE 与 IDEF1X。
- `1:N` 只描述最大基数，不等于参与是否可选；IR 必须保留两端各自的最小值和最大值。
- 概念 Chen ERD 可以直接表达 `M:N`；逻辑关系模型或物理模式必须用关联实体/关联表转换为两条 `1:N`。
- DFD 描述数据移动，不描述时间、控制决策或程序顺序；程序流程图描述控制流，不描述数据存储或主外键。
- Structure Chart 描述模块层次与耦合，不是流程图；Statechart 描述状态与事件转换。
- Office/WPS/POI 只能插入已校验图或生成已规范化的原生表格，不能作为主要的图形语义绘制器。

## 校验、修复与停止条件

`scripts/validate_ir.py` 负责 IR 的通用规则和 ER、DFD、流程图的不变量；渲染器语法错误与语义错误分别记录。最多尝试两轮不引入新业务事实的机械修复。若仍需要未知事实，停止并写清楚问题或 `TBD`，不得声称“图已正确”。

## 表格

先阅读 [references/table-style.md](references/table-style.md)。学校、期刊、甲方或用户提供的模板优先；没有模板时，在适合的场景使用克制的三线表。不要默认蓝色表头、渐变、阴影或彩色边框。表题在上，来源和注释在下；数字对齐和精度一致；不得编造数据、单位、口径或来源。

## 工具安装边界

阅读 [references/tooling.md](references/tooling.md)。未获明确授权时，禁止安装软件、修改 PowerShell 执行策略、增加 Scoop bucket、迁移既有 Scoop、全局安装或提升权限。Windows 新装 Scoop 的计划默认使用 `D:\Scoop`；已有 Scoop 安装默认复用但不迁移。
