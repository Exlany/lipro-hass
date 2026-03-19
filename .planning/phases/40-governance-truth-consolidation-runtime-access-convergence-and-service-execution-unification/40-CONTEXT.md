# Phase 40: Governance truth consolidation, runtime-access convergence, and service execution unification - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning
**Source:** fresh audit continuation after `v1.4` archive

<domain>
## Phase Boundary

本 phase 只收三类 post-v1.4 高价值尾债：

1. authority precedence / active truth / archive snapshot / derived-map identity 仍有口径漂移；
2. control/services 对 runtime 的 read-model 仍分散在 `runtime_access`、`diagnostics_surface`、`device_lookup`、`maintenance` 等处；
3. service-layer auth/error execution contract 仍有 duplicated path，尤其是 `schedule.py` 没有完全复用 `services/execution.py`。

本 phase 不重开 protocol/runtime/control root，不恢复 compat shell，不把 archive snapshots 误升为 active truth。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `v1.4` archive assets 继续保留历史证据身份，但 current truth 只能由 `PROJECT / ROADMAP / REQUIREMENTS / STATE`、baseline、review ledgers 与 developer docs 解释。
- continuity / release-trust / install-path / support-routing 必须拥有 machine-readable registry，并由 meta guards 强制同步到 public docs / templates。
- `runtime_access` 是 control-plane 与 services 获取 runtime enumeration / device lookup / snapshot projection 的唯一正式 read-model home。
- `services/execution.py` 是 shared auth/error execution home；本 phase 不再允许 `schedule.py` 维护独立 coordinator auth chain。
- touched naming residue 继续向 `protocol` / `port` / `facade` / `operations` 语义收口；stale `client` / `forwarding` / `mixin` wording 只允许留在历史/归档资产中。

### Claude's Discretion
- registry 文件的具体位置、字段命名与 meta-test 接入方式；
- runtime_access 新 helper 的粒度；
- phase-40 tests 是扩写现有套件还是新增 focused meta guard。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态与禁止项
- `AGENTS.md` — 仓库级 authority 顺序、phase sync contract、正式 plane 裁决
- `.planning/ROADMAP.md` — current roadmap truth and phase contract
- `.planning/REQUIREMENTS.md` — requirement IDs and traceability truth
- `.planning/STATE.md` — current execution status and next-command truth
- `.planning/baseline/PUBLIC_SURFACES.md` — public surface / control-home / assurance identity
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority precedence and sync direction
- `.planning/baseline/VERIFICATION_MATRIX.md` — acceptance / phase evidence contract
- `.planning/reviews/V1_4_EVIDENCE_INDEX.md` — archived milestone evidence pointer
- `.planning/v1.4-MILESTONE-AUDIT.md` — archived milestone verdict and evidence links

### Runtime-access / control / services
- `custom_components/lipro/control/runtime_access.py` — formal runtime read-model home
- `custom_components/lipro/control/diagnostics_surface.py` — control diagnostics projection
- `custom_components/lipro/services/device_lookup.py` — service device/coordinator lookup
- `custom_components/lipro/services/maintenance.py` — service runtime entry refresh enumeration
- `custom_components/lipro/services/execution.py` — shared auth/error execution facade
- `custom_components/lipro/services/schedule.py` — schedule handlers needing execution convergence

### Touched terminology hotspots
- `custom_components/lipro/core/api/auth_service.py`
- `custom_components/lipro/core/api/endpoint_surface.py`
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/coordinator/runtime/command/sender.py`

### Validation / guards
- `tests/core/test_control_plane.py`
- `tests/core/test_diagnostics.py`
- `tests/services/test_device_lookup.py`
- `tests/services/test_maintenance.py`
- `tests/services/test_execution.py`
- `tests/services/test_services_schedule.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_version_sync.py`

</canonical_refs>

<specifics>
## Specific Ideas

- baseline 三件套需吸收 `v1.4` closeout 和 `Phase 38/39` 合同；
- `docs/README.md` 需要明确区分 active truth、archive snapshots、derived maps 与 compatibility notes；
- continuity/runbook 需要补 break-glass verify-only / non-publish rehearsal story；
- `runtime_access` 可新增 shared helpers：runtime entry/coordinator iteration、device lookup、update-interval/device mapping projection；
- `schedule.py` 与 diagnostics auth-aware helper 应优先复用 shared service execution contract，避免 duplicated reauth logic。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 内重命名 `custom_components/lipro/core/api/client.py` 文件本身；当前只清理 touched stale terminology 与 internal symbols。
- 不在本 phase 内重做 `Coordinator` / `LiproProtocolFacade` root 结构；只消费现有正式 ports/surfaces。
- 不引入新的 abstraction layer、compat shell 或 second execution story。

</deferred>

---

*Phase: 40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification*
*Context gathered: 2026-03-19 via fresh audit continuation*
