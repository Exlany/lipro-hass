# Summary 112-03

## What changed
- 更新 `.planning/baseline/AUTHORITY_MATRIX.md`：live planning governance-route contract family 现在只承认 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`，`.planning/MILESTONES.md` 明确回到 archive chronology / evidence 角色；latest archived evidence pointer 对齐到 `V1_30`。
- 更新 `.planning/reviews/FILE_MATRIX.md`：为 `entry_auth.py` 与 `runtime_infra.py` 补上 sanctioned formal-home wording，并登记新的 `tests/meta/test_phase112_formal_home_governance_guards.py`。
- 向 `.planning/baseline/VERIFICATION_MATRIX.md` 增加 `Phase 112` acceptance section，把 current route、default next、required artifacts 与 runnable proof 收口为正式验证真源。
- 新增 `tests/meta/test_phase112_formal_home_governance_guards.py`，冻结 maintainer docs route truth、archived pointer、sanctioned-home wording 与 `coordinator.coordinator` residue closeout。
- 把 active route machine truth 前推到 `Phase 112 in progress`：更新 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 的 governance-route contract/default next，并同步 `tests/meta/governance_current_truth.py` 与 `tests/meta/test_governance_route_handoff_smoke.py`。

## Why it changed
- `GOV-72` 要求 formal-home discoverability 与 governance-anchor cleanup 成为 baseline/review/guard 一致的 machine-check truth，而不是一次性文档补丁。
- 随着 `Phase 112` 进入执行态，live route selector、default next 与 smoke suite 也必须从 `discussion-ready` 前推到 `in progress`。

## Verification
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/governance_current_truth.py tests/meta/test_governance_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py`
- `18 passed in 3.98s`
- `uv run ruff check custom_components/lipro/control/runtime_access_types.py custom_components/lipro/control/runtime_access_support_views.py custom_components/lipro/control/runtime_access_support_devices.py custom_components/lipro/control/developer_router_support.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py tests/meta/governance_current_truth.py tests/meta/test_governance_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py tests/meta/governance_followup_route_current_milestones.py`
- `All checks passed!`

## Outcome
- `Phase 112` 的 docs / baseline / review / guard 真相现在收束为单一主链。
- active route 已前推到 `Phase 112 in progress`，后续只剩 phase-level verification / completion，再把默认路由前推到 `Phase 113`。
