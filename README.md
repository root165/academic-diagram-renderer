# Academic Diagram Renderer

为中文论文、毕业设计、项目报告、需求分析与系统设计文档生成**语义正确、符号规范、可复现且可审计**的图与表。

它不是“让模型随手画一张图”的提示词集合。它把自然语言需求先约束为可检查的中间表示（IR），再选择合适的图法和渲染器；缺少事实时保留 `TBD`，缺少工具时请求用户授权安装，而不是把手写 SVG、Office 形状或一段 Mermaid 文本伪装成已经验证的成图。

阅读入口：[中文运行说明](SKILL.zh-CN.md) · [English runtime entry](SKILL.md)

## 适用范围

- 概念 ER 图、逻辑关系模型、物理数据库模式
- DFD、程序流程图、BPMN
- UML 用例、时序、活动、状态机、组件、部署图
- Structure Chart（结构图）、功能分解图、WBS
- 论文三线表、需求追踪表、字段字典、风险和决策表

不适合用于装饰性插画、海报、思维导图，或只想在 Word/WPS 中拖拽形状排版的任务。

## 为什么需要它

常见的 AI 绘图问题不是“不会画矩形”，而是把不同层次和不同记法混在一起：在 ERD 使用流程箭头，把 DFD 画成程序流程，把 Structure Chart 画成时间线，或在没有需求依据时杜撰字段和基数。

本项目用下列边界抑制这些问题：

1. **先建模，后绘制**：自然语言 → IR → 语义校验 → 源码 → 渲染 → 视觉验收。
2. **模型层次明确**：概念 ER、逻辑关系模型、物理模式不会混为一谈。
3. **记法单一**：同一 ERD 只使用 Chen、Crow's Foot/IE 或 IDEF1X 之一。
4. **事实可追溯**：图的元素关联到需求编号、段落或资料来源；未知信息显式标为 `TBD`/`assumption`。
5. **渲染可证明**：优先 SVG/PDF；PNG 仅用于兼容。手写 SVG 不得被称为“渲染结果”。
6. **安装需授权**：发现必要渲染器不存在时，先给出安装计划并等待用户同意。

## 项目结构

```text
academic-diagram-renderer/
├── SKILL.md                    # Agent 的入口、路由与工作流
├── agents/openai.yaml          # 可选的 OpenAI/Codex UI 元数据
├── references/                 # 按图型按需加载的规则
│   ├── routing.md
│   ├── er-modeling.md
│   ├── flowchart-iso5807.md
│   ├── dfd.md
│   ├── uml.md
│   ├── structure-chart.md
│   ├── table-style.md
│   └── tooling.md
├── schemas/diagram-ir.schema.json
├── templates/                  # IR 起始模板
├── scripts/
│   ├── discover-tools.ps1
│   ├── install-renderer.ps1
│   ├── validate_ir.py
│   ├── render.py
│   └── inspect_output.py
└── evals/                      # 开发/回归测试，不是运行时必需项
```

## 安装

### 先理解可移植性

本项目采用通用的 **Agent Skill 目录** 形式：根目录的 `SKILL.md` 是必要入口，`references/`、`templates/` 和 `scripts/` 是同目录资源。因此它可以被支持“读取本地技能目录 + 执行工作区命令”的 Agent 使用。

不同产品的“技能注册目录”和导入 UI 不同，不能把某个产品的路径当成通用标准。若宿主不支持自动发现，仍可将整个目录作为工作区资源，并明确要求 Agent 在任务开始前读取 `SKILL.md`。

### 通用安装步骤

1. 克隆或下载本仓库。
2. **完整保留** `academic-diagram-renderer/` 目录层级；不要只复制 `SKILL.md`。
3. 将该目录复制到宿主 Agent 的技能目录，或在该 Agent 的配置中登记此目录。
4. 赋予 Agent 读取目录、运行 Python/PowerShell（如适用）和调用本机渲染器的权限。
5. 使用显式调用测试一次；如果宿主支持隐式匹配，也可让其按描述自动选中。

### Codex

OpenAI 的官方文档将用户级 Codex Skills 放在 `$HOME/.agents/skills`，仓库级 Skills 放在 `<repo>/.agents/skills`。因此，推荐的跨机器安装是：

```powershell
# 在仓库根目录执行；将 <repo-root> 替换为本仓库目录
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force "<repo-root>\academic-diagram-renderer" `
  "$HOME\.agents\skills\academic-diagram-renderer"
```

然后在 Codex 中用 `$academic-diagram-renderer` 显式调用，或直接提出与 ERD、DFD、流程图、UML、系统设计图或论文表格有关的任务。部分 Codex 桌面环境也提供 Skills 面板或额外扫描目录；以当前客户端显示的实际目录为准。若新增 Skill 没有立即出现，重启或重新加载 Skills。

官方参考：<https://learn.chatgpt.com/docs/build-skills>

### 其他 Agent / IDE

| 宿主能力 | 安装或接入方式 |
| --- | --- |
| 支持 Agent Skills / `SKILL.md` | 将整个目录放入该产品文档规定的 skills 根目录，并确认它会加载 `SKILL.md`。 |
| 支持项目级指令但不支持 Skills | 将整个目录保留在仓库中，在项目指令中要求 Agent 先阅读 `academic-diagram-renderer/SKILL.md`。 |
| 只支持系统提示词 | 将 `SKILL.md` 的内容作为系统/开发者指令，并同时提供 `references/`、`templates/`、`scripts/` 的可读路径。 |
| 不支持本地脚本执行 | 可使用规则和模板做建模审查，但不能宣称已完成确定性渲染或脚本校验。 |

若某个宿主使用插件/扩展分发机制，应将本目录作为插件中的 skill 资源；不要重新改写规则后再分发，以免丢失校验和授权门。

## 快速开始

### 1. 请求一张逻辑 ERD

```text
使用 academic-diagram-renderer：
为在线订餐系统画逻辑 ERD。
一个用户可创建 0..N 张订单，每张订单必须且仅属于一个用户；
订单与菜品为 M:N，数量和成交单价属于该关联。
输出 IR、可编辑源码、SVG 和验证报告；不要补充未给出的字段。
```

预期行为：Skill 选择逻辑关系模型和 Crow's Foot/IE，使用 `OrderItem` 关联实体，将数量和成交单价放在其中，保留未提供的主键策略为 `TBD`。如果 PlantUML/Graphviz 缺失，它会请求授权安装或交付“IR + 源码 + 阻塞说明”，不会伪造 SVG。

### 2. 请求一张 DFD

```text
使用 academic-diagram-renderer：
为图书馆借阅系统做 0 层 DFD。读者提交借阅申请；
系统查询馆藏库；系统返回借阅结果。使用 Gane–Sarson。
```

预期行为：读者是外部实体、馆藏库是数据存储、借阅处理是过程，箭头标注为“借阅申请”“馆藏信息”等数据名词；不会出现“是/否”判定菱形。

### 3. 使用内置校验器

JSON 是无额外依赖的默认 IR 格式：

```powershell
cd academic-diagram-renderer
python scripts/validate_ir.py path\to\diagram.ir.json --report validation.json
```

`validation.json` 记录错误、警告和通过状态。YAML 也可使用，但需要宿主已提供 `PyYAML`；缺少它时请改用 JSON 或在获得授权后安装依赖。

### 4. 渲染和验收

```powershell
powershell -ExecutionPolicy Bypass -File scripts/discover-tools.ps1
python scripts/render.py diagram.puml --format svg
python scripts/inspect_output.py diagram.svg --report output-inspection.json
```

最后仍需要在正常阅读尺寸下检查文字截断、重叠、箭头方向、标签遮挡和版面留白。`inspect_output.py` 检查格式与基本完整性，不替代视觉审阅。

## 缺少渲染器时的授权流程

工具探测只读；安装脚本默认拒绝任何副作用。

```powershell
# 只输出计划：不会安装、不会加 bucket、不会修改执行策略
powershell -ExecutionPolicy Bypass -File scripts/install-renderer.ps1 `
  -Plan -Renderer plantuml
```

Agent 应根据计划向用户说明缺什么、为什么需要、建议包/bucket、Scoop 目录、网络和磁盘影响，并询问：

> 是否授权按上述方案安装？

只有得到用户对**该方案**的明确同意后，Agent 才可带 `-Approved` 执行安装。新装 Scoop 的默认计划目录是 `D:\Scoop`；已有 Scoop 不会被迁移。`-InstallScoop`、新增 bucket、全局安装、管理员权限或改变目录都属于需要单独明确展示和授权的副作用。

建议的工具选择：

| 图型/需求 | 首选 | 说明 |
| --- | --- | --- |
| UML、IE/Crow's Foot ERD | PlantUML | 结构化源码、版本控制友好 |
| 树状层次、正交布局 | Graphviz | 适合结构图、功能分解 |
| 简单流程和简单时序 | Mermaid CLI | 仅在记法足够时使用 |
| BPMN 图元、可手工编辑排版 | Draw.io CLI | 导出前必须实测 CLI |

优先交付 SVG/PDF；只有文档软件不能良好处理矢量图时才提供高分辨率 PNG。不要用截图替代渲染产物。

## 工作流

```text
需求材料
  ↓
图型 + 模型层次 + 记法选择
  ↓
IR（来源 / 假设 / TBD）
  ↓
语义校验 ──失败──→ 仅修复已知事实；需要新事实时向用户提问
  ↓ 通过
可编辑渲染源码（.puml / .dot / .mmd / .drawio）
  ↓
工具探测 ──缺失──→ 安装计划 → 用户授权 → 安装与最小验证
  ↓ 可用
SVG/PDF 渲染 → 格式检查 → 视觉验收 → 插入报告
```

推荐把它与文档写作 Skill、需求分析 Skill 或代码仓库中的需求规格说明配合：

1. 需求分析先产出带编号的业务规则；
2. 本 Skill 将每个关键节点/关系映射到这些编号；
3. 论文/报告写作工具只插入已经验收的图与表；
4. 需求变化时修改 IR，再重新校验和渲染，而不是在文档中手工改图。

## 关键建模约束

### ERD

- 在 `conceptual_er`、`logical_relational`、`physical_schema` 中选择一层。
- Chen、Crow's Foot/IE、IDEF1X 不混用。
- `1:N` 仅描述最大基数，不能推断是否可选；IR 始终保存双向 `min` 与 `max`。
- 概念 ERD 可直接表示 `M:N`；逻辑/物理关系模型必须用关联实体或关联表拆解为两条 `1:N`。
- 只依赖“这对关联”的属性（例如数量、成交单价）属于关系/关联实体。

### 流程图与 DFD

- 程序流程图基于 ISO 5807：判定分支必须有清楚、互斥且完备的标签。
- DFD 选择 Yourdon–DeMarco 或 Gane–Sarson 一种记法；外部实体/数据存储为名词，过程为动词短语，数据流为数据名词。
- DFD 不表现时间顺序、判定菱形、控制流、PK/FK。

### UML、结构图和表格

- UML 以 UML 2.5.1 语义为基线；时序条件使用 `alt/opt/loop`，不使用流程图菱形。
- `SC 图` 必须先消歧：Structure Chart 是模块层级/耦合，Statechart 是状态与事件转换。
- 没有学校、期刊或甲方模板时，论文表默认采取克制的三线表；禁止因 Office 默认样式而使用蓝色表头、渐变或装饰性阴影。

## 依赖与安全边界

| 能力 | 最低要求 | 可选依赖 |
| --- | --- | --- |
| IR 校验 | Python 3.9+ | `PyYAML`（仅 YAML IR） |
| 工具探测/授权安装计划 | PowerShell 5.1+ | Scoop（仅获授权后） |
| PlantUML | Java | Graphviz（推荐） |
| Mermaid | Node.js | Mermaid CLI |
| Draw.io | Draw.io Desktop CLI | — |

本 Skill 不会自行下载安装软件、增加 Scoop bucket、改变执行策略、提升权限或迁移既有 Scoop 安装。所有此类动作必须经过用户明确授权，并在完成后重新探测版本和最小渲染样例。

## 质量门与交付清单

一次合格交付至少包含：

- `diagram.ir.json`：可追溯的模型；
- 可编辑源文件：`.puml`、`.dot`、`.mmd` 或 `.drawio`；
- `validation.json`：语义校验结果；
- SVG/PDF，及必要时的 PNG；
- `output-inspection.json`：格式检查结果；
- 图型、记法、渲染器版本、假设与未决项说明。

验证失败时，最多进行两轮不引入新业务事实的机械修复；仍需未知信息时，交付明确诊断和问题，而不是宣称“图已正确”。

## 开发与测试

```powershell
python <skill-creator-path>\scripts\quick_validate.py academic-diagram-renderer
python -m py_compile scripts\validate_ir.py scripts\render.py scripts\inspect_output.py
```

`evals/` 保存真实任务的回归用例。修改建模规则时，至少覆盖：

- 带可选性与关联实体的逻辑 ERD；
- DFD 与流程图的边界；
- `SC` 歧义；
- 渲染器缺失时的授权与降级行为；
- 三线表与既有文档模板的优先级。

## 规范与参考

- P. P.-S. Chen, *The Entity-Relationship Model—Toward a Unified View of Data*：<https://dl.acm.org/doi/10.1145/320434.320440>
- ISO 5807:1985：<https://www.iso.org/standard/11955.html>
- OMG UML 2.5.1：<https://www.omg.org/spec/UML/2.5.1/PDF>
- PlantUML IE 图：<https://plantuml.com/ie-diagram>
- OpenAI Skills：<https://learn.chatgpt.com/docs/build-skills>

## 贡献

欢迎提交图型规则、IR 校验规则、模板或可复现实例。请避免把单个课程模板或某一个渲染器的偶然语法写成普适标准；新增约束应说明其适用图型、模型层次、规范依据和可验证条件。
<<<<<<< HEAD
=======

>>>>>>> 08ab14292206705fb54483ac6a83fc091b0a7202
