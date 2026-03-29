---
description: 【工作流】前端开发辅助 — 加载规范 → 编写代码 → Lint 验收
scope: frontend
author: 渡山源码
project: dushan-admin-frontend
---

# /frontend-dev — 前端开发辅助

> 用法：`/frontend-dev {文件或目录或描述}` — 按规范编写/修改前端代码。

```yaml
# ── 开发配置 ──
auto_lint: true # 编写完成后自动运行 frontend-lint Skill 验收
architecture_docs: false # 是否加载架构文档（复杂改动时手动开启）
```

---

## Step 1: 识别任务和文件类型

分析用户的开发目标：

- **新建文件** → 需要识别文件类型
- **修改文件** → 需要加载该文件类型的编码规范

识别文件类型映射（按路径/命名自动判断）：

| 文件类型     | 识别特征                    | MCP 规范          |
| ------------ | --------------------------- | ----------------- |
| 页面 (views) | `views/*/index.vue`         | views.md          |
| 页面高级     | `views/*/` (表格/表单/弹窗) | views_advanced.md |
| 页面 Grid    | `views/*/` (vxe-grid)       | views_grid.md     |
| 组件         | `components/*.vue`          | component.md      |
| API          | `api/*/index.ts`            | api.md            |
| 路由         | `router/routes/`            | router.md         |
| 国际化       | `locales/`                  | i18n.md           |
| Hooks        | `hooks/` / composable       | hooks.md          |
| WebSocket    | `ws/` / websocket           | websocket.md      |

## Step 2: 加载编码规范（必须，不可跳过）

对目标文件调用 MCP 获取**该文件类型**的详细编码规范：

```
dushan-codegen-mcp → get_rules_for_file(file_path, mode="codegen")
```

返回的规范包含：结构要求 + 约束条目 + 代码示例。
Agent 必须逐条阅读规范内容，作为编写代码的唯一标准。

## Step 3: 加载架构知识（仅 architecture_docs=true 时）

涉及复杂架构改动时，按需加载：

```
dushan-codegen-mcp → read_knowledge("architecture/fullstack.md")    — 前后端联动
dushan-codegen-mcp → search_knowledge(相关关键词)                    — 搜索相关知识
```

## Step 4: 编写/修改代码

根据 Step 2 加载的规范 + `.agents/rules/global.md` 中的全局原则，编写代码。

编写要求：

1. 严格遵守 MCP 返回的文件类型规范
2. 严格遵守 `.agents/rules/global.md` 的前端全局编码原则
3. 修改文件保持现有代码风格一致
4. 对结构明显的文件（Router、data.ts），只做精确替换，禁止整文件重写

## Step 5: Lint 验收（仅 auto_lint=true 时）

编写完成后，运行 frontend-lint Skill 检查规范：

// turbo

```bash
cd .agent/skills/lint/scripts && python lint_frontend.py {修改的文件} --format summary
```

- **0 issues** → ✅ 编写完成
- **有 ERROR** → 必须修复后再完成
- **有 WARNING** → 报告给用户，建议修复

---

## MCP 工具速查

| MCP 服务             | 工具                 |  阶段  | 用途                           |
| -------------------- | -------------------- | :----: | ------------------------------ |
| `dushan-codegen-mcp` | `get_rules_for_file` | Step 2 | 获取文件类型的编码规范（必须） |
| `dushan-codegen-mcp` | `read_knowledge`     | Step 3 | 加载架构文档（可选）           |
| `dushan-codegen-mcp` | `search_knowledge`   | Step 3 | 搜索相关知识（可选）           |
