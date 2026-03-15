# Phase 17 Context

## User Intent

- 继续对 `lipro-hass` 做全仓复查，并把仍然显性的 residual / compat / naming / typing / governance 尾债继续物理清理。
- 目标不是重开第二条架构故事线，而是在既有北极星单一主链下，继续做最后一轮高收益、低漂移、可验证的收口。
- 本 phase 必须同时满足：
  1. 使用 GSD 流程完成规划与执行；
  2. 使用小步、原子、可验证的方式推进；
  3. 不把历史 compat 再合法化；
  4. 完成后再做全仓验证与终审。

## Current Truth

- `Phase 16` 已完成并通过全量验证；`v1.1` 里程碑审计当前状态为 `tech_debt`，说明无 blocker，但仍有显式 residual 未物理退场。
- 当前 second-pass 复查后，remaining residual 主要集中在：
  - `_ClientTransportMixin` 只剩定义与导出，已接近纯死壳；
  - `_ClientBase` 与 endpoint legacy mixin family 仍延续旧继承叙事；
  - `persist_entry_tokens_if_changed()` 仍保留 `get_auth_data()` fallback；
  - `power_service.py` 仍输出 helper-level compatibility envelope；
  - `LiproMqttClient` 仍是显眼的 legacy transport name，且 meta guard 对 locality 的 pytest 显式覆盖还不够；
  - 全仓 residual 指标仍为 `Any=632`、`except Exception=36`、`type: ignore=12`。

## Non-Negotiables

- `LiproProtocolFacade` 仍是唯一正式 protocol root。
- `Coordinator` 仍是唯一正式 runtime orchestration root。
- 不允许新增 second root、旁路 wiring、raw payload backflow、无 gate rename campaign。
- 所有残留清理必须同步治理资产：`ROADMAP`、`STATE`、`REQUIREMENTS`、baseline、reviews、phase artifacts。

## Phase 17 Candidate Work

1. 退役 `_ClientTransportMixin`，并把 `_ClientBase` / endpoint mixin family 继续收敛到显式 protocol port。
2. 删除 `entry_auth` 中的 `get_auth_data()` fallback，把 token persistence 统一到 `AuthSessionSnapshot` 正式契约。
3. 收口 `power_service.py` 的 compatibility envelope，把 outlet-power helper 契约写成显式 typed contract，而不是隐式 `{"data": rows}` 包装。
4. 继续 demote `LiproMqttClient` legacy naming：生产代码尽量转向 transport-local canonical naming / protocol contract，测试与 guards 同步跟进。
5. 把以上 changes 回写到 governance truth，并完成 phase verification / validation / final repo audit。

## Success Shape

- API residual spine 被物理削薄，而不再只是“文档上登记”。
- auth/power contract 更明确，旧 fallback / shape envelope 被移除或显式降级。
- MQTT transport naming/locality 不再在非 transport 位置扩散，并有 focused meta guard 兜底。
- `Phase 17` 完成后，治理资产与 repo audit 对同一组 residual 讲同一条故事，不留下新的 silent defer。
