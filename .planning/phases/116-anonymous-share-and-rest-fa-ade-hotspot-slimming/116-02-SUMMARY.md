# Summary 116-02

## What changed
- 在 `custom_components/lipro/core/anonymous_share/manager.py` 中改用 `scope_state_property(...)` 统一绑定 `_ScopeState` 字段，收敛 `_collector`、`_last_upload_time`、`_installation_id`、`_ha_version`、`_share_client`、`_reported_device_keys`、`_storage_path` 与 `_cache_loaded` 的重复 getter/setter。
- 新增 `_AggregateViewState`，让多个 `aggregate_view()` 实例共享同一 aggregate submit outcome，同时 scoped manager 的 `last_submit_outcome` 继续独立落在各自 `_ScopeState` 上。
- 在 `tests/core/anonymous_share/test_manager_recording.py` 与 `tests/core/anonymous_share/test_manager_submission.py` 增加 focused regressions，分别冻结 registry-backed state binding 与 aggregate/scoped outcome boundary。

## Why it changed
- `manager.py` 的热点并不在 record/build/submit 主流程，而在 registry-backed scoped state 与 aggregate-view memory 的样板噪音和语义分叉。
- 本次收敛把 shared registry state 与 aggregate outcome carrier 明确化，避免 aggregate 结果污染 scoped outcome，也避免多个 aggregate view 对同一 registry 出现漂移结论。

## Verification
- `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/anonymous_share/test_manager_scope_views.py tests/core/anonymous_share/test_observability.py`
- `uv run ruff check custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_support.py tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py`

## Outcome
- `AnonymousShareManager` / `get_anonymous_share_manager()` outward contract 不变，但 `_ScopeState` 代理与 aggregate/scoped outcome 语义更集中、更稳定。
