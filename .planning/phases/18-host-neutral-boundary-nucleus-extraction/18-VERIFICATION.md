# 18 Verification

## Final Result

- `uv run python scripts/check_architecture_policy.py --check` ✅
- `uv run python scripts/check_file_matrix.py --check` ✅
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` ✅ (`59 passed`)
- `uv run pytest -q tests/flows/test_config_flow.py tests/core/test_init.py tests/core/test_token_persistence.py tests/core/test_categories.py tests/core/device/test_capabilities.py tests/core/capability/test_registry.py tests/core/test_device.py tests/core/device/test_device.py tests/platforms/test_entity_behavior.py tests/entities/test_descriptors.py tests/snapshots/test_device_snapshots.py` ✅ (`355 passed`)
- `uv run pytest -q` ✅ (`2188 passed`)
- `uv run ruff check .` ✅
- `uv run mypy` ✅

## Arbitration

- Phase 18 已把 auth/bootstrap reusable truth、device/capability host-neutral nucleus、HA platform projection adapter seam 与 governance guard chain 收口到同一条故事线。
- 本轮未更新 `.planning/STATE.md` / `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` 的全局 phase lifecycle，以避免覆盖当前 `Phase 17 closeout` 的里程碑归档真相；Phase 18 结果以本 phase 目录与对应 baseline/review truth 为准。
