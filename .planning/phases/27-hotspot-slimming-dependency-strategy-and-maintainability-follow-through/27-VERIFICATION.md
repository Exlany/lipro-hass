# Phase 27 Verification

status: passed

## Goal

- 核验 `Phase 27: hotspot slimming, dependency strategy and maintainability follow-through` 是否完成 `HOT-05` / `RES-04` / `TST-02`：继续切薄 runtime/protocol hotspot、清理旧 phase residue，并把测试巨石拆成更稳定的专题套件。
- 终审结论：**`HOT-05`、`RES-04` 与 `TST-02` 已在 2026-03-17 完成；`protocol_service` formal capability port、forwarder retirement 与 test-monolith split 现已同源闭环。**

## Reviewed Assets

- Phase 资产：`27-CONTEXT.md`、`27-RESEARCH.md`、`27-VALIDATION.md`
- 已生成 summaries：`27-01-SUMMARY.md`、`27-02-SUMMARY.md`、`27-03-SUMMARY.md`、`27-04-SUMMARY.md`
- synced truth：`custom_components/lipro/{runtime_types.py,services/schedule.py,services/diagnostics/handlers.py,entities/firmware_update.py}`、`custom_components/lipro/core/coordinator/{coordinator.py,runtime_context.py,orchestrator.py}`、`tests/{conftest.py,core/test_init.py,core/test_init_service_handlers.py,services/test_services_diagnostics.py,services/test_service_resilience.py,test_coordinator_public.py,meta/test_governance_guards.py,meta/test_governance_closeout_guards.py,meta/test_public_surface_guards.py,meta/test_toolchain_truth.py}`、`scripts/check_file_matrix.py`、`.github/workflows/ci.yml`、`.pre-commit-config.yaml`、`AGENTS.md`、`CONTRIBUTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/codebase/{STRUCTURE,TESTING}.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER}.md`、`.planning/baseline/{PUBLIC_SURFACES,DEPENDENCY_MATRIX,VERIFICATION_MATRIX}.md`、`.planning/v1.3-HANDOFF.md`

## Must-Haves

- **1. Formal capability-port convergence — PASS**
  - `ProtocolServiceLike` 与 `LiproCoordinator.protocol_service` 现已成为 runtime-owned formal capability surface。
  - schedule / diagnostics / firmware-update consumer 不再依赖 `Coordinator` 的纯转发方法或 ghost seam。

- **2. Hotspot slimming without second-root regression — PASS**
  - `Coordinator` 上一簇纯协议转发方法已退场，outlet-power polling 也已直接依赖 formal service。
  - 这次切薄没有新建第二 root / bus / DI 容器；`Coordinator` 仍是唯一正式 runtime root。

- **3. Test megafile split with governance truth sync — PASS**
  - `tests/core/test_init.py` 与 `tests/meta/test_governance_guards.py` 已拆出专题套件，同时保留锚点文件。
  - `TESTING.md`、`FILE_MATRIX.md` 与 `test_toolchain_truth.py` 已同步新文件与新计数，没有留下治理漂移。

## Evidence

- `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_task_callback.py` → `106 passed`
- `uv run pytest -q tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/test_coordinator_public.py tests/core/test_coordinator.py` → `245 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` → `74 passed`
- `uv run python scripts/check_file_matrix.py --check` → 退出码 `0`
- `uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/services/schedule.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/entities/firmware_update.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/coordinator/runtime_context.py custom_components/lipro/core/coordinator/orchestrator.py tests/conftest.py tests/core/test_init.py tests/core/test_init_service_handlers.py tests/services/test_services_diagnostics.py tests/services/test_service_resilience.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_toolchain_truth.py scripts/check_file_matrix.py` → `All checks passed!`

## Risks / Notes

- `LiproRestFacade` 仍然是 remaining hotspot，但它被诚实登记为 child-façade maintainability debt，而不是 second-root 故事线。
- 本 phase 没有把 reverse-engineered vendor `MD5` 登录哈希路径误登记为仓库弱密码学债；该路径继续按协议约束处理。
- 若后续继续推进 v1.3 closeout，应先基于当前 completed route map 做 milestone 归档/下一轮 seed，而不是回退到 `client` seam 或 mega-test 故事线。
