---
description: 【规则】后端全局编码入口 — 强制从 codegen-mcp 获取规则
trigger: always_on
scope: backend
author: 渡山源码
project: dushan-admin-backend
---

# 后端开发强制规则

> ⚠️ 所有后端编码规范由 `dushan-codegen-mcp` 知识库统一管理。

**核心指令**：

1. 编写任何后端代码之前，必须通过 CLI 获取最新规则：

```bash
cd dushan-mcp/dushan-codegen-mcp
python -m cli rules <file_path> --mode codegen --format json
```

2. 必须加载并遵循 `.agent/skills/backend-dev/SKILL.md` 的 Step 0 Preflight 门禁。

3. 编写完成后，必须运行 Lint 验收：

```bash
cd .agent/skills/lint/scripts
python dushan_lint.py <file_path> --format summary
```

> 禁止在此文件内硬编码具体规则条目。规则的唯一源头是 codegen-mcp 知识库。
