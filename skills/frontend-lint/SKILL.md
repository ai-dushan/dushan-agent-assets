---
name: frontend-lint
description: >
  【SKILLS】前端 Vue/TypeScript 代码规范检查（dushan-admin-frontend 工作区）。 仅限 .vue、.ts、.tsx 文件。对前端代码审查、规范验证、提交前检查时触发。 后端 .py/.sql 文件请用 backend-lint。
scope: frontend
author: 渡山源码
project: dushan-admin-frontend
---

# DuShan Frontend L0 Lint — 前端代码规范静态检查

基于正则的零依赖、零 Token 消耗前端代码规范检查引擎。支持 `.vue`、`.ts`、`.tsx` 文件。

## 何时使用

- 用户要求 **前端代码审查 / review / scan**
- 用户修改前端代码后需要 **验证规范**
- 作为 `/review-frontend` 工作流的 **第一步**
- 用户问 **"这个前端文件有什么问题"**

## 何时不使用

- 后端 Python 代码检查（使用 `dushan-lint` 后端 Skill）
- 用户仅在讨论设计方案或架构
- 用户要求生成新代码（生成后可用本 skill 验证）

## 规则清单（9 条）

| 规则 | 级别    | 检查内容                                                |
| ---- | ------- | ------------------------------------------------------- |
| FE-1 | ERROR   | .vue 文件禁止 `<style` 块                               |
| FE-2 | WARNING | 禁止 Tailwind `dark:` 前缀                              |
| FE-3 | WARNING | .vue 必须 `<script setup lang="ts">`                    |
| FE-4 | ERROR   | 禁止 Options API（`export default {`）                  |
| FE-5 | WARNING | API 文件（`api/*/index.ts`）必须使用 `export namespace` |
| FE-6 | WARNING | 禁止硬编码中文按钮文案（应使用 `$t()`）                 |
| FE-7 | WARNING | views/ 中禁止直接使用 `requestClient`                   |
| FE-8 | WARNING | 文件名必须 kebab-case                                   |
| FE-9 | WARNING | 禁止非空断言 `!.`（改用 `?.` + `??`）                   |

## 工作流

### 1. 全量扫描

```bash
cd .agent/skills/lint/scripts
python lint_frontend.py "../../../../apps/web-ele/src" --format summary
```

### 2. 指定目录 / 文件

```bash
# 扫描 views 目录
python lint_frontend.py ../../../../apps/web-ele/src/views --format summary

# 扫描 API 目录
python lint_frontend.py ../../../../apps/web-ele/src/api --format summary

# 扫描单个文件
python lint_frontend.py ../../../../apps/web-ele/src/views/system/user/index.vue
```

### 3. 审查特定规则

```bash
# 只查 style 块
python lint_frontend.py ../../../../apps/web-ele/src --rule FE-1

# 只看 ERROR 级别
python lint_frontend.py ../../../../apps/web-ele/src --severity error
```

## 输出格式

| 格式                | 用途                 |
| ------------------- | -------------------- |
| `--format summary`  | 一行概要（默认）     |
| `--format stats`    | 规则分布统计         |
| `--format json`     | 程序化消费（CI/MCP） |
| `--format markdown` | 人类可读报告         |

## 脚本文件说明

| 文件 | 职责 |
| --- | --- |
| [\_base.py](scripts/_base.py) | 公共基础：数据类、文件扫描、报告输出 |
| [lint_frontend.py](scripts/lint_frontend.py) | 9 条前端规则，可独立运行 |

## 注意事项

- 所有脚本必须在 `scripts/` 目录下执行
- 扫描排除：`node_modules`, `dist`, `.git`, `.vscode`, `.changeset`, `.agent`
- 支持文件类型：`.vue` / `.ts` / `.tsx`
- 性能：正则检查，速度极快
