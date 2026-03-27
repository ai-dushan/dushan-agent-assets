# DuShan Agent Assets

渡山 AI Agent 资产仓库 — 开源的 Skills / Workflows / Rules 集合。

## 目录结构

```
dushan-agent-assets/
├── rules/          # 编码规则（.md）
├── skills/         # 技能包（目录，含 SKILL.md）
├── workflows/      # 工作流（.md）
└── README.md
```

## 元数据约定

### Rules / Workflows (.md 文件)

```yaml
---
name: backend-architecture
description: 后端架构决策
trigger: always_on
scope: backend          # universal / frontend / backend
author: DuShan Team
---
```

### Skills (SKILL.md)

```yaml
---
name: backend-lint
description: 后端代码规范检查
scope: backend          # universal / frontend / backend
author: DuShan Team
---
```

## 贡献指南

1. Fork 本仓库
2. 在对应目录下创建你的资产文件
3. 确保 YAML frontmatter 包含必要的元数据
4. 提交 Pull Request

## 许可证

MIT License
