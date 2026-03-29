---
description: 【规则】DevOps 编码规范 — module_devops 模块化架构
trigger: always_on
scope: devops
author: 渡山源码
project: dushan-devops
---

# DevOps 工作区编码规范

> **核心职责**：Git 沙箱隔离 → MCP 注入 → Agent 子进程调度 → L0 Lint 验收 → 断路器重试 → 人工审批
> **技术栈**：Python 3.12+ · FastAPI · SQLAlchemy (SQLite) · Jinja2 SSR · 零框架 JS SPA
> **入口**：`app.py` → `module_devops.app:app` → `0.0.0.0:8002`

## 1. 模块化分层架构

所有业务代码必须在 `module_devops/` 下，严格分层：

```
module_devops/
├── controller/     ← HTTP 路由层（薄壳委派 Service）
├── service/        ← 业务逻辑层（核心算法）
├── dal/            ← 数据访问层（models.py + database.py）
├── core/           ← 跨层基础设施（pipeline / gitops / i18n / settings）
├── enums/          ← 枚举 + 全局常量
├── integration/    ← Agent Runner / MCP 注入器 / Lint 集成
└── resources/      ← 静态资源 / 页面数据
```

- 严禁引用 `src/` 或 `static/` 目录（已废弃）
- 所有路径推导基于 `core/settings.py` 中的 `DEVOPS_ROOT` 唯一锚点
- 前端模板在 `templates/`，静态资源在 `module_devops/resources/static/`
- AI 资产统一在 `data/` 下管理：`agent-assets-local/`（自定义）+ `agent-assets-repo/`（远程仓库）

## 2. Python 编码原则

1. 一个文件一个核心类，单文件 ≤ 500 行，单方法 ≤ 100 行
2. 完整路径导入（`from module_devops.core.settings import ...`），禁止相对导入
3. 类型注解用内置类型，`X | None` 替代 Optional，禁止 `dict[str, Any]` 作参数
4. 禁止硬编码字符串，使用 `enums/enums.py` 枚举 + `enums/constants.py` 常量
5. 禁止 `except Exception: pass`，异常必须捕获并合理处理
6. 文件头 docstring 必须有（职责/依赖/被调用，≤6 行）
7. 禁止向后兼容代码、防御性获取、死代码、孤岛代码
8. 所有配置通过 `DevOpsSettings`（pydantic-settings）注入，禁止硬编码 API Key

## 3. Agent Runner 插拔规范

- 所有 Runner 继承 `integration/base_runner.py:BaseAgentRunner`
- 新增 Runner 只需创建 `integration/runners/runner_xxx.py` + 在 `registry.py` 注册
- Runner 必须实现 ANSI 过滤 + TTY 死锁拦截

## 4. MCP 注入器策略

- 所有注入器继承 `integration/mcp_injector.py:McpInjectorStrategy`
- 不支持 MCP 的 Agent 使用 `NoopMcpInjector`
- 注入器注册表：`MCP_INJECTOR_REGISTRY`

## 5. 状态机纪律

- 任务状态只读写 SQLite，禁止 JSON 文件存状态
- 状态枚举：`QUEUED → RUNNING → LINT_FAILED → NEEDS_HUMAN → SUCCESS / ROLLBACK`
- 沙箱失败必须调用 `gitops.rollback_sandbox()` 自动销毁

## 6. 前端约束

- Jinja2 模板放 `templates/`，后缀 `.html.j2`
- 静态资源放 `module_devops/resources/static/`，通过 `/static/` URL 访问
- JS 零框架，原生 DOM 操作
- CSS 使用 CSS 变量主题系统（`base.css` 中定义 `:root` / `[data-theme]`）
- SVG 图标由 `core/icon_registry.py` 服务端渲染
- 国际化由 `core/i18n.py` + `locale/*.json` 提供
