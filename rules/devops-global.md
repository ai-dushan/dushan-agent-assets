---
description: 【规则】DevOps 编码入口 — 强制从 codegen-mcp 获取规则
trigger: always_on
scope: devops
author: 渡山源码
project: dushan-devops
---

# DevOps 开发强制规则

> ⚠️ 所有 DevOps 编码规范由 `dushan-codegen-mcp` 知识库统一管理。

**核心指令**：

1. 编写任何 DevOps 代码之前，必须通过 CLI 获取最新规则：

```bash
cd dushan-mcp/dushan-codegen-mcp
python -m cli rules <file_path> --mode codegen --format json
```

2. 编写完成后，必须运行 Lint 验收：

```bash
cd .agent/skills/forge-lint/scripts
python forge_lint.py <file_path> --format summary
```

3. 架构约束参考 `module_demo/` 活代码结构。

> 禁止在此文件内硬编码具体规则条目。规则的唯一源头是 codegen-mcp 知识库。
