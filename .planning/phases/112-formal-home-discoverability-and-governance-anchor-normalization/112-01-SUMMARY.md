# Summary 112-01

## What changed
- 把 `docs/developer_architecture.md` 的 current-route header 更新为 `v1.31 active milestone route / starting from latest archived baseline = v1.30`，并把 `Last aligned through` 前推到 `Phase 112`。
- 在 developer architecture first-hop 中新增 `Sanctioned Root-level Homes` 段，并在快速导航 / control-plane / 目录映射里显式登记 `runtime_infra.py`、`runtime_types.py`、`entry_auth.py` 的正式归属。
- 移除 active-route 语境下的 archived-only `$gsd-new-milestone` 默认下一步叙事，改为把 continuation truth 指回 `.planning/STATE.md` 与 `$gsd-next`。
- 在 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 中补充 active-route selector truth，并把 latest archived evidence / audit pointer 统一到 `V1_30` / `v1.30`。

## Why it changed
- `ARC-29` 要求 sanctioned root homes 与 maintainer discoverability 讲同一条故事，不能让根层 formal homes 看起来像 accidental leftovers。
- `GOV-72` 要求 maintainer-facing docs 停止传播 archived-only current-story 与 stale archived pointers。

## Verification
- `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py`
- `65 passed in 1.38s`
- `uv run ruff check custom_components/lipro/control/runtime_access_types.py custom_components/lipro/control/runtime_access_support_views.py custom_components/lipro/control/runtime_access_support_devices.py custom_components/lipro/control/developer_router_support.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py`
- `All checks passed!`

## Outcome
- developer / maintainer first-hop 文档现在明确承认 active `v1.31` route 与 latest archived `v1.30` baseline。
- `runtime_infra.py`、`runtime_types.py`、`entry_auth.py` 在 first-hop docs 中具备清晰的 sanctioned-home discoverability。
