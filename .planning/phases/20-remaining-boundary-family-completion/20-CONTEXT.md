# Phase 20 Context

**Phase:** `20 Remaining Boundary Family Completion`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Date:** 2026-03-16
**Status:** Ready for planning
**Source:** current roadmap/requirements/state truth + Phase 19 closeout + focused code scan

## Why Phase 20 Exists

`Phase 18-19` 已证明 host-neutral nucleus 与 headless proof story 可以沿单一正式主链继续推进，但 `v1.2` 仍有一块明确登记、尚未正式化的技术债：**剩余 boundary families 仍未进入 registry-backed / replay-covered / authority-indexed 的正式边界家族体系**。

当前仓库中，protocol boundary 已有正式 family 与 registry：

- REST：`rest.mqtt-config`、`rest.device-list`、`rest.device-status`、`rest.mesh-group-status`
- MQTT：`mqtt.properties`
- formal homes：`custom_components/lipro/core/protocol/boundary/rest_decoder.py`、`custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`、`custom_components/lipro/core/protocol/boundary/schema_registry.py`
- replay/authority fixtures：`tests/fixtures/api_contracts/`、`tests/fixtures/protocol_boundary/`、`tests/fixtures/protocol_replay/`

但 roadmap 与 requirements 已明确点名，以下四类 remaining families 仍应在 `Phase 20` 完成正式化：

1. `rest.list-envelope.v1`
2. `rest.schedule-json.v1`
3. `mqtt.topic.v1`
4. `mqtt.message-envelope.v1`

本轮代码扫描显示，这些 remaining families 的“业务能力”并非不存在，而是**仍以 helper-level / endpoint-level / concrete-path ad-hoc 形式散落**：

- REST list envelope 目前仍主要隐含在 `rest_decoder.py` 的 `_extract_list_payload()` 等 helper 中，尚未以 family 身份登记。
- schedule JSON 仍主要存在于 `custom_components/lipro/core/api/endpoints/schedule.py` 与 `custom_components/lipro/services/schedule.py` 的 endpoint/service normalization 链中，尚未进入 protocol-boundary registry / replay family。
- MQTT topic parsing 目前主要存在于 `custom_components/lipro/core/mqtt/topics.py` 与 `custom_components/lipro/core/mqtt/message_processor.py`，尚未形成正式 boundary decoder family。
- MQTT message envelope 目前主要隐含在 `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py` 的 `_select_property_source()` 与 payload wrapping 逻辑中，尚未以独立 family 进入 registry / authority / replay truth。

因此，`Phase 20` 的目标不是“增加更多业务功能”，而是把这些已存在、但仍未被正式边界治理吸纳的 payload/topic/envelope truths 收编进单一 boundary family story，使 `SIM-03` / `SIM-05` 获得可执行的完成态。

## Goal

1. 把 `rest.list-envelope.v1` 与 `rest.schedule-json.v1` 正式落到 protocol boundary registry、authority fixtures 与 drift assertions。
2. 把 `mqtt.topic.v1` 与 `mqtt.message-envelope.v1` 正式落到 protocol boundary registry、authority fixtures 与 drift assertions。
3. 让 replay manifests / fixture inventory / authority matrix / baseline docs 不再把这些 families 视为 partial / de-scope / implicit helper behavior。
4. 继续减少 schedule/topic/envelope/list 方向的 helper-level ad-hoc normalization，但不偷跑到 `Phase 21` 的 broad-catch / observability hardening。

## Decisions (Locked)

- **单一正式主链不变**：`LiproProtocolFacade` 仍是唯一正式 protocol root；`Coordinator` 仍是唯一正式 runtime root。
- **formalization only**：本 phase 的本质是 boundary family formalization，不是新增第二套 protocol story，不是抽新框架，也不是通用 CLI/host 设计。
- **family must be registry-backed**：每个新增 family 都必须具备稳定 `family/version` 身份、authority source、fixture truth、decoder registry entry 与最小 drift assertion。
- **authority must stay singular**：fixtures / manifests / docs 只能引用 authority source，不得复制第二份 payload truth。
- **replay must remain public-path-based**：新增 replay coverage 只能通过 formal protocol/boundary public path 驱动，不得绕开 registry/decoder 直接写 helper assertions。
- **phase boundary strictness**：本 phase 只做 remaining families formalization；broad-catch 收窄、observability 分类统一、diagnostics/evidence 语言统一留给 `Phase 21`；全局 closeout 与发布治理留给 `Phase 22`。
- **minimum truth sync required**：若 family formalization 改变 baseline/review truth，必须同轮同步 `.planning/baseline/*.md`、`.planning/reviews/*.md` 与 phase 资产；若 `Phase 20` 完成，需最小回写 `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`。

## Non-Negotiable Constraints

- 不得新增第二条 decode authority chain。
- 不得让 helper / endpoint / service 成为比 boundary family 更高的 authority source。
- 不得把 schedule service normalization、message processor concrete handling 或 topic parser 当作正式真源继续扩散。
- 不得把 replay/evidence 反向提升为 authority source。
- 不得把 `Phase 20` 伪装成业务功能开发；它必须是 protocol-boundary truth formalization。

## Known Hotspots / Likely Homes

- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- `custom_components/lipro/core/protocol/boundary/schema_registry.py`
- `custom_components/lipro/core/api/endpoints/schedule.py`
- `custom_components/lipro/services/schedule.py`
- `custom_components/lipro/core/mqtt/topics.py`
- `custom_components/lipro/core/mqtt/message_processor.py`
- `tests/fixtures/api_contracts/`
- `tests/fixtures/protocol_boundary/`
- `tests/fixtures/protocol_replay/`
- `tests/harness/protocol/replay_loader.py`
- `tests/integration/test_protocol_replay_harness.py`

## Likely Deliverable Shape

- `20-01`: formalize remaining REST families (`rest.list-envelope.v1`, `rest.schedule-json.v1`)
- `20-02`: formalize remaining MQTT families (`mqtt.topic.v1`, `mqtt.message-envelope.v1`)
- `20-03`: sync inventory / fixtures / manifests / guards / docs to the new family truth

## Out of Scope

- broad-catch / exception taxonomy hardening
- diagnostics/system-health/evidence export classification unification
- release/readme/support/governance global closeout
- new host-neutral runtime abstraction or second consumer root

---

*Phase: 20-remaining-boundary-family-completion*
*Context gathered: 2026-03-16 via roadmap/requirements/state truth + focused protocol-boundary scan*
