# Phase 39 PRD — Governance Current-Story Convergence, Control-Home Clarification, and Mega-Test Decomposition

**Phase:** `39`
**Date:** `2026-03-19`
**Status:** Executed and completed (2026-03-19)

## Problem Statement

`Phase 38` 关闭了最后一条已登记的 active residual family，但仓库仍残留一组高价值尾债：

1. `ROADMAP / REQUIREMENTS / STATE / PROJECT / developer_architecture / NORTH_STAR` 对“当前里程碑 / 当前 tranche / next action / control-home”没有完全讲同一条故事。
2. `custom_components/lipro/control/` 已是正式 control-plane home，但 `services/` 与权威文档仍残留旧的迁移措辞与 carrier 叙事。
3. `custom_components/lipro/core/protocol/compat.py` 已成为无人引用的 dead shell；协议夹具 `get_device_list.envelope.json` 与相关 replay/test/doc 的命名与 governance evidence 需要完成单故事收口。
4. 多个巨石测试仍然过大，尤其是 device / mqtt / config-flow / anonymous-share / governance suites，继续增加认知负担与变更风险。

## Goals

- 把 governance current-story 收敛到以 `ROADMAP / REQUIREMENTS / STATE / PROJECT` 为核心、可机检的单一故事线。
- 把 control-plane formal home 明确固定到 `custom_components/lipro/control/`，并把 `services/` 重新表述为 declarations / adapters / handler helpers。
- 退役 dead compat shell 与误导性 compat/legacy 命名，不回退到第二 public story。
- 继续 topicize 巨石测试，并将治理守卫从长 prose 断言推进到更结构化的锚点与算术校验。
- 所有迁移伴随文档、夹具、回放、守卫、治理台账同步更新。

## Non-Goals

- 不创建新的 protocol/runtime/control root。
- 不重新引入 `compat shell`、`legacy constructor name`、`service wiring` 等旧语义。
- 不把 `v1.3` 回写为 failed audit，也不倒退到 handoff-only 叙事。
- 不借“兼容”名义保留无人引用的空壳模块。

## Locked Requirements

- **GOV-32**：authority/current-story 必须在 `ROADMAP / REQUIREMENTS / STATE / PROJECT / developer_architecture / NORTH_STAR` 之间收口，并由 machine-checkable guards 守护。
- **DOC-03**：开发者架构文档与北极星文档必须反映当前 formal planes / roots / current priority，不允许继续传播 stale version / phase / topology prose。
- **CTRL-08**：`control/` vs `services/` 的 formal role 必须只有一条故事；`control/` 是 formal home，`services/` 只承载 service declarations / adapters / handler helpers。
- **RES-09**：剩余 dead shell、compat/legacy naming 与误导性 fixture/replay authority 命名必须退役或历史化，不能继续暗示第二 public truth。
- **TST-07**：remaining mega-tests 与 governance suites 必须继续 topicize，治理守卫必须优先依赖 structured anchors / arithmetic checks，而不是 stale prose fragments。

## Acceptance Criteria

1. `ROADMAP`、`REQUIREMENTS`、`STATE`、`PROJECT` 对 `v1.4` / `Phase 39` 的现状与 next action 一致，且 coverage/traceability 算术无误。
2. `docs/developer_architecture.md` 与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 删除 stale version / phase residue，完整说明 current topology 与 control-home story。
3. `custom_components/lipro/core/protocol/compat.py` 退场；`get_device_list.envelope.json` 作为唯一 authority asset 命名被统一接受，所有 manifest/tests/readmes/guards 同步。
4. 巨石测试继续拆分为专题面，文件体量明显下降，且无 import-cycle / fixture leakage / collection regression。
5. `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / PROMOTED_PHASE_ASSETS` 与 phase 39 执行产物同步更新。
6. 全量验证通过：lint / typing / architecture policy / file matrix / translations / targeted pytest / full pytest。

## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/control/`
- `custom_components/lipro/services/`
- `tests/meta/test_governance_*.py`
- `tests/fixtures/api_contracts/README.md`
- `tests/fixtures/protocol_replay/README.md`

## Already Fixed / Must Not Be Replanned

- 不重开 `LiproClient` / `LiproMqttClient` / `raw_client` / `get_device_list` compat seam。
- 不回退 `Coordinator` / `LiproProtocolFacade` 单一正式主链。
- 不把 `services/execution.py` 重新描述为 active auth seam。
- 不把 `firmware_support_manifest.json` bundled trust-root 命名重新写回 advisory truth。
