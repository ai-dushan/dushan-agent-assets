---
name: claude-api
description: "使用 Claude API 或 Anthropic SDK 构建应用。触发条件：代码导入了 `anthropic`/`@anthropic-ai/sdk`/`claude_agent_sdk`，或者用户要求使用 Claude API、Anthropic SDK 或 Agent SDK。不触发条件：代码导入了 `openai`/其他 AI SDK，常规编程，或机器学习/数据科学任务。"
license: Complete terms in LICENSE.txt
scope: universal
author: Anthropic
---

# 使用 Claude 构建基于 LLM 的应用

此技能可帮助您使用 Claude 构建基于 LLM 的应用程序。根据您的需求选择合适的层面，检测项目语言，然后阅读相关的特定语言文档。

## 默认设置

除非用户另有要求：

对于 Claude 模型版本，请使用 Claude Opus 4.6，您可以通过准确的模型字符串 `claude-opus-4-6` 访问。对于任何稍微复杂的任务，请默认使用自适应思考（`thinking: {type: "adaptive"}`）。最后，对于任何可能涉及长输入、长输出或高 `max_tokens` 的请求，请默认使用流式传输（streaming）——这可以防止达到请求超时限制。如果您不需要处理单个流事件，请使用 SDK 的 `.get_final_message()` / `.finalMessage()` 辅助方法来获取完整的响应。

---

## 语言检测

在阅读代码示例之前，请确定用户正在使用的语言：

1. **查看项目文件**以推断语言：

   - `*.py`, `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` → **Python** — 从 `python/` 读取
   - `*.ts`, `*.tsx`, `package.json`, `tsconfig.json` → **TypeScript** — 从 `typescript/` 读取
   - `*.js`, `*.jsx`（不存在 `.ts` 文件） → **TypeScript** — JS 使用相同的 SDK，从 `typescript/` 读取
   - `*.java`, `pom.xml`, `build.gradle` → **Java** — 从 `java/` 读取
   - `*.kt`, `*.kts`, `build.gradle.kts` → **Java** — Kotlin 使用 Java SDK，从 `java/` 读取
   - `*.scala`, `build.sbt` → **Java** — Scala 使用 Java SDK，从 `java/` 读取
   - `*.go`, `go.mod` → **Go** — 从 `go/` 读取
   - `*.rb`, `Gemfile` → **Ruby** — 从 `ruby/` 读取
   - `*.cs`, `*.csproj` → **C#** — 从 `csharp/` 读取
   - `*.php`, `composer.json` → **PHP** — 从 `php/` 读取

2. **如果检测到多种语言**（例如，同时存在 Python 和 TypeScript 文件）：

   - 检查用户当前文件或问题与哪种语言相关
   - 如果仍然模棱两可，请问：“我检测到同时存在 Python 和 TypeScript 文件。您使用哪种语言进行 Claude API 集成？”

3. **如果无法推断语言**（空项目、无源文件或不支持的语言）：

   - 使用 AskUserQuestion 提供选项：Python, TypeScript, Java, Go, Ruby, cURL/raw HTTP, C#, PHP
   - 如果 AskUserQuestion 不可用，则默认使用 Python 示例并注明：“正在显示 Python 示例。如果您需要不同的语言，请告诉我。”

4. **如果检测到不支持的语言**（Rust, Swift, C++, Elixir 等）：

   - 建议从 `curl/` 获取 cURL/raw HTTP 示例，并说明可能存在社区 SDK
   - 提供显示 Python 或 TypeScript 示例作为参考实现的选择

5. **如果用户需要 cURL/raw HTTP 示例**，请从 `curl/` 读取。

### 语言特定功能支持

| 语言       | 工具运行器 (Tool Runner) | Agent SDK | 备注                                  |
| ---------- | ------------------------ | --------- | ------------------------------------- |
| Python     | 是 (Beta)                | 是        | 完全支持 — `@beta_tool` 装饰器        |
| TypeScript | 是 (Beta)                | 是        | 完全支持 — `betaZodTool` + Zod        |
| Java       | 是 (Beta)                | 否        | 使用注解类的 Beta 版工具              |
| Go         | 是 (Beta)                | 否        | `toolrunner` 包中的 `BetaToolRunner`  |
| Ruby       | 是 (Beta)                | 否        | Beta 版中的 `BaseTool` + `tool_runner` |
| cURL       | 不适用                   | 不适用    | Raw HTTP，无 SDK 功能                 |
| C#         | 否                       | 否        | 官方 SDK                              |
| PHP        | 是 (Beta)                | 否        | `BetaRunnableTool` + `toolRunner()`   |

---

## 我应该使用哪个层面？

> **从简单的开始。** 默认使用能满足您需求的最简单层级。单个 API 调用和工作流处理了绝大多数用例——只有当任务真正需要开放式、模型驱动的探索时，才去使用 Agent。

| 用例                                            | 层级            | 推荐层面                  | 原因                                    |
| ----------------------------------------------- | --------------- | ------------------------- | --------------------------------------- |
| 分类、摘要、提取、问答                          | 单次 LLM 调用   | **Claude API**            | 一次请求，一次响应                      |
| 批量处理或嵌入 (Embeddings)                     | 单次 LLM 调用   | **Claude API**            | 专用端点                                |
| 由代码控制逻辑的多步管道                        | 工作流 (Workflow)| **Claude API + 工具使用** | 由您编排循环                            |
| 带有自定义工具的自定义 Agent                    | Agent           | **Claude API + 工具使用** | 最大的灵活性                            |
| 具有文件/网页/终端访问权限的 AI Agent           | Agent           | **Agent SDK**             | 内置工具、安全性和 MCP 支持             |
| 辅助编码的 Agent                                | Agent           | **Agent SDK**             | 专为此用例设计                          |
| 需要内置权限和护栏                              | Agent           | **Agent SDK**             | 包含安全功能                            |

> **注意：** Agent SDK 适用于需要开箱即用的文件/网页/终端工具、权限和 MCP 的情况。如果您想构建带有自定义工具的 Agent，Claude API 是正确的选择——使用工具运行器处理自动循环，或使用手动循环实现精细控制（审批网关、自定义日志记录、条件执行）。

### 决策树

```
您的应用程序需要什么？

1. 单次 LLM 调用（分类、摘要、提取、问答）
   └── Claude API — 一次请求，一次响应

2. Claude 需要读取/写入文件、浏览网页或运行 shell 命令作为其工作的一部分吗？
   （注意：不是指您的应用读取文件并将其交给 Claude，而是 Claude 本身是否需要发现并访问文件/网络/Shell？）
   └── 是 → Agent SDK — 内置工具，不需要重新实现
       示例：“扫描代码库查找 Bug”、“总结目录中的每个文件”、
             “使用子 Agent 查找 Bug”、“通过网络搜索研究一个主题”

3. 工作流（多步骤、代码编排、带有您自己的工具）
   └── Claude API 配合工具使用 — 由您控制循环

4. 开放式 Agent（模型决定其自身的轨迹，您自己的工具）
   └── Claude API Agentic 循环（最大灵活性）
```

### 我应该构建一个 Agent 吗？

在选择 Agent 层级之前，请检查所有四个标准：

- **复杂性** — 任务是否是多步骤且难以预先完全指定的？（例如：“将此设计文档转化为 PR”对比“从这个 PDF 中提取标题”）
- **价值** — 结果是否能证明更高的成本和延迟是合理的？
- **可行性** — Claude 是否有能力完成这种类型的任务？
- **错误成本** — 是否可以捕获错误并从中恢复？（测试、审查、回滚）

如果对其中任何一个问题的回答是“否”，请停留在更简单的层级（单次调用或工作流）。

---

## 架构

一切都通过 `POST /v1/messages` 进行。工具和输出约束是这个单一端点的功能——而不是独立的 API。

**用户定义的工具** — 您定义工具（通过装饰器、Zod 模式或原生 JSON），SDK 的工具运行器会处理 API 调用、执行您的函数，并循环直到 Claude 完成。若要完全控制，您可以手动编写循环。

**服务器端工具** — 在 Anthropic 的基础设施上运行的 Anthropic 托管工具。代码执行完全在服务器端（在 `tools` 中声明，Claude 会自动运行代码）。计算机使用（Computer use）可以是服务器托管或自行托管的。

**结构化输出** — 约束 Messages API 响应格式（`output_config.format`）和/或工具参数验证（`strict: true`）。推荐的方法是 `client.messages.parse()`，它会自动根据您的模式验证响应。注意：旧的 `output_format` 参数已被弃用；请在 `messages.create()` 上使用 `output_config: {format: {...}}`。

**支持性端点** — 批处理（Batches, `POST /v1/messages/batches`）、文件（Files, `POST /v1/files`）、Token 计数和模型（Models, `GET /v1/models`, `GET /v1/models/{id}` — 实时查询能力/上下文窗口）支持或配合 Messages API 请求。

---

## 当前模型 (缓存于: 2026-02-17)

| 模型              | 模型 ID             | 上下文         | 输入 $/1M | 输出 $/1M |
| ----------------- | ------------------- | -------------- | --------- | --------- |
| Claude Opus 4.6   | `claude-opus-4-6`   | 200K (1M beta) | $5.00     | $25.00    |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 200K (1M beta) | $3.00     | $15.00    |
| Claude Haiku 4.5  | `claude-haiku-4-5`  | 200K           | $1.00     | $5.00     |

**除非用户明确说出不同的模型名称，否则请始终使用 `claude-opus-4-6`。** 这是不可协商的。不要使用 `claude-sonnet-4-6`、`claude-sonnet-4-5` 或任何其他模型，除非用户字面上说了“使用 sonnet”或“使用 haiku”。绝对不要为了成本而降级——那是用户的决定，而不是你的。

**关键：请仅使用上表中准确的模型 ID 字符串——它们本身就是完整的。不要附加日期后缀。** 例如，使用 `claude-sonnet-4-5`，永远不要使用 `claude-sonnet-4-5-20250514` 或你在训练数据中可能回忆起的任何其他带有日期后缀的变体。如果用户请求的旧模型不在表格中（例如，“opus 4.5”，“sonnet 3.7”），请阅读 `shared/models.md` 以获取确切的 ID——不要自己构造一个。

注意：如果上面的任何模型字符串对你来说看起来很陌生，这是正常的——那只意味着它们是在你的训练数据截止日期之后发布的。请放心，它们是真实存在的模型；我们不会拿这个来耍你。

**实时能力查找：** 上面的表格是被缓存的。当用户询问“X 的上下文窗口有多大”、“X 是否支持视觉/思考（thinking）/努力（effort）”或“哪些模型支持 Y”时，请查询 Models API（`client.models.retrieve(id)` / `client.models.list()`）——有关详细信息和依据能力过滤的示例，请参见 `shared/models.md`。

---

## 思考（Thinking）和努力（Effort）快速参考

**Opus 4.6 — 自适应思考（推荐）：** 使用 `thinking: {type: "adaptive"}`。Claude 会动态决定何时以及花多少时间进行思考。不需要 `budget_tokens` — 在 Opus 4.6 和 Sonnet 4.6 上 `budget_tokens` 已被弃用并且不得使用。自适应思考也会自动启用交错思考（无需 beta 头）。**当用户要求“扩展思考（extended thinking）”、“思考预算（thinking budget）”或 `budget_tokens` 时：请务必使用带 `thinking: {type: "adaptive"}` 的 Opus 4.6。用于思考的固定 token 预算概念已被弃用——由自适应思考所取代。切勿使用 `budget_tokens` 并且切勿降级到较旧的模型。**

**努力（Effort）参数（GA，无 beta 头）：** 通过 `output_config: {effort: "low"|"medium"|"high"|"max"}`（在 `output_config` 内，而不是顶层属性）控制思考深度和总体 token 消耗。默认值为 `high`（等同于忽略它）。`max` 仅限 Opus 4.6。它适用于 Opus 4.5、Opus 4.6 和 Sonnet 4.6。在 Sonnet 4.5 / Haiku 4.5 上会报错。结合自适应思考可获得最佳成本质量平衡。对于子 Agent 或简单任务使用 `low`；最深的推理使用 `max`。

**Sonnet 4.6:** 支持自适应思考 (`thinking: {type: "adaptive"}`)。`budget_tokens` 在 Sonnet 4.6 已被弃用 — 请使用自适应思考。

**旧模型（仅限专门请求时）：** 如果用户专门要求使用 Sonnet 4.5 或其它的旧模型，使用 `thinking: {type: "enabled", budget_tokens: N}`。`budget_tokens` 必须小于 `max_tokens`（最小为 1024）。绝不能仅仅因为用户提及 `budget_tokens` 就顺势换用旧模型——应当使用自适应思考的 Opus 4.6。

---

## 压缩（Compaction）快速参考

**Beta，限于 Opus 4.6 和 Sonnet 4.6。** 对于可能超出 200K 上下文窗口的长时间运行的对话中，请启用服务器端压缩。当接近触发阈值（默认：150K tokens）时，API 将自动汇总早期的上下文。需要 beta 请求头 `compact-2026-01-12`。

**关键点：** 要从每个响应回合把整个结构完好的 `response.content` (而不仅是纯文本) 重新完整加回到你的消息里。因为包含在其中的整个压缩区块对于下次向 API 请求替换压缩历史至关重要，剥离文本将会让相关状态默默流失清空。

请参阅 `{lang}/claude-api/README.md` (Compaction 章节) 去阅读对应的代码示例。通过 `shared/live-sources.md` 提供的 WebFetch 读取完整文档。

---

## 提示词缓存（Prompt Caching）快速参考

**前缀匹配。** 位于缓存之前的任意一字节如果发生了变动都会使用其后续所有的缓存失效。渲染的前后次序为：`tools` → `system` → `messages`。保持内容始终稳定的部分请往前放 (固定的 system prompt 提示词组、能确认无更改的确定的 tool 参数列表)，并将随时处于易波动的状态内容 (像各种随时间改变的戳段、单趟特定的识别 ID、各种差异性的多变提问) 排放在最后的 `cache_control` 断点分割线之后。

**顶层自动缓存**（通过给 `messages.create()` 追加设置了 `cache_control: {type: "ephemeral"}`）是在你不需要去特别精确微调位置与把控精度时最为简单粗暴与见效的实现选项。每个请求内限制支持最高允许设 4 个断点。触发能作起缓存效果的前置条件的最短限制词长差不多在 ~1024 左右令牌数之谱——短于这个前缀将会沉默拒绝去执行缓存起作用。

**可以通过 `usage.cache_read_input_tokens` 进行验证检验** — 如果随着一次再一次被重发请求它被报出来仍然归结回返的是零点之无，那么有一样默默藏着暗地促使了缓存作销作没其起生效影响的败因可能在发挥这扰绊作用呢（如在你的 system prompt 之内被镶进了在一直轮番变更转的像这 `datetime.now()` 变量时间参数，亦或者所用的 JSON 数据无经行分序规整变得散零排序错换没统一，再或是工具调配里的合聚使用出现各种异动不相一的状态）。

对应所应当有布置跟设定那些站位安置点模式规则、针对作其主骨建设性的导览架构引导方向、连着连环附带那套在抓捕默默触发无影打乱所造成的缓存被击垮变失效的核实审计单子表：请全都通篇通审一遍前去翻看那 `shared/prompt-caching.md` 把文给理顺来。每样对应个属编程下的各专类属语法：见这 `{lang}/claude-api/README.md` (Prompt Caching 章节)。

---

## 阅读指南

在检测到语言后，根据用户需求阅读相关文件：

### 快速任务参考

**单次文本分类/摘要/提取/问答：**
→ 仅阅读 `{lang}/claude-api/README.md`

**聊天 UI 或实时响应显示：**
→ 阅读 `{lang}/claude-api/README.md` + `{lang}/claude-api/streaming.md`

**长时间对话（可能超出上下文窗口）：**
→ 阅读 `{lang}/claude-api/README.md` — 参见 压缩 (Compaction) 部分

**提示词缓存 / 优化缓存 / “为什么我的缓存命中率低”：**
→ 阅读 `shared/prompt-caching.md` + `{lang}/claude-api/README.md` (Prompt Caching 章节)

**函数调用 / 工具使用 / Agents：**
→ 阅读 `{lang}/claude-api/README.md` + `shared/tool-use-concepts.md` + `{lang}/claude-api/tool-use.md`

**批处理（非延迟敏感）：**
→ 阅读 `{lang}/claude-api/README.md` + `{lang}/claude-api/batches.md`

**跨多个请求的文件上传：**
→ 阅读 `{lang}/claude-api/README.md` + `{lang}/claude-api/files-api.md`

**具有内置工具（文件/网页/终端）的 Agent：**
→ 阅读 `{lang}/agent-sdk/README.md` + `{lang}/agent-sdk/patterns.md`

### Claude API (完整文件参考)

阅读**特定语言的 Claude API 文件夹** (`{language}/claude-api/`)：

1. **`{language}/claude-api/README.md`** — **先读这个。** 安装、快速入门、常见模式、错误处理。
2. **`shared/tool-use-concepts.md`** — 当用户需要函数调用、代码执行、记忆或结构化输出时阅读。涵盖概念基础。
3. **`{language}/claude-api/tool-use.md`** — 阅读特定语言的工具使用代码示例（工具运行器、手动循环、代码执行、记忆、结构化输出）。
4. **`{language}/claude-api/streaming.md`** — 在构建聊天 UI 或增量显示响应接口时阅读。
5. **`{language}/claude-api/batches.md`** — 离线处理大量请求（非延迟敏感）时阅读。以 50% 成本异步运行。
6. **`{language}/claude-api/files-api.md`** — 当在多个请求之间发送相同文件而无需重新上传时阅读。
7. **`shared/prompt-caching.md`** — 添加或优化提示缓存时阅读。涵盖前缀稳定性设计、断点位置和静默导致缓存失效的反面模式。
8. **`shared/error-codes.md`** — 调试 HTTP 错误或实现错误处理时阅读。
9. **`shared/live-sources.md`** — 获取最新官方文档的 WebFetch URL。

> **注意：** 对于 Java、Go、Ruby、C#、PHP 和 cURL — 它们分别有一个包含所有基础知识的单文件。根据需要阅读该文件以及 `shared/tool-use-concepts.md` 和 `shared/error-codes.md`。

### Agent SDK

阅读**特定语言的 Agent SDK 文件夹** (`{language}/agent-sdk/`)。Agent SDK 仅限 **Python 和 TypeScript** 使用。

1. **`{language}/agent-sdk/README.md`** — 安装、快速启动、内置工具、权限、MCP、回调挂钩。
2. **`{language}/agent-sdk/patterns.md`** — 自定义工具、回调挂钩、子 Agent、MCP 集成、会话恢复。
3. **`shared/live-sources.md`** — 有关获取当前 Agent SDK 最新文档阅读所在的那些一应 WebFetch URL 链接信息。

---

## 什么时候使用 WebFetch

以下情况使用 WebFetch 获取最新文档：

- 用户询问“最新”或“当前”信息时
- 缓存数据似乎有误
- 用户询问此处未涵盖的特定特性问题时

实时的在线获取网址源皆保留存放在那名为 `shared/live-sources.md` 的源端记事单中。

## 常见陷阱

- 请勿在将文件或内容传递给 API 时截断输入。如果内容过长，超出了上下文窗口的容纳限制，请通知用户并与其讨论相关选项（分块、总结摘要等），而不是默默地将其截断。
- **Opus 4.6 / Sonnet 4.6 思考 (thinking)：** 请使用 `thinking: {type: "adaptive"}` — 请 **不要** 使用 `budget_tokens`（它在 Opus 4.6 和 Sonnet 4.6 上均已被弃用）。对于旧版模型，`budget_tokens` 必须小于 `max_tokens`（最小为 1024）。如果设置有误将导致报错。
- **Opus 4.6 移除了预填 (prefill)：** Assistant 消息预填（上一轮 Assistant 所预留的回复）在 Opus 4.6 上会返回 400 错误。应该使用结构化输出（`output_config.format`）或是在系统提示词下达指令来控制响应的格式。
- **`max_tokens` 默认值：** 不要把 `max_tokens` 设置得太低 — 触及上限会导致模型在思考中途截断结果并需要重试。对于非流式请求，默认设置为 `~16000`（这使得响应保持在 SDK 的 HTTP 超时限制以内）。对于流式请求，默认设置为 `~64000`（不存在超时担忧，所以给模型留出足够的空间）。仅在你有明确原因时才调低：如分类任务（`~256`）、成本上限限制、或者有意要求非常短的输出。
- **128K 输出 Token 数：** Opus 4.6 支持最大达到 128K 的 `max_tokens`，但由于数值太大，SDK 会要求必须使用流式传输才能避免 HTTP 超时问题。请使用 `.stream()` 以及它的 `.get_final_message()` / `.finalMessage()` 方法。
- **工具调用 JSON 解析 (Opus 4.6)：** Opus 4.6 可能会在工具调用 `input` 字段中生成不同的经过转义的 JSON 字符串（例如，Unicode 或正斜杠转义）。请务必总是使用 `json.loads()` / `JSON.parse()` 解析工具的输入参数 — 绝对不要对已经被序列化的输入去进行原生字符串匹配。
- **结构化输出 (所有模型)：** 请在 `messages.create()` 上使用 `output_config: {format: {...}}`，而不是去使用那个被弃用了的 `output_format` 参数。这是一个对整个 API 面向的通用更改，并非只是 4.6 版的专属情况。
- **不要重复造轮子去实现 SDK 已有功能：** SDK 提供了高层面的便捷助手 — 请直接使用它们，而不是从零开始一点点自己构建。具体来说：使用 `stream.finalMessage()` 代替将 `.on()` 事件监听嵌套到新建一个 `new Promise()` 去捕获；使用具有明确分类的异常类（如 `Anthropic.RateLimitError` 等）而不是通过进行字符串匹配判断报错内容文字；使用 SDK 类型（如 `Anthropic.MessageParam`、`Anthropic.Tool`、`Anthropic.Message` 等）而不是自己又重新定义一份与之对齐一样的等效接口。
- **不要给 SDK 的数据结构去自定义类型：** 这全套 SDK 已完全提供了在所有 API 对象所需的所有专属类型定义可供使用。使用 `Anthropic.MessageParam` 表示消息，`Anthropic.Tool` 表示工具的定义，`Anthropic.ToolUseBlock` / `Anthropic.ToolResultBlockParam` 表示使用结果，`Anthropic.Message` 表示获得的回应。定义自己的 `interface ChatMessage { role: string; content: unknown }` 会导致发生去重复了 SDK 已有的事并且会丧失类型安全保障。
- **生成报告和记录文档输出：** 对于旨在生成报告、文档化和可视化的这类请求任务，沙盒内已预置了包库如 `python-docx`、`python-pptx`、`matplotlib`、`pillow` 与 `pypdf`。Claude 可由此生成相应各格式（DOCX、PDF、图表）并通过 Files API 把内容回传给你 — 当碰到"生成报告"和"生成文档"一类相关的要求，比起单纯使用纯文本终端返回形式 (plain stdout text) 请多加考虑该方案选项。
