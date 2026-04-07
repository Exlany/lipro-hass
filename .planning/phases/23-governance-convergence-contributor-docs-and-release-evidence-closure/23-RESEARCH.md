# Phase 23 Research

**Status:** `research complete`
**Date:** `2026-03-16`
**Mode:** `user-directed replanning override`
**Requirements:** `GOV-16`, `GOV-17`
**Planning stance:** `保留已完成 23-01..03，仅追加 23-04+`
**Locked installer decision:** `install.sh` / `README.md` / `README_zh.md` 默认安装路径继续保持 `ARCHIVE_TAG=latest`

## Executive Judgment

- `23-01..03` 已是历史完成记录；本轮正确动作不是改写历史，而是在同一 phase 目录下追加 `23-04+` 的审查驱动计划。
- 当前存在一个必须正视的治理张力：`23-CONTEXT.md` 要求基于终极审查追加整改计划，但 `.planning/STATE.md`、`.planning/REQUIREMENTS.md`、`.planning/reviews/RESIDUAL_LEDGER.md` 仍把 `Phase 23/24` 记为 `complete/archive-ready/no silent defer`。因此新增计划的第一步必须先把“为何在已 closeout 之后仍追加 plan”讲清楚，并给出审查问题全覆盖账本。
- 最优拆分是 **5 个新增计划 / 4 个波次**：先修用户可见契约与低风险边界，再收正式主链与热点，然后处理 tests/scripts/governance 漂移，最后收 contributor docs / release evidence / defer handoff。
- 本轮研究只建议**重新规划**，不建议在研究阶段把上游 north-star / baseline / state truth 直接改写成“未完成”；只有执行真正落地后，才应按 authority order 回写。
- 锁定用户体验裁决：默认安装入口继续是 `ARCHIVE_TAG=latest`；pinned tag / `main` / mirror 仅作为高级或可复现场景，不能反客为主。

## Audit-driven Scope Map

### 1. 治理真相与 phase 身份

- `23-CONTEXT.md` 明确要求：所有审查问题必须落入 `execute now / phase-local defer / future phase`，不能 silent drop。
- 但当前 active governance truth 仍宣称 `Phase 23/24` 已收官，说明本轮 planning 必须先建立“历史完成 + 用户定向增量整改”的 addendum 叙事。
- `.planning/phases/**` 默认仍是执行工作区资产，不应被新的 `23-RESEARCH.md` 反向提升成平行 authority chain。

### 2. Production / Architecture

- `custom_components/lipro/fan.py` 存在真实契约错位：`gentle_wind` 未进入 `PRESET_MODES`，换气扇 `preset_mode()` 可能返回 `off`，但 `VENT_PRESET_MODES` 未包含它。
- `custom_components/lipro/control/runtime_access.py` 的 `_as_runtime_entry()` 通过修改对象 `__dict__` 伪造 `entry_id/options`，且 telemetry 缺失时仍会回退读取 coordinator internals，这与 control-plane 只读边界不一致。
- `custom_components/lipro/entities/base.py` 仍由实体直接走 `Coordinator.async_send_command()`；这和北极星的 `Entity -> Service -> Runtime` 叙事仍有距离。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 仍在 runtime 执行 compat row normalization；该归一化是否应继续下沉到 protocol boundary，必须在本轮明裁。
- runtime snapshot 与 developer report 仍是双套投影：`build_runtime_snapshot()` 与 `build_developer_report()` 字段重叠但未共享 builder，`gateway/IR/panel/mesh` 诊断仍依赖 sidecar 数据拼装。
- `custom_components/lipro/control/service_router.py`、`custom_components/lipro/core/utils/developer_report.py`、`custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/api/client.py` 依旧是热点文件；`control` 与 `services` 仍有双向耦合；高价值 broad `except Exception` 仍需继续收窄。

### 3. Tests / Scripts / Governance Assets

- `.planning/codebase/TESTING.md` 本质是 derived collaboration map，但其统计数字已被审查点名漂移；要么刷新，要么加 stale gate，不能继续当静态真相。
- `scripts/check_architecture_policy.py` 依赖 `tests.helpers.*`，`scripts/export_ai_debug_evidence_pack.py` 依赖 `tests.harness.*`；这暴露出 script authority purity 不够硬。
- 多个 meta/tests 仍偏向 wording guard；超大测试文件与 coordinator 私有内部强耦合也已进入审查视野，至少需要先形成 execute-now 与 defer 的边界账本。

### 4. Contributor Docs / Release Evidence / Open-source Posture

- `README.md` / `README_zh.md` 已形成良好的双语入口，但 contributor-facing evidence path 仍不够显式：贡献者能看到 troubleshooting / runbook，却看不到“何时跑架构治理检查、何时导出 evidence pack”。
- `README*` 多处要求附上 `failure_summary` / `failure_entries`，但当前 developer report 的稳定输出字段并未与该叙事完全同构。
- `.github/workflows/release.yml` 目前做到的是：复用 `ci.yml`、校验 tag=version、产出 zip 与 `SHA256SUMS`。这足以证明“可发包”，但还不足以构成更完整的发布证据故事。
- 单维护者脆弱性、模板与 `docs/TROUBLESHOOTING.md` 的 developer-report 口径、`firmware_support_manifest.json` 的 metadata/信任链，都应纳入本轮分类，但不能虚假承诺仓库当前没有的人力或供应链设施。

## Recommended Plan Structure

### Wave 4

#### 23-04 — 用户可见契约与低风险边界快修

**建议目标**

- 修复 `fan.py` 的 preset/options 契约错位。
- 去除 `runtime_access.py` 的 `__dict__` 注入，改成无副作用的 runtime-entry 读取方式。
- 明确 installer / README / troubleshooting 的默认安装主路径继续是 `ARCHIVE_TAG=latest`，并把 pinned tag / `main` / mirror 明确降级为高级场景。

**为何先做**

- 这些问题直接影响普通用户安装、实体 UI 与 control-plane 安全边界，是最适合优先收口的一组低风险高收益缺口。

### Wave 5

#### 23-05 — Entity / Runtime / Protocol 正式主链收口

**建议目标**

- 裁决 `entities/base.py` 的命令路径是否进一步经 service/runtime formal surface 收口。
- 裁决 `snapshot.py` 的 compat normalization 是否继续下沉到 protocol boundary。
- 收窄与本计划直接相关的 typed-failure / fallback seam，避免继续旁读 coordinator internals。

**边界约束**

- 可以做中等深度 production refactor，但不得恢复第二条正式主链，也不得新增 compat shell。

#### 23-06 — Hotspot 减重、typed-failure 与 control/services 降耦

**建议目标**

- 对 `service_router.py`、`developer_report.py` 做一轮局部减重与职责拆分。
- 切断 `control ↔ services` 的双向耦合路径。
- 对 `coordinator.py`、`api/client.py` 做必要的轻量减重；剩余热点必须显式登记 defer/follow-up。

**为何与 23-05 并列同 wave**

- `23-05` 聚焦主链正确性；`23-06` 聚焦维护性与 blast-radius reduction。两者可共享验证背景，但最好分成两个原子计划执行。

### Wave 6

#### 23-07 — Tests / Scripts / Governance Purity Repair

**建议目标**

- 刷新 `.planning/codebase/TESTING.md`，或建立派生图谱 stale gate。
- 审视 `scripts/check_architecture_policy.py`、`scripts/export_ai_debug_evidence_pack.py` 对 `tests.*` 的依赖，并明确 authority boundary。
- 产出 audit coverage checklist / future-debt ledger，确保本轮终极审查项没有 silent omission。

### Wave 7

#### 23-08 — Contributor Docs、Release Evidence 与 Defer/Handoff 收口

**建议目标**

- 对齐 `README.md`、`README_zh.md`、`docs/TROUBLESHOOTING.md`、issue/PR templates、release runbook、evidence index 的对外叙事。
- 把 contributor-facing evidence path 讲清楚：什么时候需要 diagnostics、developer report、architecture policy check、evidence pack。
- 让 release 继续复用 `ci.yml` gate，同时补上“最小充分”的发布证据故事；但不要在本轮伪装成已经拥有完整 provenance/SBOM/signing/code-scanning 体系。
- 明确写出本轮 defer/handoff：单维护者韧性、完整供应链增强、firmware manifest 深化 metadata/签名、长尾 test debt 与 broad-catch 尾项。

## Risk/Boundary

- **不要重写历史**：`23-01..03` 仍是已完成记录；本轮是 addendum，不是历史清洗。
- **不要反转安装体验**：默认安装入口仍是 `ARCHIVE_TAG=latest`；这不是可谈判优化项，而是锁定决策。
- **不要为了解释问题而制造第二主链**：docs/reporting/release evidence 的修补必须继续 pull 正式真源，不能新造 compat shell、旁路 telemetry、旁路 runtime。
- **不要在本 phase 虚构治理能力**：多维护者承诺、私有安全运营、完整供应链 attestation 若仓库当前并不存在，只能如实 defer。
- **不要在 research 阶段篡改 authority order**：若后续执行触发文档回写，仍应遵守 `north-star -> baseline -> roadmap/state -> phase assets -> tests/scripts`。

### 适合在本 phase 执行

- 治理真相 addendum 与全覆盖账本。
- `fan.py` 契约修复、`runtime_access.py` 无副作用读取、主链/reporting contract 收口。
- 热点减重第一刀、control/services 降耦第一刀、高价值 typed-failure 收窄。
- `TESTING.md` 漂移修复、script authority purity 修补、关键结构化 guards。
- contributor docs / release evidence 的最小充分对齐。

### 仅应作为 follow-up / defer

- provenance / SBOM / signing / code scanning 的完整上线。
- 单维护者 bus factor 的组织性扩容。
- 仓库级 broad-catch 尾项清零。
- giant tests 全量拆分、marker 体系重建、benchmark threshold、coverage baseline engineering。
- `firmware_support_manifest.json` 的深度 metadata / trust-chain / signing 体系。

## Validation Architecture

### Validation dimensions

1. **Coverage completeness**：每个审查问题都必须落入某个计划或 defer ledger。
2. **User-facing contract**：`fan` preset、developer report guidance、README 安装与 troubleshooting 口径一致。
3. **Mainline integrity**：不恢复第二主链，不新增 compat shell，不让 control/runtime/reporting 再旁路 internals。
4. **Governance purity**：phase 资产、baseline、脚本、tests、release evidence 的 authority order 保持单向。

### Recommended validation slices

- `uv run pytest tests/platforms/test_fan.py tests/platforms/test_entity_base.py -q`
- `uv run pytest tests/core/test_system_health.py tests/core/test_diagnostics.py tests/core/test_developer_report.py tests/services/test_services_registry.py tests/services/test_services_diagnostics.py -q`
- `uv run pytest tests/core/coordinator/test_entity_protocol.py tests/core/test_device_list_snapshot.py tests/core/api/test_api_diagnostics_service.py -q`
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_evidence_pack_authority.py -q`
- `uv run pytest tests/integration/test_ai_debug_evidence_pack.py tests/integration/test_protocol_replay_harness.py tests/integration/test_mqtt_coordinator_integration.py -q`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run ruff check .`

## Coverage Ledger

| 审查问题 | 处置分类 | 建议计划 |
|---|---|---|
| `23-CONTEXT` 与 `STATE/REQUIREMENTS/RESIDUAL_LEDGER` 的 closeout 张力 | execute now | `23-CONTEXT` / `23-RESEARCH` addendum + `23-07` checklist |
| `23-01..03` 保留为历史完成记录，新增计划从 `23-04+` 起 | execute now | `23-CONTEXT` / `23-RESEARCH` |
| `fan.py` preset/options mismatch | execute now | `23-04` |
| `runtime_access.py` 的 `__dict__` 注入与 fallback 旁路 | execute now | `23-04` |
| 默认安装路径继续是 `ARCHIVE_TAG=latest` | locked constraint | `23-04` / `23-08` |
| `entities/base.py` 仍直打 coordinator command path | execute now | `23-05` |
| `snapshot.py` runtime compat normalization | execute now | `23-05` |
| runtime snapshot / developer report 双套投影 | execute now | `23-05` / `23-06` |
| gateway / IR / panel / mesh 诊断 sidecar | phase-local defer allowed | `23-05` follow-up boundary |
| `service_router.py` hotspot | execute now | `23-06` |
| `developer_report.py` / `coordinator.py` / `api/client.py` hotspot | execute now | `23-06` |
| `control` 与 `services` 双向耦合 | execute now | `23-06` |
| broad `except Exception` 高价值收窄 | execute now | `23-05` / `23-06` checklist |
| `.planning/codebase/TESTING.md` 统计漂移 | execute now | `23-07` |
| `scripts/check_architecture_policy.py` 依赖 `tests.helpers` | execute now | `23-07` |
| `scripts/export_ai_debug_evidence_pack.py` 依赖 `tests.harness` | execute now | `23-07` |
| wording guard brittleness | phase-local defer allowed | `23-07` + defer ledger |
| giant tests / coordinator 私有内部耦合 | phase-local defer allowed | `23-07` + future phase |
| bug template / troubleshooting / developer-report 口径摩擦 | execute now | `23-08` |
| contributor-facing evidence path 不清晰 | execute now | `23-08` |
| release 只有 zip + `SHA256SUMS`，缺更完整证据故事 | execute now | `23-08` |
| provenance / SBOM / signing / code scanning 全量落地 | future phase | `23-08` defer ledger |
| 单维护者 bus factor / maintainer model | future phase | `23-08` defer ledger |
| `firmware_support_manifest.json` metadata / signing 深化 | phase-local defer allowed | `23-08` defer ledger |
