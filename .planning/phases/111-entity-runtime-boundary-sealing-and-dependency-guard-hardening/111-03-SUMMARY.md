# Summary 111-03

## What changed
- 在 `tests/core/test_runtime_access.py` 补齐坏 seam proof：显式但 underspecified 的 `runtime_data` 会降级成受限 read-model；空 `entry_id` 会拒绝生成 diagnostics projection。
- 在 `tests/core/test_init_service_handlers_commands.py` 补齐 `send_command` 失败分支：空命令字符串触发 schema validation，property list item 缺失 `value` 或非 mapping 会 fail-fast。
- 在 `tests/core/test_init_service_handlers_debug_queries.py` 补齐 `query_command_result` 终态 proof：新增 `failed` terminal 与 budget-exhausted `unconfirmed` terminal 覆盖。

## Why it changed
- `TST-38` 要求把 runtime access 与 command-result changed surface 的关键坏分支冻结成 focused tests，避免未来只能靠全仓 mega-suite 才发现回归。
- 这些分支正是 `Phase 111` 触碰后的高价值薄弱点：underspecified runtime seam、service payload validation 与 polled command-result terminal semantics。

## Verification
- `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py`
- `39 passed in 1.01s`
- `uv run ruff check tests/core/test_runtime_access.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py`
- `All checks passed!`

## Outcome
- runtime_access 的 degraded / rejected seam 已有直接 proof。
- `send_command` 与 `query_command_result` 的关键失败/未确认终态已被冻结为局部回归测试，不再依赖隐式 coverage。
