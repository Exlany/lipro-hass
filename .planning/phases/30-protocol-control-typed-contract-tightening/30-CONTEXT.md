# Phase 30 Context

**Phase:** `30 Protocol/control typed contract tightening`
**Milestone:** `v1.3 Quality-10 Remediation & Productization`
**Date:** `2026-03-17`
**Status:** `planned — ready for execution`
**Source:** `ROADMAP` / `REQUIREMENTS` / `STATE` / `v1.3-HANDOFF` + boundary-adjacent typed hotspot inventory

## Why Phase 30 Exists

`Phase 29` 继续切薄 REST child façade 后，最高杠杆的 typed / exception debt 不在全仓，而在最靠近 boundary 与 control root 的 `core/api`、`core/protocol`、`control`。这里决定 formal contract，也最容易把灰区语义洗白成正式行为。

## Goal

1. 收紧 `core/api` 的 response/result spine、typed aliases 与 request/auth arbitration。
2. 收紧 `core/protocol` 的 canonical contract / decoder output / root broad-catch，并清除 boundary-adjacent `type: ignore`。
3. 收紧 `control` 的 lifecycle exception taxonomy，把 setup/unload 主链从 generic catch-all 提升为明确 arbitration。

## Decisions (Locked)

- 本 phase 只触及 `core/api`、`core/protocol`、`control` 与它们的直接 typed seams；runtime/service/platform distributed backlog 留给 `Phase 31`。
- 允许引入更精确的 typed alias / protocol / canonical payload contract，但不引入新的 public root、总线或 façade。
- broad-catch 只能在语义被明确分类后保留；若只是“为了不崩”，则不属于正式 contract。
- diagnostics/developer payload 的低杠杆 `Any` 尾债原则上留给 `Phase 31` 的 budget/no-growth 收官，除非是本 phase touched zone 的直接阻塞项。

## Non-Negotiable Constraints

- 不得顺手吞下 `Coordinator` / runtime state / services/platforms backlog。
- 不得为 type tightening 重写 vendor payload truth；canonical normalization 仍在 protocol boundary 发生。
- 不得因为 tightening 破坏 `LiproProtocolFacade -> LiproRestFacade` 正式主链。

## Canonical References

- `.planning/ROADMAP.md` — `Phase 30` goal / success criteria
- `.planning/REQUIREMENTS.md` — `TYP-06`, `ERR-04`
- `.planning/STATE.md` — continuation truth
- `.planning/v1.3-HANDOFF.md` — typed backlog baseline / separation rules
- `custom_components/lipro/core/api/client_auth_recovery.py`
- `custom_components/lipro/core/api/client_transport.py`
- `custom_components/lipro/core/api/endpoints/payloads.py`
- `custom_components/lipro/core/api/request_codec.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`

## Specifics To Lock During Planning

- 第一优先是 `REST response/result spine`：这是 `Any` 的传播源，最能连带压缩 protocol façade 的宽口。
- 第二优先是 `protocol boundary/root`：这里同时包含唯一 `type: ignore`、多处 broad-catch，以及 canonical contract 回落到 `dict[str, Any]` 的根因。
- 第三优先是 `control lifecycle root`：文件小但卡在 setup/unload 主链，`ERR-04` 价值极高。

## Expected Plan Shape

最优应为 `3 plans`：

1. REST response/result spine tightening
2. protocol boundary/root contract tightening
3. control lifecycle exception arbitration + touched-zone guard freeze
