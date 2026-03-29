---
name: asset-authoring
description: >
  AI Agent 资产编写指南。当需要创建或修改 Skills、Workflows、Rules 时使用此技能。
  提供 frontmatter 元数据规范、目录结构约束、样板模板和校验脚本。
scope: universal
author: 渡山源码
project: dushan-agent-assets
---

# AI Agent 资产编写指南

本技能指导如何为 DuShan DevOps 平台编写标准化的 AI Agent 资产（Skills / Workflows / Rules）。

## 资产分类与目录结构

```
dushan-agent-assets/
├── skills/              # 技能（目录型，含 SKILL.md + 子结构）
│   └── {skill-name}/
│       ├── SKILL.md     # 技能主文档（必须）
│       ├── scripts/     # 辅助脚本（可选）
│       ├── templates/   # 模板文件（可选）
│       ├── examples/    # 示例文件（可选）
│       └── reference/   # 参考文档（可选）
├── workflows/           # 工作流（单文件型 .md）
│   └── {workflow-name}.md
└── rules/               # 规则（单文件型 .md）
    └── {rule-name}.md
```

> **IDE 挂载路径约定**：Skills → `.agent/skills/`（单数），Workflows → `.agents/workflows/`（复数），Rules → `.agents/rules/`（复数）。

---

## Frontmatter 元数据规范

每个 MD 文件**必须**在第一行以 `---` 开始的 YAML frontmatter。

### 字段定义

| 字段          | 类型   | Rules | Workflows | Skills | 说明                       |
| ------------- | ------ | :---: | :-------: | :----: | -------------------------- |
| `description` | string | 必须  |   必须    |  必须  | 资产描述（命名规范见下方） |
| `project`     | string | 必须  |   必须    |  推荐  | 所属项目名，用于过滤       |
| `scope`       | string | 必须  |   必须    |  推荐  | 适用范围                   |
| `author`      | string | 推荐  |   推荐    |  推荐  | 作者或团队                 |
| `trigger`     | string | 推荐  |     -     |   -    | 触发方式（Rules 专用）     |
| `name`        | string |   -   |     -     |  推荐  | 技能名称（Skills 专用）    |

### description 命名规范

**格式**：`【资产类型】scope标题 — 概要描述`

方括号内放**资产类型**（工作流 / 规则 / 技能），scope 信息（前端/后端/DevOps）放在标题正文中。
此格式确保在 IDE 的 `/` 斜杠命令选择器中一眼区分资产类型和所属领域。

**Rules 示例**：

```
【规则】后端全局编码原则 — 11 条基准规范
【规则】后端架构决策 — 8 条不可违反规则
【规则】前端全局编码原则 — 10 条基准规范
【规则】DevOps 编码规范 — module_devops 模块化架构
```

**Workflows 示例**：

```
【工作流】后端开发辅助 — 加载规范 → 编写代码 → Lint 验收
【工作流】后端代码审查 — L0 Lint → L1 MCP → L2 深度 → 评分报告
【工作流】前端开发辅助 — 加载规范 → 编写代码 → Lint 验收
【工作流】DevOps 开发辅助 — 加载规范 → 编写代码 → 验收
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

### Rules 模板

```yaml
---
description: 【规则】后端全局编码原则 — 概要描述
trigger: always_on
scope: backend
author: 渡山源码
project: dushan-admin-backend
---
# 规则标题

1. 规则条目一 — 简要说明
2. 规则条目二 — 简要说明
3. 规则条目三 — 简要说明
```

**编写要求**：

- 每条规则一行，编号列表
- 用 `—` 分隔规则名和说明
- 聚焦"不可违反"的硬约束，避免建议性描述
- 总条目控制在 8-12 条以内

### Workflows 模板

```yaml
---
description: 【工作流】后端开发辅助 — 步骤概要
scope: backend
author: 渡山源码
project: dushan-admin-backend
---

# /workflow-name — 工作流标题

> 用法：`/workflow-name {参数}` — 一句话说明用途。

## Step 1: 步骤标题

步骤描述...

## Step 2: 步骤标题

步骤描述...

---

## MCP 工具速查

| MCP 服务 | 工具 | 阶段 | 用途 |
|---------|------|:----:|------|
| `mcp-name` | `tool_name` | Step N | 说明 |
```

**编写要求**：

- 使用 `## Step N:` 格式编号步骤
- 每个步骤明确输入/输出/操作
- 涉及 MCP 调用的步骤写明具体工具和参数
- 支持 `// turbo` 注解标记可自动执行的步骤
- 可在开头添加 YAML 配置块控制行为

### Skills 模板

```yaml
---
name: skill-name
description: >
  技能描述第一行。
  技能描述第二行。
scope: universal
author: 渡山源码
project: dushan-agent-assets
---

# 技能标题

简要介绍此技能的功能。

## 何时使用

- 触发场景一
- 触发场景二

## 何时不使用

- 排除场景一

## 工作流

### 1. 步骤一

说明和命令...

### 2. 步骤二

说明和命令...

## 注意事项

- 注意点一
- 注意点二
```

**编写要求**：

- `name` 必须与目录名一致
- `description` 使用 `>` 多行语法，首行为技能分类标签
- 必须包含"何时使用"和"何时不使用"章节
- 含脚本时放在 `scripts/` 子目录
- 引用子文件用相对路径

---

## 校验

编写完成后运行校验脚本检查 frontmatter 合规性：

```bash
# 校验单个文件
python scripts/validate_frontmatter.py ../../rules/backend-global.md

# 校验整个资产目录
python scripts/validate_frontmatter.py ../../../dushan-agent-assets

# 校验并输出 JSON 格式
python scripts/validate_frontmatter.py ../../../dushan-agent-assets --format json
```

校验内容包括：

- frontmatter 是否存在且格式正确
- `description` 是否缺失
- `project` 值是否在有效范围内
- Skills 的 `name` 是否与目录名一致
- Rules 的 `trigger` 是否为有效值

---

## 常见问题

**Q: Rules 和 Workflows 的 `description` 有什么区别？**

- Rules 的 `description` 直接作为标题下方的提示显示
- Workflows 的 `description` 同时作为斜杠命令的描述

**Q: 通用 Skill 需要设 `project` 吗？**

- 不需要。不设 `project` 的资产在"全部/通用"中展示
- 如果某 Skill 仅服务于特定项目，必须设 `project`

**Q: 如何让新增的 `project` 值出现在过滤下拉框？**

- frontmatter 中写入 `project: 新项目名` 即可
- DevOps 前端会自动收集所有 `project` 值，无需额外注册
