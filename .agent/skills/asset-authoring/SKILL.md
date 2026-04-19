---
name: asset-authoring
description: >
  AI Agent 资产编写指南。当需要创建或修改 Skills、Rules 时使用此技能。
  提供 frontmatter 元数据规范、目录结构约束、样板模板和校验脚本。
scope: universal
author: 渡山源码
project: dushan-agent-assets
---

# AI Agent 资产编写指南

本技能指导如何为 DuShan DevOps 平台编写标准化的 AI Agent 资产（Skills / Rules）。本指南全面拥抱 Skills 架构，废弃了旧版的 Workflows 概念。

## 资产分类与目录结构

```text
dushan-agent-assets/
├── skills/              # 技能（目录型，含 SKILL.md + 子结构）
│   └── {skill-name}/
│       ├── SKILL.md     # 技能主文档（必须，包含触发条件和工作流步骤）
│       ├── scripts/     # 辅助脚本（可选）
│       ├── templates/   # 模板文件（可选）
│       ├── examples/    # 示例文件（可选）
│       └── reference/   # 参考文档（可选，存放详细架构约束）
└── rules/               # 规则探针（单文件型 .md）
    └── {rule-name}.md   # 仅作为强制读取对应 Skill 的轻量指针
```

> **IDE 挂载路径约定**：Skills → `.agent/skills/`（单数），Rules → `.agents/rules/`（复数）。

---

## Frontmatter 元数据规范

每个 MD 文件**必须**在第一行以 `---` 开始的 YAML frontmatter。

### 字段定义

| 字段          | 类型   | Rules | Skills | 说明                       |
| ------------- | ------ | :---: | :----: | -------------------------- |
| `description` | string | 必须  |  必须  | 资产描述（命名规范见下方） |
| `project`     | string | 必须  |  推荐  | 所属项目名，用于过滤       |
| `scope`       | string | 必须  |  推荐  | 适用范围                   |
| `author`      | string | 推荐  |  推荐  | 作者或团队                 |
| `trigger`     | string | 推荐  |   -    | 触发方式（Rules 专用）     |
| `name`        | string |   -   |  推荐  | 技能名称（Skills 专用）    |

### description 命名规范

**格式**：`【资产类型】scope标题 — 概要描述`

方括号内放**资产类型**（规则 / 技能），scope 信息（前端/后端/DevOps）放在标题正文中。
此格式确保在 IDE 中快速区分资产类型和所属领域。

**Rules 示例**：

```text
【规则】后端全局编码入口 — 强制加载 backend-dev 技能
【规则】前端全局编码入口 — 强制加载 frontend-dev 技能
```

**Skills 示例**（使用 `>` 多行语法）：

```
【技能】后端 Lint — Python/SQL 代码规范检查
【技能】前端 Lint — Vue/TypeScript 代码规范检查
【技能】资产编写指南 — Skills/Workflows/Rules 编写规范
```

### 字段值约束

**`project`（项目名）**：

- 必须与生态模块 key 严格匹配
- 当前有效值：`dushan-admin-backend`、`dushan-admin-frontend`、`dushan-agent-assets`、`dushan-devops`、`dushan-codegen-mcp`、`dushan-graph-mcp`
- 不设 `project` 的资产被视为"通用"，在"全部/通用"过滤下展示

**`scope`（适用范围）**：

- `backend` — 后端专属
- `frontend` — 前端专属
- `devops` — DevOps 专属
- `universal` — 通用（默认值）

**`trigger`（触发方式，Rules 专用）**：

- `always_on` — 始终生效
- `on_demand` — 按需触发

---

## 样板模板

### Rules 模板（MCP 指针）

```yaml
---
description: 【规则】后端全局编码入口 — 强制从 codegen-mcp 获取规则
trigger: always_on
scope: backend
author: 渡山源码
project: dushan-admin-backend
---
# 后端开发强制规则

> ⚠️ 所有编码规范由 `dushan-codegen-mcp` 知识库统一管理。

**核心指令**：

1. 编写代码前，通过 CLI 获取最新规则：
   `python -m cli rules <file_path> --mode codegen --format json`

2. 加载并遵循 `.agent/skills/backend-dev/SKILL.md` 的 Preflight 门禁。

3. 编写完成后运行 Lint 验收。

> 禁止在此文件内硬编码具体规则条目。规则的唯一源头是 codegen-mcp 知识库。
```

**编写要求**：

- Rules 文件仅作为 IDE 全局注入的**轻量 MCP 指针**。
- 禁止在 Rules 中硬编码具体编码规范条目。
- 将 Rules 指向 `codegen-mcp CLI` 获取最新规则，和对应的 Fat Skill 执行开发流程。
- 具体业务逻辑、开发步骤和架构约束全部下沉到 Skills 的 `SKILL.md` 或 `reference/` 中。

### Skills 模板

````yaml
---
name: skill-name
description: >
  【技能】领域描述 — 功能概要第一行。
  适用场景补充。
scope: backend
author: 渡山源码
project: dushan-admin-backend
---

# 技能标题

> 用法：触发此 Skill 后，按以下步骤完成任务。

```yaml
auto_trigger: true   # 是否自动触发（false = 仅手动触发）
preflight: true      # 是否强制 Preflight 门禁
auto_lint: true      # 是否编写完成后自动运行 Lint
````

---

## 何时使用

- 触发场景一
- 触发场景二

## 何时不使用

- 排除场景一
- 排除场景二

## Step 0: Preflight — 构建任务上下文（可选门禁）

> 高风险任务建议启用此步骤。

```bash
cd dushan-mcp/dushan-codegen-mcp
python -m cli rules <file_path> --mode codegen --format json
```

## Step 1: 识别任务和文件类型

文件类型映射表...

## Step 2: 编写/修改代码

遵守 Step 0 返回的规范...

## Step 3: Lint 验收

```bash
cd .agent/skills/lint/scripts
python <lint_script>.py <file_path> --format summary
```

## 注意事项

- 注意点一
- 注意点二

````

**编写要求**：

- `name` 必须与目录名一致
- `description` 使用 `>` 多行语法，首行为 `【技能】` 分类标签
- 必须包含"何时使用"和"何时不使用"章节
- 含脚本时放在 `scripts/` 子目录
- 引用子文件用相对路径
- 涉及编码的 Skill 建议包含 Preflight → 编码 → Lint 三段式结构
- `auto_trigger: false` 的 Skill 仅在用户手动要求时触发，不混入自动链路

### 成熟 Skill 范例（推荐参考）

编写新 Skill 前，建议先阅读以下已落地的 Skill 作为参照：

| Skill | 位置 | 特点 |
|-------|------|------|
| `backend-dev` | `dushan-admin-backend/.agent/skills/backend-dev/SKILL.md` | Preflight 门禁 + CLI 规则获取 + Lint 验收 |
| `backend-test` | `dushan-admin-backend/.agent/skills/backend-test/SKILL.md` | 手动触发 + 独立于自动链路 |
| `frontend-dev` | `dushan-admin-frontend/.agent/skills/frontend-dev/SKILL.md` | 前端三段式 + Preflight |
| `forge-codegen` | `dushan-devops-agents/.agent/skills/forge-codegen/SKILL.md` | CLI 驱动 + 文件类型映射 |


---

## 校验

编写完成后运行校验脚本进行全量 Lint 检查：

```bash
# 校验单个文件
python scripts/validate_frontmatter.py ../../rules/backend-global.md

# 校验整个资产目录（dushan-agent-assets 的 skills/ + rules/）
python scripts/validate_frontmatter.py ../../../dushan-agent-assets

# 校验任意项目工作区的 .agent/skills/ + .agents/rules/
python scripts/validate_frontmatter.py ../../../dushan-admin-backend --workspace

# JSON 格式输出（供 CI 消费）
python scripts/validate_frontmatter.py ../../../dushan-agent-assets --format json
```

### 校验规则总览

#### Frontmatter 规则（FM-1 ~ FM-10）

| 规则 | 级别 | 说明 |
|------|------|------|
| FM-1 | ERROR | 缺少 YAML frontmatter |
| FM-2 | ERROR | 缺少 `description` 字段 |
| FM-3 | WARNING | `project` 值不在有效列表中 |
| FM-4 | INFO | 未设置 `project`（归类为通用） |
| FM-5 | WARNING | `scope` 值无效 |
| FM-6 | ERROR | Skills `name` 与目录名不一致 |
| FM-7 | WARNING | Skills 未设置 `name` |
| FM-8 | WARNING | Rules `trigger` 值无效 |
| FM-9 | INFO | Rules 未设置 `trigger` |
| FM-10 | INFO | 发现未知 frontmatter 字段 |

#### Skills 内容规则（SK-1 ~ SK-8）

| 规则 | 级别 | 说明 |
|------|------|------|
| SK-1 | WARNING | `description` 未以 `【技能】` 开头 |
| SK-2 | WARNING | 缺少"何时使用"或"何时不使用"章节 |
| SK-3 | WARNING | SKILL.md 超过 600 行 |
| SK-4 | WARNING | H2 章节超过 15 个 |
| SK-5 | ERROR | 缺少 H1 标题 |
| SK-6 | INFO | 包含 TODO / FIXME / HACK 标记 |
| SK-7 | WARNING | 引用了不存在的 scripts/ 文件 |
| SK-8 | WARNING | 存在空代码块 |

#### Rules 内容规则（RL-1 ~ RL-4）

| 规则 | 级别 | 说明 |
|------|------|------|
| RL-1 | INFO | `description` 未以 `【规则】` 开头 |
| RL-2 | WARNING | 正文未引用 MCP CLI 指令（非指针模式） |
| RL-3 | WARNING | 正文超过 50 行（指针应轻量） |
| RL-4 | INFO | 包含实现代码块（应下沉到 Skills） |

#### 目录结构规则（DIR-1 ~ DIR-3）

| 规则 | 级别 | 说明 |
|------|------|------|
| DIR-1 | ERROR | Skill 目录缺少 SKILL.md |
| DIR-2 | INFO | 发现非标准文件/目录 |
| DIR-3 | INFO | scripts/ 目录存在但为空 |

---

## 常见问题

**Q: 为什么废弃 Workflows？**

- 为了统一资产架构。Workflows 本质上是分步操作指南，这完全可以融合进 Skills 中。统一使用 Skills 能够更好地保证跨各种 AI IDE (Claude Code, Cursor, Windsurf) 的兼容性和上下文高内聚。

**Q: 通用 Skill 需要设 `project` 吗？**

- 不需要。不设 `project` 的资产在"全部/通用"中展示
- 如果某 Skill 仅服务于特定项目，必须设 `project`

**Q: 如何让新增的 `project` 值出现在过滤下拉框？**

- frontmatter 中写入 `project: 新项目名` 即可
- DevOps 前端会自动收集所有 `project` 值，无需额外注册
````
