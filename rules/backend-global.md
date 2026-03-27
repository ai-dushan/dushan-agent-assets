---
trigger: always_on
scope: backend
author: DuShan Team
---

# 后端全局编码原则

1. 面向对象优先，一个文件一个核心类，单文件 ≤ 500 行，单方法 ≤ 100 行
2. 完整路径导入，禁止相对导入，禁止创建 `__init__.py`
3. 类型注解用内置类型，`X | None` 替代 Optional，禁止 `dict[str, Any]` 作参数
4. 禁止硬编码字符串/枚举值，使用枚举、常量、配置（settings/builder）
5. 异常用 `ServiceException` + `ErrorCodeConstants`，禁止 `except Exception: pass`
6. 所有方法 `async def`，禁止 async 中阻塞调用
7. 文件头 docstring 必须有（职责/依赖/被调用，≤6 行）
8. 禁止向后兼容代码、防御性获取、死代码、孤岛代码
9. 禁止硬编码默认值，配置通过 ConfigBuilder 唯一入口获取
10. 编写/修改代码前，调用 MCP `get_rules_for_file(file_path)` 获取该文件类型的详细规范
11. 编写/修改代码后，运行 backend-lint Skill 检查规范
