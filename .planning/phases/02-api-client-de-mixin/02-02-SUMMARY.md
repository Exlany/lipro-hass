---
phase: 02-api-client-de-mixin
plan: "02"
subsystem: api
tags: [refactor, facade, transport, auth-recovery, request-policy]
requires:
  - phase: 02-01
    provides: rest slice governance matrix, residual/kill truth, formal phase-2 exit contract
provides:
  - `LiproRestFacade` 作为 Phase 2 正式 REST root 的首个代码落地
  - 显式 `ClientSessionState` / `TransportExecutor` / `AuthRecoveryCoordinator` / `RequestPolicy` 协作主链
  - `LiproClient` 降级为 transitional compat shell，但保留旧 patch/test seam
  - transport/helper tests 改为同时验证 formal collaborator 与 legacy seam 兼容
affects: [02-03, 02-04, 02.5]
completed: 2026-03-12
---

# Phase 02 Plan 02-02 执行总结

## 本次完成

- 在 `custom_components/lipro/core/api/client.py` 中引入 `LiproRestFacade`，并将 `LiproClient` 降级为继承 façade 的 transitional compat shell。
- 在 `custom_components/lipro/core/api/client_base.py` 中新增 `ClientSessionState`，把 session / token / refresh lock / user/biz state 收口到单一状态根。
- 在 `custom_components/lipro/core/api/client_transport.py` 中引入 `TransportExecutor`，把签名、会话获取、HTTP 执行、mapping-level retry 收敛到显式 transport collaborator。
- 在 `custom_components/lipro/core/api/client_auth_recovery.py` 中引入 `AuthRecoveryCoordinator`，把 auth 错误分类、refresh、replay、API 错误记录从继承链中剥离为独立协作者。
- 在 `custom_components/lipro/core/api/request_policy.py` 中引入 `RequestPolicy`，让 pacing / busy-retry / rate-limit policy 成为显式状态与策略对象。
- 保留 `client_pacing.py` / `client_transport.py` / `client_auth_recovery.py` 中的薄兼容壳，使大量 legacy tests 与 patch points 在 `02-02` 不被一次性打碎。
- 更新 `tests/core/api/test_api_client_transport.py`、`tests/core/api/test_helper_modules.py`、`tests/core/api/test_protocol_contract_matrix.py`，让测试既覆盖新 formal root/collaborator，又持续锁住 Phase 1 contract truth。

## 关键裁决

- **正式根裁决**：Phase 2 的正式 REST root 现在是 `LiproRestFacade`，不是 `LiproClient`。
- **状态所有权裁决**：session/auth/token/refresh single-flight 都归 `ClientSessionState`；transport 不再拥有状态事实源。
- **恢复链裁决**：`AuthRecoveryCoordinator` 负责认证错误分类、refresh 与 replay 决策；transport 只做执行，不直接改 auth state。
- **请求策略裁决**：`RequestPolicy` 成为 pacing / busy-retry / retry/backoff 的正式 owner；但对外保留旧 patch seam，避免下游测试与消费者瞬时断裂。
- **兼容面裁决**：`LiproClient` 继续保留 legacy list payload wrappers / method names，但正式协议逻辑已下沉到 façade + collaborators；compat shell 只做桥接，不再是主链。

## 验证结果

- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_client_transport.py tests/core/api/test_helper_modules.py -q`
  - 结果：`18 passed`
- `uv run pytest tests/core/api/test_api.py -q`
  - 结果：`216 passed`
- `uv run pytest tests/meta/test_public_surface_guards.py -q`
  - 结果：`3 passed`

## 修改文件

- `custom_components/lipro/core/api/__init__.py`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/client_base.py`
- `custom_components/lipro/core/api/client_transport.py`
- `custom_components/lipro/core/api/client_auth_recovery.py`
- `custom_components/lipro/core/api/client_pacing.py`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/transport_core.py`
- `tests/core/api/test_api_client_transport.py`
- `tests/core/api/test_helper_modules.py`
- `tests/core/api/test_protocol_contract_matrix.py`
- `.planning/phases/02-api-client-de-mixin/02-02-SUMMARY.md`

## 边界确认

- 本计划未迁移 endpoint collaborators / payload normalizers；这些仍由 `02-03` 负责。
- 本计划未正式删除 compat shell / legacy public names；这些仍由 `02-04` 收口。
- 本计划已确保：即使正式主链改为 façade + collaborators，legacy tests/patch seam 仍继续可用，不会让 Phase 2 在中途进入“双输状态”。

## 主代理下一步

- 可直接进入 `02-03`：迁移 endpoint collaborators 与 payload normalizers。
- `02-03` 必须开始削弱 `_ClientEndpointsMixin` 的正式地位，否则 `mixin` 残留仍停留在 endpoint 聚合层。
