---
description: 【工作流】后端代码审查 — L0 Lint → L1 MCP 分析 → L2 深度审查 → 评分报告
scope: backend
author: DuShan Team
---

# /review — 后端代码审查

> 用法：`/review {文件或目录}` — 三层递进审查 + 评分报告。

// turbo-all

```yaml
# ── 审查配置 ──
review_depth: full              # full: L0+L1+L2 / quick: L0+L1 only
fix_after_review: ask           # ask: 报告后询问 / never: 只报告不修
architecture_docs: false        # 是否加载架构文档（复杂改动时手动开启）

# ── 评分维度 ──
scoring:
  architecture: { weight: 25, label: "架构合规" }
  template: { weight: 20, label: "模板合规" }
  type_safety: { weight: 15, label: "类型安全" }
  code_quality: { weight: 15, label: "代码质量" }
  security: { weight: 15, label: "安全性" }
  documentation: { weight: 10, label: "文档规范" }
```
