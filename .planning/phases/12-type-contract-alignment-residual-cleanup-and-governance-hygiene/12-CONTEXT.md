# Phase 12 Context

**Phase:** `12 Type contract alignment residual cleanup and governance hygiene`
**Milestone:** `v1.1 Protocol Fidelity & Operability`
**Date:** 2026-03-14
**Status:** Planned from PRD Express Path
**Source:** PRD Express Path (`.planning/phases/12-type-contract-alignment-residual-cleanup-and-governance-hygiene/12-PRD.md`) + current baseline verification

## User / Product Context

- 契约者要求先复核上一轮终极审阅报告哪些内容在**当前基线**上仍然成立，再把仍成立的问题编织进 `Phase 12`。
- 契约者明确要求：**不要为了测试保留 compat 冗余**；已经关闭的残留不要因历史报告而复活。
- 因此 `Phase 12` 必须以“验证后的真问题”为输入，而不是机械照抄旧报告。

## Verified Current Inputs

### A. Static Type Contract Misalignment

- `uv run mypy` 当前仍失败，错误集中在 `runtime_types.py`、`core/coordinator/coordinator.py`、`core/api/client.py`、`control/diagnostics_surface.py`、`services/diagnostics/helpers.py` 与平台 setup 入口。
- 核心矛盾包括：
  - `LiproCoordinator` protocol 对 `devices` 可写性与 `Coordinator` 当前 read-only public surface 不一致
  - `async_query_ota_info()` 的 public return contract 与 `Coordinator` / 平台消费者不一致
  - `LiproRestFacade` 与 typed service protocols 之间仍有 `dict[str, Any]` / structured rows 的分裂

### B. Remaining Explicit Compat Residuals

- 仍在 active governance truth 中登记的残留包括：
  - `core.api.LiproClient`
  - `LiproProtocolFacade.get_device_list`
  - `LiproMqttFacade.raw_client`
  - `DeviceCapabilities` compat alias
  - `_ClientBase` 及相关 API compat spine 残留
- `services/wiring.py` 与 `_ClientEndpointsMixin` aggregate export 已关闭，不再作为本 phase 的 active production residual。

### C. Developer / Config Drift

- `docs/developer_architecture.md` 仍写 `Coordinator` “约 450 LOC”，与当前文件现实不符。
- `custom_components/lipro/quality_scale.yaml` 仍引用过时测试路径 `tests/test_config_flow.py`，且 README known limitations 数量叙事已落后。
- `.devcontainer.json` 仍指向 `venv/bin/python`，与仓库当前 `.venv` 约定不一致。

### D. Contributor / Open-Source Governance Gaps

- `CONTRIBUTING.md` 与 `.github/pull_request_template.md` 尚未把 CI `security` job 纳入显式 contributor contract。
- `.github/CODEOWNERS` 仍是单维护者配置。
- 顶层尚无 `CODE_OF_CONDUCT.md` / `SUPPORT.md`。
- CI 尚未接入 shell 脚本静态门禁。

## Explicitly Excluded Because Already Fixed

- `tests/core/test_device_refresh.py` 与 canonical `get_devices(offset, limit)` 已对齐。
- `tests/core/ota/test_ota_candidate.py` 与 `manifest_truth` 已对齐。
- `tests/meta/test_governance_guards.py` 与 `.planning/v1.1-MILESTONE-AUDIT.md` 已对齐到 `current_snapshot`。
- `custom_components/lipro/services/wiring.py` 已删除，不能被重新合法化。
- `_ClientEndpointsMixin` aggregate export 已从 active endpoint surface 移除。

## Locked Decisions

### Type Policy
- `uv run mypy` 通过是本 phase 的硬门槛之一。
- 优先收敛 public contract 与 concrete implementation，而不是用更宽的 `Any`/`object` 继续掩盖分歧。

### Residual Policy
- compat 只允许继续缩窄，不允许因为旧测试或旧报告而回流。
- 已关闭 residual 必须保持关闭；仍保留者必须继续显式登记并附 delete gate。

### Governance Policy
- 活跃治理真源只看 `docs/*`、`.planning/baseline/*`、`.planning/reviews/*`、`.github/*` 与 contributor-facing docs。
- 历史 phase 资产可以提供背景，但不能反向定义今天的 truth。

### Scope Policy
- 本 phase 是“精准收口”而非“再造架构”：不引入新技术栈、不重开 shared-core 叙事、不做无边界 feature 扩张。

## Planning Expectations

- plans 应至少覆盖四条主线：
  1. type contract convergence
  2. compat seam cleanup / narrowing
  3. developer/config truth calibration
  4. contributor/open-source governance hygiene
- 每个 plan 必须说明：要清理的 residual、涉及文件、验证矩阵、以及哪些旧报告项已被判定为 out-of-scope。
- 若某些开源治理项不准备立即实现，plan 必须明确给出“记录决策 + 文档化理由”，而不是把它们重新变成口头债。

## Claude's Discretion

- plan 的波次切分
- compat seam 是“物理删除”还是“进一步缩窄并写清 delete gate”
- community governance 项是“新增文件”还是“显式记录暂缓决策”

## Specific References

- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/device/capabilities.py`
- `docs/developer_architecture.md`
- `custom_components/lipro/quality_scale.yaml`
- `.devcontainer.json`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- `.github/workflows/ci.yml`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

## Deferred / Out of Scope

- 重新打开已修复的 Phase 11 测试迁移问题
- 恢复任何已删除 compat shell
- 大规模 feature 扩展或 shared-core 抽离

---

*Phase: 12-type-contract-alignment-residual-cleanup-and-governance-hygiene*
*Context gathered: 2026-03-14 via PRD Express Path*
