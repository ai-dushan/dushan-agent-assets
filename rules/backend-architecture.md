---
description: 后端架构决策硬约束（分层、注入、VO 穿透等 8 条不可违反规则）
trigger: always_on
scope: backend
author: 渡山源码
project: dushan-admin-backend
---

# 后端架构决策（绝对不能违反）

1. VO 允许跨层穿透 — Service/Mapper 可直接使用 Controller 的 VO，不得误判为架构违规
2. BO 仅用于纯 Service 内部结构 — Controller 不使用的才需要 BO
3. Mapper 可接受 PageReqVO — 分页查询场景继承自 PageParam，合法
4. Service 层用 `Inject()` 注入依赖 — 禁止 `get_bean()` 动态获取
5. 跨子业务通过 Service 接口调用 — 禁止直接注入其他子业务的 Mapper
6. 租户 ID 由 `TenantContextHolder` 隐式传递 — 禁止方法签名中层层透传 tenant_id
7. 严格分层：Controller → Service → Mapper → DO — 禁止层级穿透
8. 纯方法约束用 `Protocol`，需 `__init__` 用 `ABC`，实现类 `class XxxImpl(XxxService)`
