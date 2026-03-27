---
description: 【工作流】后端开发辅助 — 加载规范 → 编写代码 → Lint 验收
scope: backend
author: DuShan Team
---

# /backend-dev — 后端开发辅助

> 用法：`/dev {文件或目录或描述}` — 按规范编写/修改后端代码。

```yaml
# ── 开发配置 ──
auto_lint: true               # 编写完成后自动运行 backend-lint Skill 验收
auto_template: true            # 新文件时自动渲染 J2 模板骨架
architecture_docs: false       # 是否加载架构文档（复杂改动时手动开启）
```

---

## Step 1: 识别任务和文件类型

分析用户的开发目标：

- **新建文件** → 需要识别文件类型 + 渲染模板骨架
- **修改文件** → 需要加载该文件类型的编码规范

识别文件类型映射（按路径/命名自动判断）：

| 文件类型 | 识别特征 | MCP 规范 | J2 模板 |
|---------|---------|---------|---------|
| Controller | `*_controller.py` / `controller/` | controller.md | controller.py.j2 |
| Service 接口 | `*_service.py` / `service/` (Protocol) | service.md | service.py.j2 |
| Service 实现 | `*_service_impl.py` | service.md | service_impl.py.j2 |
| Mapper | `*_mapper.py` / `dal/mysql/` | mapper.md | mapper.py.j2 |
| DO | `*_do.py` / `dal/dataobject/` | do.md | do.py.j2 |
| VO | `*_vo.py` / `vo/` | vo_dto.md | vo.py.j2 |
| Enum | `*_enum.py` / `enums/` | enums.md | enum.py.j2 |
| API 接口 | `*_api.py` / `api/` | api.md | api.py.j2 |
| API 实现 | `*_api_impl.py` | api.md | api_impl.py.j2 |
| SPI | `*_spi_adapter.py` / `spi/` | spi.md | spi_provider_adapter.py.j2 |
| Redis DAO | `*_redis_dao.py` | dao.md | redis_dao.py.j2 |
| Job | `*_job.py` / `job/` | job.md | job.py.j2 |
| Router | `router.py` | router.md | router.py.j2 |
| Error Code | `error_code_constants.py` | error_code.md | error_code.py.j2 |
| BO | `bo/` | bo.md | — |
| Config | `*_config_builder.py` | config.md | — |
| Framework | `framework/starter_*/` | framework.md | — |

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
dushan-codegen-mcp → read_knowledge("architecture/framework.md")   — Framework 能力索引
dushan-codegen-mcp → search_knowledge(相关关键词)                   — 搜索相关知识
```

## Step 4: 新文件 → 渲染模板骨架（仅 auto_template=true 且新建文件时）

根据 Step 1 识别的文件类型，渲染 J2 标准模板：

```
dushan-codegen-mcp → render_template(模板名, { module, entity, ... })
```

基于渲染出的骨架编写代码，确保结构与标准一致。

## Step 5: 编写/修改代码

根据 Step 2 加载的规范 + `.agents/rules/` 中的全局原则，编写代码。

编写要求：

1. 严格遵守 MCP 返回的文件类型规范
2. 严格遵守 `.agents/rules/global.md` 的全局编码原则
3. 严格遵守 `.agents/rules/architecture.md` 的架构决策
4. 新文件基于 Step 4 的模板骨架编写
5. 修改文件保持现有代码风格一致

## Step 6: Lint 验收（仅 auto_lint=true 时）

编写完成后，运行 backend-lint Skill 检查规范：

// turbo
```bash
cd .agent/skills/lint/scripts && python dushan_lint.py {修改的文件} --format summary
```

- **0 issues** → ✅ 编写完成
- **有 ERROR** → 必须修复后再完成
- **有 WARNING** → 报告给用户，建议修复

---

## MCP 工具速查

| MCP 服务 | 工具 | 阶段 | 用途 |
|---------|------|:----:|------|
| `dushan-codegen-mcp` | `get_rules_for_file` | Step 2 | 获取文件类型的编码规范（必须） |
| `dushan-codegen-mcp` | `render_template` | Step 4 | 渲染 J2 标准模板骨架 |
| `dushan-codegen-mcp` | `read_knowledge` | Step 3 | 加载架构文档（可选） |
| `dushan-codegen-mcp` | `search_knowledge` | Step 3 | 搜索相关知识（可选） |
