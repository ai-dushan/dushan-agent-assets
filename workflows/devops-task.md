---
description: 【工作流】DevOps 任务发射 — 选工作区 → 选 Agent → 发射 Pipeline → 监控
---

# /devops-task — DevOps 任务发射

> 用法：`/devops-task {目标描述}` — 通过 DevOps Pipeline 发射 AI 编码任务。

```yaml
# ── 发射配置 ──
default_agent: codex # 默认 Agent（codex / claude / gemini / qwen-code / dummy）
auto_monitor: true # 发射后自动监控任务状态
```

---

## Step 0: 前置检查

确认 DevOps 服务正在运行：

// turbo

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/api/tasks
```

- **200** → 服务正常，继续
- **非 200** → 提示用户先启动：`cd dushan-devops && .venv\Scripts\python app.py`

## Step 1: 选择工作区

获取已注册的工作区列表：

// turbo

```bash
curl -s http://localhost:8002/api/workspaces
```

返回：`[{id, label, path, has_rules, has_workflows, has_skills}, ...]`

用户需要指定目标工作区。若用户未指定，展示列表让用户选择。

## Step 2: 选择 Agent

可用 Agent 列表：

| Agent     | CLI         | 认证方式   | 备注                         |
| --------- | ----------- | ---------- | ---------------------------- |
| codex     | `codex`     | OAuth 登录 | 需先 `codex login`           |
| claude    | `claude`    | OAuth 登录 | 需先 `claude login`          |
| gemini    | `gemini`    | API Key    | 需配置 DUSHAN_GEMINI_API_KEY |
| qwen-code | `qwen-code` | API Key    | 需配置对应环境变量           |
| dummy     | 测试打桩    | 无需       | 仅用于验证 Pipeline 流程     |

> **踩坑提醒**：Codex 使用 OAuth 而非 API Key，无需在 `.env` 配置 OPENAI_API_KEY。

## Step 3: 构造目标描述

将用户的需求转化为清晰的 `objective` 文本。要求：

1. 明确具体的交付物（文件路径 + 内容要求）
2. 不超过 500 字
3. 避免使用括号 `()` 等 PowerShell 特殊字符

## Step 4: 发射任务

将 JSON 写入临时文件后，通过 Python 脚本发射（避免 PowerShell 转义问题）：

```python
import httpx

resp = httpx.post("http://localhost:8002/api/tasks", json={
    "objective": "<Step 3 的目标描述>",
    "agent": "<Step 2 选择的 Agent>",
    "workspace": r"<Step 1 选择的工作区路径>",
})
print(resp.json())
```

成功返回：`{"success": true, "task_id": "task-xxx", "message": "任务已发射"}`

> **踩坑提醒**：API 参数名是 `workspace`（不是 `workspace_path`），传入项目绝对路径。

> **踩坑提醒**：不要用 PowerShell 的 curl + JSON 字符串，`()` 等字符会导致 ParserError。用 Python 脚本发射最安全。

> **踩坑提醒**：DevOps venv 已有 `httpx`（FastAPI 依赖），直接用 `httpx.post()` 发射最简洁。

## Step 5: 监控任务状态（仅 auto_monitor=true 时）

发射后轮询任务状态：

// turbo

```bash
curl -s http://localhost:8002/api/tasks/<task_id>
```

状态流转：

```
QUEUED → RUNNING → NEEDS_HUMAN（成功，等审批）
                 → LINT_FAILED → 自动重试（最多 2 轮）
                 → FAILED（Agent 异常）
```

- **NEEDS_HUMAN** → 提示用户打开 WebUI 审批或回滚
- **RUNNING** → 等待，每 10 秒轮询
- **FAILED** → 报告错误日志

---

## Pipeline 全链路说明

```
发射 → 创建 Git Worktree 沙箱 → MCP 注入 → Prompt 拼装 → Agent 执行
                                                              ↓
                  人工审批 ← NEEDS_HUMAN ←── Lint 通过
                      │                       ↓ 失败
                      │             错误注入 Prompt → 重试
                      │                       ↓ 超限
                      │             断路器触发 → 人工介入
                      ↓
            Approve → Merge    /    Rollback → 销毁
```

## 常见错误速查

| 错误                             | 原因                    | 解决                          |
| -------------------------------- | ----------------------- | ----------------------------- |
| `402 Payment Required`           | Agent OAuth 订阅过期    | 重新登录或更换 Agent          |
| `ModuleNotFoundError: requests`  | venv 无 requests        | 用 `httpx`（已有）或 `urllib` |
| PowerShell `ParserError` on `()` | JSON 被 PS 解析为表达式 | 用 Python 脚本发射            |
