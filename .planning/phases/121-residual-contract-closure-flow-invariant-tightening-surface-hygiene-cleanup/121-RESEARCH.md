# Phase 121 Research: residual contract closure, flow invariant tightening & surface hygiene cleanup

## Why this follow-up phase exists

`Phase 120` 已把主要 runtime/service contract、flow taxonomy 与 tooling/docs truth 收到 closeout-ready，但仓内仍留有几处“不会立刻炸、却继续稀释 formal truth”的残缝。`Phase 121` 的目标不是加功能，而是把这些 residual 从“还能解释”推进到“已彻底收口”。

## Findings

### 1. `runtime_access` read-model 仍携带 raw coordinator seam

- `custom_components/lipro/control/runtime_access_types.py` 当前让 `RuntimeCoordinatorView` 同时承载事实投影与 raw `LiproCoordinator` 根对象，且额外暴露 `runtime_coordinator` 属性。
- `custom_components/lipro/control/runtime_access_support_views.py`、`custom_components/lipro/control/runtime_access_support_devices.py` 与 `custom_components/lipro/control/developer_router_support.py` 继续通过 `view.coordinator.runtime_coordinator` 取回 raw runtime root。
- 这让 control-plane read-model 在语义上仍然是“顺便带着 runtime root 的 view”，而不是纯粹的 typed projection。

**Recommended direction**
- 让 `RuntimeCoordinatorView` 只保留 read-model facts；raw coordinator 仅通过 `get_entry_runtime_coordinator()`、`iter_runtime_coordinators()`、`iter_runtime_entry_coordinators()` 这类 dedicated helper surface 离开 helper cluster。
- 同时检查 `custom_components/lipro/control/__init__.py`，把没有实际消费者、只因“方便 import”而留下的 aggregate export 再缩一轮。

### 2. `flow/login.py` 仍有 silent default projection

- `custom_components/lipro/flow/login.py` 的 `ConfigEntryLoginProjection.from_auth_session()` 仍把缺失的 `access_token` / `refresh_token` / `user_id` 投影成 `""` / `0`。
- 这会把 malformed auth session 伪装成“合法但空”的 config-entry data，而不是 honest failure。

**Recommended direction**
- 在 projection edge 显式校验 required session fields；缺失时抛出 `ValueError` 或同等级显式失败。
- `custom_components/lipro/config_flow.py` 统一把这类 projection failure 映射为 `invalid_response`，保持 user / reauth / reconfigure outward error taxonomy 一致。

### 3. `flow/submission.py` existing-entry validators 仍有重复分支

- `validate_reauth_submission()` 与 `validate_reconfigure_submission()` 各自重复了 entry phone_id 解析、密码校验、remember-password default、`ExistingEntrySubmission` 装配逻辑。
- 二者差别主要只是 phone 来源：`reauth` 取 stored phone，`reconfigure` 取 user input phone。

**Recommended direction**
- 收敛出单一 existing-entry invariant helper：统一负责 `phone_id`、remember-password default、password validation 与 `ExistingEntrySubmission` 组装；phone 只作为参数差异输入。
- 保持 outward field/base error keys 不变，避免为了去重重写 UI 语义。

### 4. `scripts/lint` 默认 changed-surface assurance 仍耦合 `Phase 113`

- `scripts/lint` 的 focused assurance 路由仍直接执行 `tests/meta/test_phase113_hotspot_assurance_guards.py`。
- 这让当前默认 lint 的 operational contract 继续依赖历史 phase 编号，而不是一个中性的 toolchain guard home。

**Recommended direction**
- 抽出一个 neutral guard，例如 `tests/meta/test_changed_surface_assurance_guards.py`，承接 default-mode changed-surface routing contract。
- `tests/meta/test_phase113_hotspot_assurance_guards.py` 保留历史 hotspot budget / ledger truth，但不再充当 default lint 的唯一 operational anchor。

### 5. Public-surface aggregate export 仍可进一步收窄

- `custom_components/lipro/control/__init__.py` 仍 re-export 若干 runtime snapshot / telemetry convenience surface。
- 代码库内几乎没有实际消费者依赖这些聚合导出；继续保留只会模糊 sanctioned home 与 aggregate convenience surface 的边界。

**Recommended direction**
- 只保留 adapter-root / formally justified outward homes；把 runtime-access / telemetry convenience export 留在各自文件级 formal home。
- 同步更新 dependency/public-surface guards，防止宽导出回流。

## Recommended plan split

| Plan | Focus | Why this boundary is right |
|------|-------|----------------------------|
| `121-01` | runtime-access seam closure + control aggregate export hygiene | 同一批控制面 read-model / outward surface 问题，适合一起收口 |
| `121-02` | flow projection honesty + existing-entry validator convergence | 同属 config-flow invariant family，测试与语义强关联 |
| `121-03` | changed-surface assurance de-phaseization + governance truth sync | toolchain contract 与 live planning truth 适合末尾统一固化 |

## Dependency analysis

- `121-01` 与 `121-02` 可并行：代码边界分离，互不共享生产文件。
- `121-03` 更适合作为 wave 2：
  - 需要在 runtime/flow final truth 明确后更新 docs / route truth / meta guards。
  - `scripts/lint` 与 governance docs 更像收口层，而不是先决基础设施。

## Verification spine

### Runtime / control slice
- `uv run pytest tests/core/test_runtime_access.py tests/meta/test_phase112_formal_home_governance_guards.py tests/meta/dependency_guards_service_runtime.py tests/meta/test_public_surface_guards.py -q`

### Flow slice
- `uv run pytest tests/flows/test_flow_submission.py tests/flows/test_config_flow_user.py tests/flows/test_config_flow_reauth.py tests/flows/test_config_flow_reconfigure.py -q`

### Toolchain / governance slice
- `uv run pytest tests/meta/test_changed_surface_assurance_guards.py tests/meta/test_phase113_hotspot_assurance_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py -q`
- `uv run python scripts/check_file_matrix.py --check`

### Phase gate
- `uv run ruff check .`
- `uv run pytest -q`
- `uv run python scripts/check_file_matrix.py --check`

## Planning truth that must eventually sync

- `.planning/PROJECT.md` — current goal / current focus / default next command
- `.planning/ROADMAP.md` — phase 121 goal、plan list、current milestone summary
- `.planning/REQUIREMENTS.md` — 新 requirement basket 与 traceability
- `.planning/STATE.md` — current phase / progress / next command
- `.planning/MILESTONES.md` — current milestone phase range、phase story、plan progress
- `.planning/baseline/PUBLIC_SURFACES.md` — 若 `control/__init__.py` outward surface 进一步缩窄，则需同步 canonical wording

## Recommendation

按 `121-01` / `121-02` 并行、`121-03` 末尾收口执行，能在不重新放大 phase 体积的前提下，把本轮已知 non-blocking residual 一次性压回正式单主线。