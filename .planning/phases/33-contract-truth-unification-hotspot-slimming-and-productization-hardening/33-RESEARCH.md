# Phase 33 Research

**Phase:** `33 Contract-truth unification, hotspot slimming, and productization hardening`
**Date:** `2026-03-18`
**Scope:** runtime contract truth、control plane 边界、giant roots / helper hotspots、exception arbitration、assurance / productization follow-through
**Method:** full-repo terminal audit + targeted hotspot reread + current governance/gate truth cross-check

## 1. Architecture / Contract Truth

### Verified truths

- `LiproProtocolFacade` 作为单一协议根已经成立，`LiproRestFacade` / `LiproMqttFacade` 现在更多是 child façade，而不是并行根，见 `custom_components/lipro/core/protocol/facade.py`、`custom_components/lipro/core/api/client.py`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`。
- `Coordinator` 仍是唯一正式 runtime root；`RuntimeOrchestrator` / `RuntimeContext` 已把 wiring 与 runtime service ownership 拆开，见 `custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/coordinator/orchestrator.py`。
- control plane formal homes 已固定：`EntryLifecycleController`、`ServiceRegistry`、`DiagnosticsSurface`、`SystemHealthSurface`、`RuntimeAccess`、`telemetry_surface` 等不再散回 HA 根模块，见 `custom_components/lipro/control/entry_lifecycle_controller.py`、`custom_components/lipro/control/service_registry.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/control/telemetry_surface.py`。

### Remaining architecture risk

- runtime contract 真源仍重复：`custom_components/lipro/__init__.py` 里定义了一份 `LiproRuntimeCoordinator`，`custom_components/lipro/runtime_types.py` 又定义了一份更完整的 `LiproRuntimeCoordinator / LiproCoordinator`。这会让 platform adapters、control helpers 与 runtime public surface 的 authority 继续分叉。
- `RuntimeCoordinatorSnapshot` 名义上是 read-model，实际上仍携带 live `coordinator`，让 control-plane support surfaces 对 runtime root 保持直接依赖，见 `custom_components/lipro/control/models.py`。
- control 内部仍有局部回路：`custom_components/lipro/control/runtime_access.py` 为了 system health / telemetry view 反向局部导入 `telemetry_surface`；`telemetry_surface.py` 又继续通过 `_get_explicit_attr` / `getattr` 做反射式 contract 探测，而不是显式 port。

### Research implication

`Phase 33` 必须优先把 runtime contract authority 压成单一真源，并把 control-plane telemetry / read-model / locator 做成 acyclic、port-based 边界；否则后续 giant roots 拆薄会继续踩在双真源与 ghost seam 上。

## 2. Hotspots / Structural Pressure

### Verified hotspots

- `custom_components/lipro/core/api/client.py` 仍是巨型 REST child façade，兼具 state proxy、transport wrapper、compat entrypoint 与 capability surface。
- `custom_components/lipro/core/protocol/facade.py` 仍保留大量 REST pass-through / lifecycle glue，虽然 formal root 正确，但转发面仍偏宽。
- `custom_components/lipro/core/coordinator/coordinator.py` 仍承载过多 orchestration、update-cycle、MQTT lifecycle、failure recording 与 shutdown semantics。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 与 `custom_components/lipro/core/command/result.py` 已经有更正确的 formal home，但仍是高 churn、规则密集、适合继续拆 collaborator 的 giant helper hotspots。
- `custom_components/lipro/core/protocol/boundary/rest_decoder.py` 是 canonical contract truth home，结构密集且影响面大，后续拆薄必须非常克制，不能牺牲 contract authority。

### Planning implication

热点拆薄的顺序不应平均撒网；应先处理“重复转发 + authority 吸附”最严重的 root/home，再处理“高 churn rule engine”类 helper。也就是说：先 `client.py` / `facade.py` / `coordinator.py`，再 `snapshot.py` / `command/result.py` / `rest_decoder.py` 的协作者分裂。

## 3. Exception Policy / Typed Debt / Residual Honesty

### Verified truths

- `Phase 31/32` 已经把 broad-catch 从“无约束散落”推进到“有预算、有 guard、有语义记录”的状态；快照原子拒绝链也已关闭旧 P0，见 `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`、`custom_components/lipro/core/coordinator/runtime/device_runtime.py`。
- repo-wide `mypy` 与 `ruff` 当前都是真绿；生产代码没有看到新的 `type: ignore` 回流，说明 hygiene 基线是可靠的，见 `pyproject.toml` 与当前 gates。

### Remaining debt

- production 中仍约有 31 处 `except Exception` / 类似 catch-all。热点集中在 `custom_components/lipro/control/entry_lifecycle_controller.py`、`custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/coordinator/runtime/device/snapshot.py`、`custom_components/lipro/core/utils/background_task_manager.py`、`custom_components/lipro/services/maintenance.py`。
- 一些 residual naming / shell 仍在：`custom_components/lipro/core/protocol/compat.py` 是典型空壳；部分 endpoint docstring 仍在使用 `legacy` / `mixin` 叙事；control exports 也偏宽。
- typed debt 不再是“会不会炸”的问题，而是“边界是否足够诚实”的问题：`Any` / `Mapping[str, object]` / 反射式 attr probe 仍集中在 control-support、telemetry export 与 protocol-adjacent helpers。

### Planning implication

`Phase 33` 不应只追求 broad-catch 数字下降，而要把 catch-all 收束到更少、命名明确、guard 可守的 arbitration points；同时必须把 naming residue 与 empty compat shells 一起处理，否则代码与文档会继续讲两套故事。

## 4. Assurance / Productization / Governance Follow-Through

### Strong current posture

- `.github/workflows/ci.yml` 与 `.github/workflows/release.yml` 已经形成强治理链：release 复用 CI、tag/version truth、runtime `pip-audit`、SBOM、artifact attestation/provenance、release identity manifest。
- README / CONTRIBUTING / SUPPORT / SECURITY / runbook 已经明显优于普通 HA 仓库；`install.sh` 的 zip preflight、checksum 校验、manifest 验证、rollback posture 也很成熟。
- `.planning/codebase/*.md` 已诚实降格为 derived collaboration maps，避免派生图谱反向夺权。

### Remaining productization debt

- CI 仍重复执行 `tests/snapshots/`；pre-push 守门显著弱于 CI；benchmark 更像 advisory，而不是可裁决的 budget gate。
- deep docs 仍非完全双语：入口页双语较好，但 `SUPPORT.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 的深层 parity 仍有提升空间。
- `signing` / `code scanning` 仍是 defer truth；仓库已经足够诚实，但若目标是 10/10 productization，就必须继续把 defer 边界、support window、maintainer continuity 与 dependency/compatibility posture 机器化/制度化。
- `.github/CODEOWNERS` 仍是单维护者 reality；这不是假问题，而是需要通过 continuity docs、release custody rule、support lifecycle wording 进一步硬化的现实约束。

### Planning implication

`Phase 33` 必须把 assurance hardening 与 productization hardening 当作正式交付，而不是“代码拆完再说”的尾巴；否则仓库会继续停在 8.8/10，而不是迈到真正的 10/10。

## 5. Planning Implications

### Sequencing

1. **先 contract / control truth**：统一 runtime contract authority、纯化 control snapshot / locator / telemetry ports。
2. **再 structural hotspots**：拆 `client.py` / `facade.py` / `coordinator.py` 等 giant roots，避免 authority / forwarder cluster 继续膨胀。
3. **再 exception / typed / residual**：对准 remaining catch-all、naming residue、compat shells、over-wide exports。
4. **再 assurance / productization**：对齐 CI/pre-push/benchmark/release evidence/dep posture/deep docs/continuity。
5. **最后以 tests/docs 收口**：把 mega-tests topicize 与 deep-doc parity 一起落成，形成长期维护友好的边界。

### Guard rails

- 不要把拆 giant roots 变成“创建第二 façade root”。
- 不要为了解耦 control support 而新增一套 shadow DTO / shadow truth。
- 不要把 benchmark / signing / code scanning 写成已经 blocking；若仍 deferred 或 advisory，就必须继续诚实。
- 不要只改英文或只改中文入口。

## Recommended 6-Plan Split

1. **33-01** — unify runtime contract truth and purify control read models
2. **33-02** — remove control-plane reflection loops and shrink over-wide exports
3. **33-03** — slim giant roots and forwarding clusters along formal seams
4. **33-04** — converge exception policy, typed debt, and residual naming truth
5. **33-05** — harden CI/pre-push/benchmark/release-evidence gates and reproducibility posture
6. **33-06** — topicize remaining mega-tests and close deep-doc / continuity productization gaps
