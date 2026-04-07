# v1.23 Terminal Audit

**Purpose:** 将 `v1.23 / Phase 85` repo-wide terminal audit 冻结为 review-ledger-backed truth，而不是会话记忆。  
**Status:** Historical review artifact for `AUD-04` / `GOV-62`; current closeout truth lives in `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, and `.planning/reviews/{PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER,KILL_LIST}.md`  
**Updated:** 2026-03-27  
**Historical route snapshot:** `v1.23 active route / Phase 85 planning-ready / latest archived baseline = v1.22`  
**Scope:** `custom_components/lipro`, `tests`, `docs`, `.planning`, workflows/config entry surfaces

## Audit Contract

- 本文件负责记录 `close now / route next / explicitly keep` 的 file-level verdict，并与 `.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md` 同步。
- 审计 coverage 必须显式覆盖 `production / tests / tooling / docs / governance` 五类 area；即使某一类没有新增 route-next debt，也要在本文件中留下可读裁决。
- review ledger 的锁定列为 `verdict / route / owner / exit condition / evidence path`；后续 phase 不得静默删减这些裁决字段。
- 本文件不是新的 baseline；north-star 与 current-route 裁决仍以 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` 为准。
- 已关闭 residual family 只允许作为 historical closeout truth 被引用，不得因描述审计历史而回写成 active debt。

## Executive Verdict

本轮终局审计没有发现 production 侧 second-root 回流、`LiproClient` / `LiproMqttClient` 复活、或新的 ownerless active residual family；但发现 3 类必须显式登记的事项：

> **Phase 88 freeze note:** 本文件继续记录 `Phase 85` 审计时刻的 routed verdict。`Phase 86` / `Phase 87` 的 closeout 与当前 zero-active posture 以 `.planning/reviews/{PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER,KILL_LIST}.md` 和 `VERIFICATION_MATRIX.md` 为准。

1. **`Phase 85 close now` 真源漂移**：`TARGET_TOPOLOGY.md`、`DEPENDENCY_MATRIX.md`、`ARCHITECTURE_POLICY.md` 与 `docs/developer_architecture.md` 需要与当前 formal homes / backoff truth / freshness markers 对齐。
2. **`Phase 86 closed` production carry-forward**：`share_client.py` 的 silent compat alias / bool shim 已删除，`runtime_infra.py` hotspot 已 inward split 为 local helper，同时 formal home 未漂移。
3. **`Phase 87 route next` assurance carry-forward**：3 个 giant assurance roots 仍吸附过多 concern families，需要 topicization / thin-root 化与 focused guards。

## Governance / Docs Verdicts

| File | Severity | Verdict | Owner | Exit condition | Evidence |
|---|---|---|---|---|---|
| `.planning/baseline/TARGET_TOPOLOGY.md` | High | close now | `Phase 85 / Plan 85-01` | target-topology wording 只描述当前 formal roots，不再把 `AuthSession`、legacy client names 或旧 control-home prose 写成 current topology | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` |
| `.planning/baseline/DEPENDENCY_MATRIX.md` | High | close now | `Phase 85 / Plan 85-01` | backoff truth 只承认 `core/utils/backoff.py` 作为 neutral primitive home，`request_policy.py` 不再被写成 shared compat surface | `.planning/baseline/ARCHITECTURE_POLICY.md`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` |
| `.planning/baseline/ARCHITECTURE_POLICY.md` | Low | close now | `Phase 85 / Plan 85-01` | freshness / alignment 元数据与 `Phase 85` current truth 对齐，且 rule ids 不漂移 | `.planning/baseline/ARCHITECTURE_POLICY.md`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` |
| `docs/developer_architecture.md` | Medium | close now | `Phase 85 / Plan 85-01` | `current-topology guide` freshness marker、formal-home wording 与 `Phase 85` current route 保持一致 | `docs/developer_architecture.md`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` |

## Production Verdicts

| File | Severity | Verdict | Owner | Exit condition | Evidence |
|---|---|---|---|---|---|
| `custom_components/lipro/core/anonymous_share/share_client.py` | Medium | closed in Phase 86 | `Phase 86` (`HOT-37`, `ARC-22`) | `_safe_read_json()` backward-compatible alias 与 bool-only `submit_share_payload()` shim 已删除；production/tests 只承认 outcome-native submit path | `custom_components/lipro/core/anonymous_share/share_client.py`, `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/86-01-SUMMARY.md` |
| `custom_components/lipro/runtime_infra.py` | Medium | closed in Phase 86 | `Phase 86` (`HOT-37`, `ARC-22`) | listener / reload / task bookkeeping mechanics 已 inward split 到 `runtime_infra_device_registry.py`；`runtime_infra.py` 继续保持唯一 outward formal home | `custom_components/lipro/runtime_infra.py`, `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/86-02-SUMMARY.md` |

## Assurance Verdicts

| File | Severity | Verdict | Owner | Exit condition | Evidence |
|---|---|---|---|---|---|
| `tests/core/api/test_api_diagnostics_service.py` | Medium | route next | `Phase 87` (`HOT-38`, `TST-27`) | OTA / diagnostics / cloud-query concerns 完成 topicization，thin root 只保留 suite entry 语义 | `tests/core/api/test_api_diagnostics_service.py`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` |
| `tests/core/api/test_protocol_contract_matrix.py` | Medium | route next | `Phase 87` (`HOT-38`, `TST-27`) | protocol-contract matrix 被拆成 concern-local suites，并以 focused guards 维持 root-surface / fixture-authority coverage | `tests/core/api/test_protocol_contract_matrix.py`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` |
| `tests/core/coordinator/runtime/test_mqtt_runtime.py` | Medium | route next | `Phase 87` (`HOT-38`, `TST-27`) | connect / reconnect / message / reset / DI concerns 分拆为更诚实的 topic suites，失败可直接定位具体 concern family | `tests/core/coordinator/runtime/test_mqtt_runtime.py`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md` |

## Tooling / Workflow Verdicts

| File | Severity | Verdict | Owner | Exit condition | Evidence path |
|---|---|---|---|---|---|
| `scripts/check_architecture_policy.py` | Low | close now | `Phase 85 / Plan 85-02` | tooling / workflow audit 继续固定 north-star policy check 为 active guard，而不是另立第二套 review script story | `scripts/check_architecture_policy.py`, `.planning/baseline/ARCHITECTURE_POLICY.md` |
| `scripts/check_file_matrix.py` | Low | close now | `Phase 85 / Plan 85-02` | file-matrix inventory 与 routed hotspot ledger 保持同一条 truth；tooling 只承认 `FILE_MATRIX.md` 为 review output home | `scripts/check_file_matrix.py`, `.planning/reviews/FILE_MATRIX.md` |
| `.github/workflows/ci.yml` | Low | explicitly keep | governance/tooling keep | workflow/config entry surfaces 继续只消费现有 lint / typing / pytest / policy checks，不新增 parallel governance gate | `.github/workflows/ci.yml`, `.planning/baseline/VERIFICATION_MATRIX.md` |

## Explicitly-Keep Historical Truth

| File | Severity | Verdict | Owner | Exit condition | Evidence |
|---|---|---|---|---|---|
| `.planning/reviews/V1_22_EVIDENCE_INDEX.md` | Low | explicitly keep | historical-only | 保持 pull-only archived evidence pointer 身份；不得回流成 current mutable truth | `.planning/PROJECT.md`, `.planning/STATE.md` |
| `.planning/v1.22-MILESTONE-AUDIT.md` | Low | explicitly keep | historical-only | 保持 archived verdict home 身份；后续 milestone 只能 pull 其结论，不得反向定义 `v1.23` 当前路线 | `.planning/reviews/V1_22_EVIDENCE_INDEX.md`, `.planning/PROJECT.md` |

## Routing Rules

- **close now**：只用于真源漂移、低风险文档同步或不会引发半套生产 refactor 的问题。
- **route next**：用于需要代码/测试成组改动、删除 compat shell 或拆薄热点的事项。
- **closed in phase**：用于审计登记项已被后续 phase 真实关闭、当前仅保留历史闭环证据的对象。
- **explicitly keep**：仅用于历史 evidence / archived truth / 正式保留且理由充分的对象。

## Carry-Forward Matrix

| Phase | Scope | Must consume from this audit |
|---|---|---|
| `Phase 86` | production residual eradication | `share_client.py` compat aliases / bool shim 与 `runtime_infra.py` hotspot 已在本 phase closeout |
| `Phase 87` | assurance hotspot decomposition | `test_api_diagnostics_service.py`, `test_protocol_contract_matrix.py`, `test_mqtt_runtime.py` |
| `Phase 88` | governance sync / milestone freeze | all `close now / route next / explicitly keep` verdicts + ledger alignment |

## No-Regrowth Notes

- 本审计明确确认：没有任何理由把已关闭的 `LiproClient` / `LiproMqttClient` / archived-only route story 重新写回 active residual family。
- `runtime_infra.py` 与 giant assurance roots 的后续动作是 inward split / topicization，不是 file-delete folklore。
- `share_client.py` 的 symbol-level delete gates 已在 `Phase 86` 关闭；文件仍是正式 anonymous-share worker client home。
