---
phase: 119
slug: mqtt-boundary-runtime-contract-and-release-governance-hardening
nyquist_compliant: true
wave_0_complete: true
updated: 2026-04-01
---

# Phase 119 Validation Contract

## Wave Order

1. `119-01` restore one-way MQTT boundary authority and freeze focused guards
2. `119-02` collapse runtime/service typing drift into `runtime_types.py`
3. `119-03` harden semver-only release/governance truth and refresh live docs

## Completion Expectations

- `119-01/02/03-SUMMARY.md`、`119-SUMMARY.md`、`119-VERIFICATION.md` 与 `119-VALIDATION.md` 共同证明 `ARC-30 / ARC-31 / GOV-76 / GOV-77 / TST-41` 已在同一 active route 下闭环。
- `mqtt_decoder.py` 重新成为 MQTT topic/payload decode 的唯一 protocol-boundary truth；`payload.py`、`topics.py` 与 `message_processor.py` 只保留 localized helper 身份，不再反向定义 boundary。
- `runtime_types.py` 继续保持 runtime/service 正式 contract 真源；`services/execution.py`、`services/command.py` 与 `control/entry_lifecycle_support.py` 不再持有平行 Protocol / concrete coordinator typing drift。
- release/governance/docs 当前只讲 `v1.33 active / phase 119 complete; closeout-ready (2026-04-01)` 与 semver public release namespace，不再保留 Python shadow route dict、内部 tag namespace 或 stale changelog wording。

## GSD Route Evidence

- `119-01-SUMMARY.md` 已记录 MQTT boundary authority 回归 `protocol.boundary -> mqtt` 的单向主链，并新增 focused guard 冻结 reverse-import regression。
- `119-02-SUMMARY.md` 已记录 runtime/service typing 全部收束回 `runtime_types.py` 单一 formal truth，同时保留 `Coordinator` public runtime home 不变。
- `119-03-SUMMARY.md` 已记录 semver-only release namespace、canonical governance route helper 与 live docs/changelog freshness 收口到同一条 current-route story。
- `119-VERIFICATION.md` 已记录 focused pytest、`check_file_matrix`、`ruff`、全仓 `pytest -q` 与 GSD progress/state snapshots 全绿，当前 milestone 状态保持 closeout-ready。

## Validation Commands

- `uv run pytest tests/core/mqtt/test_mqtt_payload.py tests/core/mqtt/test_topics.py tests/core/mqtt/test_message_processor.py tests/meta/test_phase68_hotspot_budget_guards.py tests/meta/test_phase119_mqtt_boundary_guards.py -q`
- `uv run pytest tests/services/test_execution.py tests/core/coordinator/services/test_command_service.py tests/meta/test_runtime_contract_truth.py -q`
- `uv run pytest tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_release_contract.py tests/meta/toolchain_truth_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_phase112_formal_home_governance_guards.py -q`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run pytest -q`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 119`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init execute-phase 119`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements.
- No new framework/bootstrap layer or manual-only stub family was required for `Phase 119`.

## Manual-Only Verifications

- All phase behaviors have automated verification.

## Archive Truth Guardrail

- `Phase 119` 可以关闭 repo-internal MQTT boundary / runtime contract / release-governance residual，但不得把 repo-external maintainer continuity、public mirror、non-GitHub private fallback 等 open-source operations 限制伪装为仓内已解决能力。
- current route docs / tests / workflows 只被允许讲一条 live story：`v1.33 active milestone route / starting from latest archived baseline = v1.32`；closeout 之后再由 milestone archive promotion 接管 latest archived truth。
