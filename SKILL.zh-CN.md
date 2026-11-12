---
name: academic-diagram-renderer
description: 为中文论文、毕业设计、项目报告、需求分析和系统设计文档创建、审查、校验、渲染或插入语义正确的图与克制的学术表格。涉及 ER/ERD、概念与逻辑数据库设计、概念结构设计、逻辑结构设计、数据库表设计、系统结构图/SC、系统功能结构图、系统逻辑架构图、业务流程图、跨职能泳道图、部署架构图、DFD、流程图、BPMN、Structure Chart/SC、Statechart、UML、架构、数据库模式、功能分解或报告表格，且图例、基数、符号、箭头、小节放置、单色/打印风格或可复现渲染很重要时使用；不用于装饰性插画或普通 Office 形状绘制。
---

# 学术图表渲染器

把图视为可校验的模型，而不是装饰。先保留业务事实并选择一种图法，记录来源，再校验结构并使用确定性渲染器输出。

## 开始前：识别模型

先确定图的**目的**、**语义层次**和**图形记法**，然后阅读 [references/routing.md](references/routing.md)。用户说“SC 图”时，必须确认其指的是 **Structure Chart（结构图）** 还是 **Statechart（状态机图）**，不可猜测；用户说“结构图”时，还要确认是 **模块/调用结构（SC）** 还是 **功能分解图**。

材料缺少会改变核心模型的事实时，提出一个最小化澄清问题。其他未知内容写为 `TBD` 或 `assumption`，并说明影响。禁止补造实体、字段、基数、关系、过程步骤、状态、指标或数据。

先创建 IR，再创建渲染器源码。JSON 是无额外依赖的默认格式；安装了 PyYAML 时也可使用 YAML。参照 [schemas/diagram-ir.schema.json](schemas/diagram-ir.schema.json) 与 `templates/` 中的对应模板。

## 文档小节契约

报告的小节名称决定要建哪种模型。放置 ERD 前先读 [references/section-contract.md](references/section-contract.md)。

| 小节 | 必需模型 | 必需记法 | 证明什么 |
| --- | --- | --- | --- |
| 概念结构设计 / 概念模型 / 数据需求 | `conceptual_er` | `chen` | 矩形、**业务属性**、动词菱形；允许 M:N；**无外键** |
| 逻辑结构设计 / 数据库表设计 / 表结构设计 | `logical_relational` | `crow_foot_ie` | 表、**PK/FK**、关联表、已拆解的 M:N |
| 物理结构设计 / 索引与存储设计 | `physical_schema` | `crow_foot_ie` 或明确的物理记法 | SQL 类型、索引、物理约束 |

同一文档同时有概念节和逻辑/表设计节时，必须出**两张独立图**：概念节用 Chen，逻辑/表设计节用 Crow's Foot。不能一图两用，也不能为了让 Chen 图“更完整”而塞入外键。概念图里出现 `_id`、表前缀或中间表，说明层次已经塌陷，不能再证明业务理解。

在 IR 的 `section` 字段记录目标小节。成对交付时，两张 IR 都要校验，并按 [references/section-contract.md](references/section-contract.md) 的一致性表检查：每个概念 M:N 必须用 `resolves_to` 指明关联表，联系属性必须在该关联表中重新出现。

## 术语分流：不要合并不同视图

中文报告里这些词很像，但语义不同。选择记法前先读 [references/authority-map.md](references/authority-map.md)。

| 用户术语 | 模型类型 | 回答的问题 | 不要悄悄改成 |
| --- | --- | --- | --- |
| 系统结构图 / SC 图 / 模块结构图 | `structure_chart` | 哪些模块调用哪些模块，传递什么数据/控制偶？ | 系统功能结构图、流程图、状态图 |
| 系统功能结构图 | `functional_decomposition` | 一个能力如何分解为子功能？ | SC 的调用箭头、数据/控制偶、执行顺序 |
| 系统逻辑架构图 | `logical_architecture` | 有哪些逻辑层/组件、职责是什么、允许什么依赖？ | 部署节点、IP/端口、服务器拓扑 |
| 基本业务流程图 | `business_flow`（`flow_variant: basic`） | 单一角色按什么活动/判断顺序处理一个事项？ | 多角色泳道、程序控制流、DFD |
| 跨职能业务流程图 | `business_flow`（`flow_variant: cross_functional`） | 多个角色/部门如何交接一个事项？ | 单角色流程、模块调用图、纯组织架构图 |
| 部署架构图 | `deployment` | 有哪些运行节点、执行环境、制品和通信路径？ | 逻辑分层、业务流程图、模块调用图 |

`SC` 是歧义缩写；`结构图` 也是。**有调用箭头和数据/控制偶的是 SC；只有父子功能线的是功能分解。**

用户只说“系统结构图 / SC”，且 DFD 呈输入—处理—输出形态时，**默认画变换型 SC**（输入支 + 中心变换 + 输出支），不要默认画事务型 SC；只有存在事务中心/按类型分派，或用户明确要求事务分析时才画事务型。**系统功能结构图默认自上而下纵向延伸**（根在上、子功能向下），不要默认画成横向树。

## 单色视觉基线

每张图都在 IR 中声明视觉策略，默认使用最基础的色调：

```json
"visual_style": {
  "palette": "monochrome",
  "background": "#FFFFFF",
  "foreground": "#111111",
  "fills": ["#FFFFFF", "#F2F2F2"],
  "color_usage": "none"
}
```

白底、黑/深灰线条与文字、至多一个浅灰填充；不使用彩色、渐变、阴影或 3D。形状、线型、线宽和文字标签承担语义，颜色不承担语义。学校/期刊模板要求彩色是唯一例外：使用 `palette: "template"`，记录 `template_reference`，并保证灰度可读。具体色板、记法样式、渲染器设置和打印检查见 [references/visual-style.md](references/visual-style.md)。

默认单色，并在渲染后用 `check_monochrome.py` 验收，不能只在口头上说“用了单色”。

## 按图型读取规则

- ERD、数据库、实体、PK/FK、基数：读 [references/er-modeling.md](references/er-modeling.md)。
- 小节放置、概念/逻辑成对交付：读 [references/section-contract.md](references/section-contract.md)。
- 规范依据与引用：读 [references/notation-evidence.md](references/notation-evidence.md)。
- 单色色板与渲染器设置：读 [references/visual-style.md](references/visual-style.md)。
- 程序或算法控制流：读 [references/flowchart-iso5807.md](references/flowchart-iso5807.md)。
- 外部实体、处理、数据存储与数据移动：读 [references/dfd.md](references/dfd.md)。
- 用例、时序、活动、状态机、组件或部署：读 [references/uml.md](references/uml.md)。
- Structure Chart（SC）、功能分解：读 [references/structure-chart.md](references/structure-chart.md)。
- 逻辑架构、部署架构：读 [references/architecture-views.md](references/architecture-views.md)。
- 基本或跨职能业务流程图：读 [references/business-flow.md](references/business-flow.md)。
- 六类图的来源等级、P1–P6 示例证据、权威图：读 [references/authority-map.md](references/authority-map.md)。
- 论文/报告表格：读 [references/table-style.md](references/table-style.md)。

## 强制工作流

1. 生成 `diagram.ir.json`（或 YAML），写入图名、用途、`section`、`diagram_type`、`semantic_level`、`notation`、`visual_style`、需求来源、假设/TBD 和模型元素。业务流程图加 `flow_variant: basic|cross_functional`；逻辑/部署架构加 `viewpoint: logical|deployment`。
2. 渲染前校验：

   ```powershell
   python scripts/validate_ir.py diagram.ir.json --report validation.json
   ```

   只修复已知事实。警告只有在最终图注或交接说明中披露时才可保留。校验器会拦截概念 Chen 图中的 FK、逻辑图中的未拆 M:N、概念节里的 Crow's Foot、彩色 palette，以及架构/业务流程中的基本不变量。
3. 按图法选择渲染器，不能因为方便随意选择：PlantUML 优先用于 UML 与 IE ERD；Graphviz 用于 Chen ERD、层次和布局敏感图；Mermaid 只用于其记法足够的简单图；需要 BPMN 图元或人工可编辑排版时使用 Draw.io。发现工具缺失时，先读 [references/tooling.md](references/tooling.md)，给出安装计划并等待授权。
4. 生成 IR 可追溯的可编辑源码：`.puml`、`.dot`、`.mmd` 或 `.drawio`。在源码中显式设置单色色板，不要依赖渲染器默认值。Chen ERD 如使用固定 `pos="x,y!"` 坐标，用 `--engine neato --fixed` 渲染，避免自动布局把图拉成竖条。
5. 优先输出 SVG/PDF，再按文档兼容性需要生成 PNG。示例：

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/discover-tools.ps1
   python scripts/render.py source.puml --format svg
   python scripts/inspect_output.py output.svg --report output-inspection.json
   python scripts/check_monochrome.py output.svg --report output-monochrome.json
   ```

   单色检查是验收的一部分，不是可选项。发现色相时修源码重渲染，不要手改 SVG。
6. 在正常阅读尺寸和灰度下检查文字截断、重叠、箭头方向、标签遮挡和留白；修正源码后重新渲染。截图只能用于视觉 QA，不能替代交付图。
7. 交付 IR、源码、SVG/PDF、必要时的 PNG、校验报告、检查报告、单色报告、记法、渲染器版本和未决假设。概念/逻辑成对交付时，明确小节放置和 M:N 映射；结构/架构/流程类图要说明来源等级：正式标准、经典教材、政府指南或事实约定。

## 不可跨越的建模边界

- 一张 ERD 不混用 Chen、Crow's Foot/IE 与 IDEF1X。
- `1:N` 只描述最大基数，不等于参与是否可选；IR 必须保留两端各自的最小值和最大值。
- 概念 Chen ERD 可以直接表达 `M:N`；逻辑关系模型或物理模式必须用关联实体/关联表转换为两条 `1:N`。
- 概念 Chen ERD 含业务属性，但不含外键、表前缀、SQL 类型或物理索引。
- 逻辑 Crow's Foot ERD 含 PK/FK 和已拆解的 M:N，不以 Chen 菱形作为主要联系符号。
- Structure Chart 描述模块层次/调用和数据/控制偶，不是功能分解树、流程图或 Statechart。
- 调用箭头表示控制权转移；数据/控制偶是**额外的细箭头**（空心/实心圆），不能只在调用箭头上写 `D:`/`C:` 代替。
- 无明显变体且 DFD 为输入—处理—输出形态时，默认画变换型 SC，而不是事务型 SC；只有存在事务中心/按类型分派时才用事务分析。
- 功能分解只表达 `is composed of` 层次，不能出现调用箭头、数据/控制偶、循环或判定；默认布局是自上而下纵向树，功能框为竖向矩形（高≥宽），不是横向长条或横向树。
- 逻辑架构展示层/组件/职责/依赖，不能出现运行节点、IP、端口或部署拓扑。
- 部署图展示运行节点、执行环境、制品和通信路径，不能出现业务活动或逻辑层带。
- 基本业务流程图是单角色活动/判断顺序；跨职能流程图有多角色/泳道和明确交接。两者都不是程序流程图。
- DFD 描述数据移动，不描述时间、控制决策或程序顺序；程序流程图描述控制流，不描述数据存储或主外键。
- Statechart 描述状态与事件转换，不是调用层次或流程图。
- Office/WPS/POI 只能插入已校验图或生成已规范化的原生表格，不能作为主要的图形语义绘制器。
- 颜色不能作为唯一语义载体；默认 palette 是单色。

## 校验、修复与停止条件

`scripts/validate_ir.py` 负责 IR 的通用规则，以及 ER、DFD、流程图、SC/功能分解、逻辑/部署架构、业务流程、状态机、表格的不变量。渲染器语法错误与语义错误分别记录。最多尝试两轮不引入新业务事实的机械修复。若仍需要未知事实，停止并写清楚问题或 `TBD`，不得声称“图已正确”。

## 表格

先阅读 [references/table-style.md](references/table-style.md)。学校、期刊、甲方或用户提供的模板优先；没有模板时，在适合的场景使用克制的三线表。不要默认蓝色表头、渐变、阴影或彩色边框。表题在上，来源和注释在下；数字对齐和精度一致；不得编造数据、单位、口径或来源。

## 工具安装边界

阅读 [references/tooling.md](references/tooling.md)。未获明确授权时，禁止安装软件、修改 PowerShell 执行策略、增加 Scoop bucket、迁移既有 Scoop、全局安装或提升权限。Windows 新装 Scoop 的计划默认使用 `D:\Scoop`；已有 Scoop 安装默认复用但不迁移。
