# Summary 111-02

## What changed
- 扩展 `.planning/baseline/ARCHITECTURE_POLICY.md`：`ENF-IMP-ENTITY-PROTOCOL-INTERNALS` 现在同时禁止 entity/platform 直连 `core.coordinator`，`ENF-IMP-CONTROL-NO-BYPASS` 覆盖面扩到 `custom_components/lipro/control/**/*.py`。
- 新增 targeted no-regrowth bans：`ENF-ADAPTER-ENTITY-RUNTIME-BRIDGE` 固化 entity typed bridge；`ENF-BACKDOOR-RUNTIME-ACCESS-NO-RAW-RUNTIME-DATA` 禁止 `runtime_access.py` 回流 raw `runtime_data` probing。
- 同步回写 `.planning/baseline/DEPENDENCY_MATRIX.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md`，把 Phase 111 的 boundary-law、guard truth 与 runnable proof 纳入正式基线。
- 更新 `scripts/check_architecture_policy.py` 与 `tests/meta/test_governance_guards.py` 的 inventory 预期，并新增 `tests/meta/test_phase111_runtime_boundary_guards.py` 作为 focused regression guard。
- 重写 `.planning/reviews/FILE_MATRIX.md` 并修复 `.planning/STATE.md` 的 machine-checkable governance sections，使 `check_file_matrix` 与 targeted governance suite 重新一致。

## Why it changed
- `GOV-71` 要求 entity/control → runtime concrete bypass 不再依赖人工 review，而要落成 policy + script + pytest 三位一体的 machine-check guard。
- 新里程碑 `v1.31` 启动后，`STATE.md` 与 file-matrix governance story 出现了 active-route 结构漂移；若不一并修复，focused guard 会持续被旧真相拖累。

## Verification
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py tests/meta/test_phase111_runtime_boundary_guards.py`
- `40 passed in 4.89s`
- `uv run ruff check tests/meta/test_governance_guards.py tests/meta/test_phase111_runtime_boundary_guards.py scripts/check_architecture_policy.py`
- `All checks passed!`

## Outcome
- entity/control runtime-boundary bans 现在已有单一 baseline 真相、脚本执行器与 focused pytest proof。
- `STATE.md` / `FILE_MATRIX.md` 不再破坏 111-02 的治理验证闭环。
