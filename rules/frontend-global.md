---
trigger: always_on
scope: frontend
author: DuShan Team
---

# 前端全局编码原则

1. 必须 `<script setup lang="ts">`，禁止 Options API / defineComponent
2. 禁止 `<style>` / `<style scoped>` / `<style lang="scss">`，样式用 Tailwind + Element Plus CSS 变量
3. 禁止 Tailwind `dark:` 前缀，暗黑模式通过 Element Plus CSS 变量适配
4. ID 类型统一 `number`，包括 ref、getData、函数参数
5. 页面不直接用 `requestClient`，通过 `#/api/` 调用
6. 枚举选项用 `getDictOptions(DICT_TYPE.XXX)` 动态获取，禁止硬编码
7. 文件名 kebab-case，禁止非空断言 `!.`（改用 `?.` + `??`）
8. 禁止向后兼容代码、死代码、孤岛代码
9. 编写/修改代码前，调用 MCP `get_rules_for_file(file_path)` 获取该文件类型的详细规范
10. 编写/修改代码后，运行 frontend-lint Skill 检查规范
