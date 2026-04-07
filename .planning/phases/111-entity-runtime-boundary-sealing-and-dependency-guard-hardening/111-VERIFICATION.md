# Phase 111 Verification

## Verdict

- `ARC-28`: passed
- `GOV-71`: passed
- `TST-38`: passed

## Evidence

### 111-01 Entity runtime boundary sealing
- `custom_components/lipro/entities/base.py` 通过本地 `DataUpdateCoordinator` typed bridge 脱离 concrete `Coordinator` import/cast。
- `custom_components/lipro/entities/firmware_update.py` 全部 runtime verbs 已回到 `runtime_coordinator` surface。

### 111-02 Governance / dependency guards
- `.planning/baseline/ARCHITECTURE_POLICY.md` 已扩展 entity/control runtime-boundary inventory。
- `.planning/baseline/DEPENDENCY_MATRIX.md` / `.planning/baseline/VERIFICATION_MATRIX.md` 已同步纳入 Phase 111 truth。
- `tests/meta/test_phase111_runtime_boundary_guards.py` 已冻结 concrete import/cast / raw runtime-data no-regrowth proof。
- `.planning/STATE.md` 与 `.planning/reviews/FILE_MATRIX.md` 已恢复 machine-checkable governance 结构一致性。

### 111-03 Changed-surface validation
- `tests/core/test_runtime_access.py` 已覆盖 underspecified runtime seam 与 empty-entry projection reject。
- `tests/core/test_init_service_handlers_commands.py` 已覆盖 empty-command / malformed properties item 分支。
- `tests/core/test_init_service_handlers_debug_queries.py` 已覆盖 `failed` / `unconfirmed` terminal states。

## Commands

- `uv run pytest -q tests/platforms/test_entity_base.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_install_flow.py`
  - `34 passed in 1.13s`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py tests/meta/test_phase111_runtime_boundary_guards.py`
  - `40 passed in 4.89s`
- `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py`
  - `39 passed in 1.01s`
- `uv run pytest -q tests/platforms/test_entity_base.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_install_flow.py tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py tests/meta/test_phase111_runtime_boundary_guards.py tests/core/test_runtime_access.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py`
  - `113 passed in 6.71s`
- `uv run ruff check custom_components/lipro/entities/base.py custom_components/lipro/entities/firmware_update.py tests/platforms/test_entity_base.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_install_flow.py tests/meta/test_governance_guards.py tests/meta/test_phase111_runtime_boundary_guards.py tests/core/test_runtime_access.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py scripts/check_architecture_policy.py`
  - `All checks passed!`
- `uv run python scripts/check_architecture_policy.py --check`
  - passed
- `uv run python scripts/check_file_matrix.py --check`
  - passed
- `uv run mypy custom_components/lipro/entities/base.py custom_components/lipro/entities/firmware_update.py`
  - `Success: no issues found in 2 source files`

## Conclusion

Phase 111 的 entity/control → runtime boundary sealing、policy guard 固化与 changed-surface validation 已形成闭环；继续推进时不应再回头修补本阶段已关闭的 concrete bypass 漏口。
