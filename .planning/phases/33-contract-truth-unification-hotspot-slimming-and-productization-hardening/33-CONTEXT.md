# Phase 33 Context

**Phase:** `33 Contract-truth unification, hotspot slimming, and productization hardening`
**Milestone:** `post-v1.3 continuation seed`
**Date:** `2026-03-18`
**Status:** `planned — research/planning complete, ready for execution`
**Source:** full-repo terminal audit (`8.8/10`) + `.planning/{ROADMAP,REQUIREMENTS,STATE,PROJECT}.md` + `Phase 32` closeout assets + current repo-wide green gates

## Why Phase 33 Exists

`Phase 25 -> 32` 已经把 correctness、telemetry seam、truth convergence、release honesty 与 repo-wide typed/exception follow-through 推到一个明显高位；但最新全仓终审仍明确留下了一簇 **不再是 P0、但足以阻挡 10/10 水位** 的 remaining debt：

1. runtime public surface 仍有双真源迹象：`custom_components/lipro/__init__.py` 与 `custom_components/lipro/runtime_types.py` 同时定义 `LiproRuntimeCoordinator`，control 还在其上再扩一层 `LiproCoordinator`。
2. control plane 内部仍有局部回路与反射式边界：`runtime_access -> telemetry_surface` 的局部导入、`_get_explicit_attr/getattr` 式 contract 说明 port 化还没收口到位。
3. giant roots / forwarder clusters 仍偏胖：`LiproRestFacade`、`LiproProtocolFacade`、`Coordinator`、`SnapshotBuilder`、`CommandResult` 等对象继续承载过宽 surface 或过长分支。
4. broad-catch 与 exception arbitration 仍分散在 lifecycle / snapshot / runtime / background-task 等路径上，数量已被治理记录，但尚未统一抽象。
5. assurance / productization story 仍有 follow-through：CI 重复 snapshot、pre-push 弱于 CI、benchmark 仍偏 advisory、dependency/compatibility posture 偏进取、深层双语 docs 与 maintainer continuity 仍未到国际成熟开源产品水位。

## Goal

1. 统一 runtime contract 真源，去掉 control-plane 的回路与伪快照泄漏，确保 control/telemetry/support 只通过正式 port 读取 runtime 真相。
2. 继续切薄 giant roots / helper hotspots / pure forwarders，但不引入第二 root、第二 façade 或第二 authority story。
3. 把 remaining broad-catch、typed debt、naming residue 收束成更少、更诚实的 named arbitration / typed contracts / internal-only support surfaces。
4. 让 local / CI / release / benchmark / dependency / support / bilingual docs / maintainer continuity story 讲同一条 machine-checkable 产品化故事。
5. 把剩余 giant tests/topic debt 纳入显式执行计划，避免治理套件继续吸附过多互不相关的职责。

## Decisions (Locked)

- 本 phase 不新建第二 orchestration root、DI 容器、event bus、mega-helper registry 或 shadow public surface。
- runtime public surface 的正式类型真源只允许收敛，不允许再横向分叉。
- control plane 只能通过显式 locator / telemetry / read-model ports 读取 runtime；不允许再用反射式 fallback 把 ghost seam 合法化。
- giant roots 的拆薄只能沿 `protocol / control / runtime / services / tests / docs` 现有正式 homes 推进；不能因为想拆大文件而新建第二条架构故事线。
- broad-catch 数值下降不是目标本身；目标是把 catch-all 变成 named arbitration、typed failure contract 或显式 documented degraded semantics。
- repo-wide gate story 必须诚实：benchmark 若仍非 blocking，就必须讲清 advisory 身份；signing/code scanning 若仍未硬门禁，就必须继续明确 defer 边界。
- 深层 bilingual docs、support/security wording、release custody 与 maintainer continuity 必须同步推进；不能只修英文入口或只修中文入口。
- reverse-engineered vendor crypto constraints（如 `MD5` 登录路径）继续按上游协议约束处理，不被伪装成仓库当前可独立消灭的密码学债。

## Non-Negotiable Constraints

- 不得让 `custom_components/lipro/__init__.py` 再成长为第二份 runtime contract 真源。
- 不得让 `RuntimeCoordinatorSnapshot` 继续携带 live `coordinator` 作为所谓 snapshot。
- 不得以 helper / exporter / iterator 导出面扩张的方式，暗中把 control-support internals 提升成长期 public surface。
- 不得把 `compat` 空壳、legacy/mixin docstring、fallback wording 继续留在正式叙事中而不给 delete gate 或 truthful disposition。
- 不得为了追求局部清爽，弱化现有 governance / public-surface / version-sync / toolchain guards。
- 不得把依赖/兼容策略、support window 与 release posture 写成三套不同故事。

## Canonical References

### Governance / Route Truth
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/PROJECT.md`
- `.planning/codebase/README.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

### Architecture / Runtime / Control
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/control/__init__.py`
- `custom_components/lipro/control/models.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/telemetry_surface.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/protocol/compat.py`
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`
- `custom_components/lipro/core/command/result.py`
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`

### Assurance / Productization
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `.pre-commit-config.yaml`
- `pyproject.toml`
- `custom_components/lipro/manifest.json`
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/TROUBLESHOOTING.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/CODEOWNERS`
- `install.sh`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_toolchain_truth.py`
- `tests/core/api/test_api.py`
- `tests/core/test_init.py`
- `tests/core/test_init_service_handlers.py`
- `tests/benchmarks/test_command_benchmark.py`
- `tests/benchmarks/test_coordinator_performance.py`

## Specifics To Lock During Planning

- `33-01` 必须先统一 runtime contract 真源，并把 `RuntimeCoordinatorSnapshot` 改造成纯 DTO；否则后续 control/telemetry 计划都会踩在不稳定基础上。
- `33-02` 必须把 `runtime_access` / `telemetry_surface` 的局部回路与 over-wide exports 当作正式执行项，而不是“顺手 cleanup”。
- `33-03` 拆 giant roots 时要明确 child homes / service homes / boundary homes，禁止只做“把大文件切成更难找的小文件”。
- `33-04` 需要明确 broad-catch burn-down 的优先路径：lifecycle、snapshot、runtime/background-task、maintenance。
- `33-05` 必须把 `snapshot` 重复测试、pre-push 与 CI 反馈时机差、benchmark advisory-only posture、release evidence drift、dependency posture 一并纳入。
- `33-06` 不能只写“以后拆测试/文档”；必须点名 `tests/core/api/test_api.py`、`tests/core/test_init.py`、`tests/core/test_init_service_handlers.py`、`tests/meta/test_governance_guards.py` 与深层 bilingual docs / continuity surfaces 的 follow-through。

## Open Questions (to resolve in research/planning)

1. runtime contract 单真源最终应完全落在 `runtime_types.py`，还是要进一步把 `LiproCoordinator` / `LiproRuntimeCoordinator` 分层压缩？
2. control-plane telemetry port 应该以 exporter-facing protocol 抽象为主，还是先建立更窄的 read-model / snapshot port？
3. giant roots 的拆解顺序，究竟该先从 `client.py` / `facade.py` 开始，还是先从 `snapshot.py` / `command/result.py` 这种高 churn helper 开始，才能最大化收益并最小化回归成本？
4. benchmark gate 最低可行 hardening 是 artifact + baseline diff，还是 should start with PR smoke budgets? 计划需给出仓库现实可承受的版本。

---

*Phase directory: `33-contract-truth-unification-hotspot-slimming-and-productization-hardening`*
*Context gathered: 2026-03-18 from the terminal full-repo audit and current planning truth.*
