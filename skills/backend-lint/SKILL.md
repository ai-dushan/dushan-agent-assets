---
name: backend-lint
description: >
  【SKILLS】后端 Python/SQL 代码规范检查（dushan-admin-backend 工作区）。
  仅限 .py 和 .sql 文件。对后端代码审查、规范验证、提交前检查时触发。
  前端 .vue/.ts 文件请用 frontend-lint。
scope: backend
author: 渡山源码
project: dushan-admin-backend
---

# DuShan L0 Lint — 代码规范静态检查

基于 Python AST + 正则的零依赖、零 Token 消耗代码规范检查引擎。
支持 `.py` 和 `.sql` 文件。

## 何时使用

- 用户要求 **代码审查 / review / scan**
- 用户修改代码后需要 **验证规范**
- 作为 `/review`、`/scan` 工作流的 **第一步**
- 用户问 **"这个文件/模块有什么问题"**
- **CI/CD 流水线** 中的自动检查

## 何时不使用

- 用户仅在讨论设计方案或架构
- 用户要求生成新代码（生成后可用本 skill 验证）
- 前端 Vue/TypeScript 代码检查

## 规则清单（53 条 / 10 组）

### [global] 全局规则 — 14 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| G-2a | WARNING | 文件超过 500 行 |
| G-2b | WARNING | 方法超过 50 行 |
| G-3 | WARNING | 禁止相对导入 |
| G-4 | INFO | typing 旧式类型（Optional/List/Dict） |
| G-5 | WARNING | 禁止 dict[str, Any] |
| G-7 | WARNING | except Exception 缺少 as e |
| G-8 | WARNING | 文件缺少 docstring |
| G-14 | WARNING | 公开方法必须 async def |
| G-34 | WARNING | 类级别可变属性 |
| G-37 | WARNING | 非空 __init__.py |
| G-LOG | WARNING | logger 禁止 f-string |
| G-N1 | WARNING | 类名必须 PascalCase |
| G-N2 | WARNING | 方法名必须 snake_case |
| G-N3 | WARNING | 文件名必须 snake_case |

### [layer] 分层规则 — 5 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| C-2 | ERROR | Controller 禁止导入 Mapper |
| C-5 | WARNING | Controller 禁止 try-except |
| S-3 | ERROR | Service 禁止直接操作 DB |
| S-9 | ERROR | Service 禁止导入 Request/Response |
| S-15 | WARNING | Service 实现层禁止定义 logger |

### [model] 数据模型规则 — 2 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| DO-1 | ERROR | DO 类必须继承 BaseDO/TenantBaseDO |
| DO-5 | WARNING | __tablename__ 必须蛇形命名 |

### [security] 安全规则 — 5 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| SEC-1 | ERROR | 硬编码 API Key / 密码 / Token |
| SEC-2 | ERROR | f-string SQL 拼接（注入风险） |
| SEC-3 | ERROR | eval / exec / compile 调用 |
| SEC-4 | WARNING | 日志中泄露敏感变量 |
| SEC-5 | WARNING | os.system() 命令注入 |

### [arch] 架构规则 — 2 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| ARCH-1 | WARNING | 层级穿透（跳过中间层） |
| ARCH-2 | WARNING | 跨模块直接引用 Service |

### [api] API 协议规则 — 6 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| API-1 | ERROR | API Protocol 文件命名/位置 |
| API-2 | WARNING | API 方法签名重复 |
| API-3 | ERROR | DTO 必须继承 BaseVO |
| API-4 | WARNING | 集合参数类型规范 |
| API-5 | WARNING | API 方法缺少 docstring |
| API-6 | ERROR | API 禁止跨模块导入实现层 |

### [bo] BO 规则 — 3 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| BO-1 | WARNING | BO 文件必须在 bo/ 目录 |
| BO-2 | WARNING | BO 类名必须以 BO 结尾 |
| BO-3 | ERROR | BO 必须继承 BaseVO |

### [ctrl] 控制器规则 — 5 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| CTRL-1 | WARNING | Controller 必须返回 CommonResult |
| CTRL-2 | WARNING | Controller 方法需 @permission 装饰器 |
| CTRL-3 | WARNING | VO 必须在 vo/ 目录 |
| CTRL-4 | WARNING | Body 参数需 Depends 注入 |
| CTRL-5 | WARNING | Service 注入方式规范 |

### [enum] 枚举规则 — 2 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| ENUM-1 | ERROR | 枚举必须继承 IntEnum/StrEnum |
| ENUM-2 | WARNING | 枚举类名必须以 Enum 结尾 |

### [sql] SQL DDL/Seed 规则 — 9 条

| 规则 | 级别 | 检查内容 |
|------|------|----------|
| SQL-1 | WARNING | CREATE TABLE 缺少 id BIGINT NOT NULL 主键 |
| SQL-2 | WARNING | 租户隔离表缺少 tenant_id 或 idx_tenant_id |
| SQL-3 | WARNING | 缺少审计字段（creator/create_time/updater/update_time/deleted） |
| SQL-4 | WARNING | create_time 缺少 DEFAULT CURRENT_TIMESTAMP |
| SQL-5 | WARNING | update_time 缺少 ON UPDATE CURRENT_TIMESTAMP |
| SQL-6 | WARNING | deleted 不符合 TINYINT(1) NOT NULL DEFAULT 0 |
| SQL-7 | INFO | 字段缺少 COMMENT |
| SQL-8 | WARNING | 引擎/字符集不符合 InnoDB + utf8mb4 |
| SQL-9 | WARNING | 禁止 AUTO_INCREMENT |

## 工作流

### 1. 全量扫描

```bash
cd .agent/skills/lint/scripts
python dushan_lint.py "../../.." --format summary
```

### 2. 指定目录 / 文件

```bash
# Python 子模块
python dushan_lint.py ../../../module_system --format summary

# SQL 目录
python dushan_lint.py ../../../sql/mysql --category sql --format summary

# 指定文件
python dushan_lint.py ../../../module_ai/service/chat/chat_service_impl.py
```

### 3. 按规则分类扫描

```bash
# 只跑分层规则
python dushan_lint.py ../../../module_system --category layer

# 只跑安全规则
python dushan_lint.py ../../../module_system --category security

# 只跑 SQL 规则
python dushan_lint.py ../../../sql/mysql --category sql

# 可用分类：global | layer | model | security | arch | api | bo | ctrl | enum | sql
```

### 4. Git 增量扫描（只查变更文件）

```bash
python dushan_lint.py "../../.." --git-diff
```

### 5. 审查特定规则

```bash
# 只查 docstring 缺失
python dushan_lint.py "../../.." --rule G-8 --format markdown

# 只看 ERROR 级别
python dushan_lint.py "../../.." --severity error
```

## 输出格式

| 格式 | 用途 |
|------|------|
| `--format summary` | 一行概要（默认） |
| `--format stats` | 规则分布统计 |
| `--format json` | 程序化消费（CI/MCP） |
| `--format markdown` | 人类可读报告 |

## 脚本文件说明

| 文件 | 职责 |
|------|------|
| [_base.py](scripts/_base.py) | 公共基础：数据类、检查引擎、报告输出（支持 .py + .sql） |
| [lint_global.py](scripts/lint_global.py) | 14 条全局规则 |
| [lint_layer.py](scripts/lint_layer.py) | 5 条分层规则 |
| [lint_model.py](scripts/lint_model.py) | 2 条模型规则 |
| [lint_security.py](scripts/lint_security.py) | 5 条安全规则 |
| [lint_arch.py](scripts/lint_arch.py) | 2 条架构规则 |
| [lint_api.py](scripts/lint_api.py) | 6 条 API 协议规则 |
| [lint_bo.py](scripts/lint_bo.py) | 3 条 BO 规则 |
| [lint_ctrl.py](scripts/lint_ctrl.py) | 5 条控制器规则 |
| [lint_enum.py](scripts/lint_enum.py) | 2 条枚举规则 |
| [lint_sql.py](scripts/lint_sql.py) | 9 条 SQL DDL/Seed 规则 |
| [dushan_lint.py](scripts/dushan_lint.py) | 统一编排入口，组合全部 53 条规则 |

## 注意事项

- 所有脚本必须在 `scripts/` 目录下执行（`from _base import` 依赖同目录）
- 扫描排除：`__pycache__`, `.venv`, `.git`, `migrations`, `.agent`
- 支持文件类型：`.py`（AST + 正则）、`.sql`（正则）
- 性能基准：2400+ 文件 ≈ 5 秒，零网络请求
