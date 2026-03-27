# Contributor Architecture Change Map / 贡献者架构变更地图

> This page is the contributor-facing routing layer between the public docs entrypoints and the deeper architecture authorities.  
> 本页是 public docs 入口与深层架构权威文档之间的 contributor-facing 路由层。

Use this page when you already know **what kind of change** you want to make, but need to know **where it belongs**, **what not to touch**, and **which evidence must be updated**.
当你已经知道自己要做哪类改动，但还不确定**改哪里**、**不能碰哪里**、**改完要补哪些证据**时，请先读这页。

## Before You Start / 开始之前

- Public docs map / 公开入口总索引：`docs/README.md`
- Contributor workflow / 贡献流程与 CI 契约：`CONTRIBUTING.md`
- Troubleshooting and support route / 排障与支持路由：`docs/TROUBLESHOOTING.md` → `SUPPORT.md`
- Private security disclosure / 私密安全披露：`SECURITY.md`
- Authority baseline / 权威长期裁决：`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- Current implementation topology / 当前实现拓扑：`docs/developer_architecture.md`

## What This Page Does Not Do / 本页不做什么

- It does **not** expose active milestone routing, archived pointers, or internal GSD workflow commands.
- It does **not** replace `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` or `docs/developer_architecture.md` as authority sources.
- It does **not** authorize a second architecture story, compat-root comeback, or raw vendor payload leaks.
- 本页**不会**暴露 active milestone route、archived pointer 或内部 GSD 命令流。
- 本页**不会**取代 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 或 `docs/developer_architecture.md` 的权威地位。
- 本页**不会**为第二套架构故事、compat root 回流或 raw vendor payload 泄漏提供合法性。

## Start by Change Family / 按改动家族选择入口

| Change family | Start here | Typical scope | Must update evidence in | Focused validation |
| --- | --- | --- | --- | --- |
| Protocol | `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/api/`, `custom_components/lipro/core/mqtt/` | façade contracts, request policy, transport normalization, auth recovery | `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/DEPENDENCY_MATRIX.md`, `.planning/baseline/VERIFICATION_MATRIX.md` | `uv run pytest tests/core/api tests/core/mqtt tests/integration/test_mqtt_coordinator_integration.py -q` |
| Runtime | `custom_components/lipro/core/coordinator/` | polling, command confirmation, snapshot refresh, MQTT lifecycle | `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md` | `uv run pytest tests/core/test_control_plane.py tests/core/test_init*.py tests/core/test_system_health.py -q` |
| Control | `custom_components/lipro/control/`, `custom_components/lipro/services/` | service routing, lifecycle, runtime access, diagnostics, system health | `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/DEPENDENCY_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md` | `uv run pytest tests/core/test_control_plane.py tests/services/test_services_registry.py tests/core/test_diagnostics.py -q` |
| External-boundary | protocol boundary + diagnostics/share/support surfaces | payload normalization, authority boundaries, report/export redaction, firmware/support truth | `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md` | `uv run pytest tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/core/ota/test_firmware_manifest.py -q` |
| Governance / docs | `README.md`, `README_zh.md`, `docs/README.md`, `.planning/baseline/*`, `.planning/reviews/*`, `tests/meta/` | public entry docs, contributor routing, guards, evidence ledgers | `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/reviews/FILE_MATRIX.md`, `.planning/reviews/PROMOTED_PHASE_ASSETS.md` | `uv run python scripts/check_file_matrix.py --check` + `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_version_sync.py` |

## Change Family Rules / 各家族改动规则

### 1. Protocol / 协议面

**Allowed story / 允许的故事线**
- Keep `LiproProtocolFacade` as the only protocol-plane root.
- Normalize vendor payloads at the protocol boundary before they reach runtime/domain/entity layers.
- Add or refine REST/MQTT collaborators only when they still converge back into the same façade chain.

**Do not / 禁止项**
- Do not reintroduce `LiproClient`, `LiproMqttClient`, raw compat shells, or a second protocol root.
- Do not let raw vendor payloads flow through the formal boundary into runtime, domain, or entities.
- Do not make concrete transport classes the public story.

**Read next / 下一步阅读**
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `AGENTS.md`

### 2. Runtime / 运行面

**Allowed story / 允许的故事线**
- Keep `Coordinator` as the only runtime orchestration root.
- Extend runtime collaborators and services through explicit composition.
- Route command/snapshot/MQTT lifecycle changes through the runtime service layer.

**Do not / 禁止项**
- Do not bypass refresh/state write paths.
- Do not add new coordinator internals backdoors for control/platform/entity callers.
- Do not let platform adapters become runtime truth owners.

**Read next / 下一步阅读**
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `AGENTS.md`

### 3. Control / 控制面

**Allowed story / 允许的故事线**
- Use `custom_components/lipro/control/` as the formal home.
- Keep root HA files and `services/` as thin adapters or helper homes.
- Use `RuntimeAccess` instead of direct coordinator/entry internals reads.

**Do not / 禁止项**
- Do not let diagnostics/system health/services/flows scatter direct `entry.runtime_data` probing.
- Do not resurrect a second control root through helpers or root modules.
- Do not move maintainer-only governance truth into public docs or thin adapters.

### 4. External-boundary / 外部边界

**Allowed story / 允许的故事线**
- Normalize imported/exported payloads before they become shared truth.
- Preserve redaction, authority ownership, and firmware/support truth as explicit contracts.
- Treat troubleshooting/support/security wording as part of the boundary contract.

**Do not / 禁止项**
- Do not leak raw vendor, private, or unredacted payloads into user-facing or contributor-facing surfaces.
- Do not make support/security wording contradict access-mode truth.
- Do not use docs to promise release or support routes that are not actually reachable.

### 5. Governance / docs / 治理与文档

**Allowed story / 允许的故事线**
- Keep `README(.md/.zh)` as public first hop and `docs/README.md` as canonical docs map.
- Use contributor-facing docs to point at evidence destinations without exposing internal workflow folklore.
- Update focused guards when navigation or truth-source wording changes.

**Do not / 禁止项**
- Do not expose `.planning/*` current-route or internal GSD commands as public first-hop guidance.
- Do not let `docs/MAINTAINER_RELEASE_RUNBOOK.md` replace the public docs-first route.
- Do not change one public entry surface without syncing its paired/boundary docs.

## Evidence Destinations / 证据回写位置

Use these destinations when your change alters outward contracts or governance truth:
当改动会影响对外契约或治理真相时，请回写这些位置：

- Public surface changes / 对外 surface 变化：`.planning/baseline/PUBLIC_SURFACES.md`
- Dependency direction / 依赖方向变化：`.planning/baseline/DEPENDENCY_MATRIX.md`
- Authority or truth-source changes / authority 或真源变化：`.planning/baseline/AUTHORITY_MATRIX.md`
- Verification obligations / 验证义务变化：`.planning/baseline/VERIFICATION_MATRIX.md`
- File ownership or fate / 文件归属或命运变化：`.planning/reviews/FILE_MATRIX.md`
- Residual or delete-gate updates / 残留或清退门禁变化：`.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md`
- Promoted long-lived phase evidence / 提升为长期治理证据的 phase 资产：`.planning/reviews/PROMOTED_PHASE_ASSETS.md`

## Quick Decision Rules / 快速决策规则

- **Need the long-term law?** Read `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`.
- **Need the current topology?** Read `docs/developer_architecture.md`.
- **Need the contributor workflow?** Read `CONTRIBUTING.md`.
- **Need to know whether a docs/change route is public or maintainer-only?** Read `docs/README.md`, `SUPPORT.md`, and `SECURITY.md`.
- **Need to know where to record truth after the change?** Use the evidence destinations list above.

## Minimum Honest Validation / 最小诚实验证

After a non-trivial architecture or docs change, prefer this sequence:
发生非平凡架构或文档改动后，优先按此顺序验证：

1. `uv run python scripts/check_file_matrix.py --check`
2. `uv run ruff check .`
3. Run the focused pytest slice for the change family you touched.
4. If public docs or governance wording changed, run `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_version_sync.py`

## Keep the Story Single / 保持单一故事线

If you are unsure whether a change is correct, ask one question:
如果你不确定某个改动是否正确，只问自己一句：

> Is this converging the repository toward one north-star mainline, or quietly restoring a second legitimate architecture story?  
> 它是在把仓库继续收敛到单一 north-star 主链，还是在偷偷恢复第二套合法架构故事？

If the answer is the second one, stop and reroute.
如果答案是后者，就停下并重新选路。
