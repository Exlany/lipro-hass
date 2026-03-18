# Phase 32 Verification

status: passed

## Goal

- 核验 `Phase 32: Truth convergence, gate honesty, and quality-10 closeout` 是否完成 `GOV-24` / `QLT-05` / `GOV-25` / `GOV-26` / `HOT-07` / `TST-04` / `TYP-08` / `ERR-06` / `RES-06`：把 v1.3 路线尾部残留的 planning truth、toolchain/release posture、derived-map freshness、runtime/platform typing 与 residual wording 收束成 final closeout contract。
- 终审结论：**Phase 32 已通过。active planning truth、release/toolchain/public-doc truth、derived collaboration map boundary、runtime/platform typing 与 meta guards 现在讲同一条完成态故事。**

## Reviewed Assets

- Phase 资产：`32-CONTEXT.md`、`32-RESEARCH.md`、`32-VALIDATION.md`
- 已生成 summaries：`32-01-SUMMARY.md`、`32-02-SUMMARY.md`、`32-03-SUMMARY.md`、`32-04-SUMMARY.md`、`32-05-SUMMARY.md`
- synced truth：`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/*.md`、`.github/workflows/release.yml`、`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`custom_components/lipro/{helpers/platform.py,binary_sensor.py,climate.py,select.py,sensor.py,runtime_types.py}`、`custom_components/lipro/entities/{base.py,firmware_update.py}`、`tests/core/api/*`、`tests/core/coordinator/runtime/*`、`tests/harness/protocol/replay_driver.py`、`tests/integration/test_protocol_replay_harness.py`、`tests/meta/{test_governance_guards.py,test_governance_closeout_guards.py,test_public_surface_guards.py,test_toolchain_truth.py,test_phase31_runtime_budget_guards.py}`、`tests/platforms/{test_select.py,test_sensor.py,test_climate.py,test_update.py}`

## Must-Haves

- **1. Planning truth no longer forks — PASS**
  - `PROJECT` / `ROADMAP` / `REQUIREMENTS` / `STATE` 与 closeout guard 已切到 `Phase 32 complete`。
  - retained handoff/audit 指针继续保留历史身份，但不再伪装成 active route truth。

- **2. Gate / release / continuity story is honest and machine-checked — PASS**
  - repo-wide `ruff` / `mypy`、release identity evidence、single-maintainer continuity、support/security boundary 与 bilingual public-doc wording 现已通过 docs + workflow + tests 同步锁定。
  - `attestation/provenance`、`SBOM`、`signing defer`、`code_scanning defer` 已被分别记录，不再混叠成模糊“已验证发行”叙事。

- **3. Derived maps and typed/runtime residue are closed out instead of hand-waved — PASS**
  - `.planning/codebase/*.md` 现有 freshness / authority header，派生图谱身份已被 guard 固化。
  - helper/platform/runtime typing、`JsonObject` callback、replay harness canonical override 与 Phase 31 budget guard 已真修；全仓 `mypy` 真绿。

## Evidence

- `uv run ruff check .` → `All checks passed!`
- `uv run mypy` → `Success: no issues found in 448 source files`
- `uv run pytest -q tests/core/api/test_helper_modules.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_protocol_contract_matrix.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_device_runtime.py tests/integration/test_protocol_replay_harness.py tests/platforms/test_select.py tests/platforms/test_sensor.py tests/platforms/test_climate.py tests/platforms/test_update.py tests/meta/test_phase31_runtime_budget_guards.py` → `244 passed`
- `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run python scripts/check_translations.py && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` → translation checks passed + `84 passed`
- `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_governance_guards.py -k "toolchain or release or runbook or support or security or codebase or contributing or docs or public or architecture or template or owner"` → `28 passed`

## Risks / Notes

- `Phase 32` 关闭的是 v1.3 closeout tranche 中仍可由本仓库裁决的 truth / gate / typing / residual 项；它没有把未证实可替换的上游协议约束伪装成仓库内部“已消灭的密码学重构”。
- 后续若继续扩大 derived-map story、release posture 或 runtime/platform typed surface，必须同步回写 planning truth、baseline/review docs 与对应 meta guards。
