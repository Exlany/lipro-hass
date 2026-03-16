# Phase 23 Context

**Phase:** `23 Governance convergence, contributor docs and release evidence closure`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion`
**Date:** `2026-03-16`
**Status:** `Ready for replanning`
**Source:** `Phase 22` observability-contract closeout truth + current roadmap/requirements/state + v1.2 final-governance chain + 2026-03-16 full-repo audit requested by user

## Why Phase 23 Exists

原始 `Phase 23` 只要求把 `v1.2` 的最终治理、贡献者入口、release evidence 与 CI gate 讲成同一条故事；但本轮契约者明确要求：**基于终极审查报告，重新为 Phase 23 制定一份覆盖全仓改进项的完整修改计划与清单，确保不漏项**。

因此，本次 `gsd-plan-phase 23` 的目标不是回滚或否定既有 `23-01..03`，而是：

1. 保留既有 `23-01..03` 作为历史完成记录；
2. 在同一 phase 目录下追加一组**审查驱动的增量计划**；
3. 让新增计划既覆盖原始 `GOV-16/GOV-17`，也显式纳入本轮审查发现的 production / tests / governance / release / docs 问题；
4. 对暂不执行的事项，必须显式写成 defer / follow-up / later-wave checklist，而不是遗漏。

## Goal

1. 生成一组**增量 PLAN.md**，系统覆盖本轮全仓审查发现的全部关键问题，并按波次拆分为可执行任务。
2. 确保新增计划仍满足 `GOV-16` / `GOV-17`，同时把代码边界收口、测试治理修复、发布供应链改进、开源治理优化纳入统一故事线。
3. 形成一份**不漏项的审查整改清单**：每个审查问题都要么进入某个计划，要么被明确标注为后续 deferred item，并写明原因。
4. 明确保留用户体验裁决：**安装脚本与 README 中的默认安装姿势仍以 `latest` 为默认值，方便普通用户使用**；tag 固定安装仅作为“可复现 / 高级用法”保留，不得把默认路径改成固定 tag。

## Decisions (Locked)

### Planning Mode

- 本次采用 **add more plans** 模式，而不是覆盖/删除既有 `23-01..03`。
- 新增计划应从 `23-04` 开始编号，保持历史执行记录可追溯。
- 新计划必须显式注明：哪些是可直接执行的修复，哪些是 follow-up / later-wave / governance checklist。

### Coverage Rules

- 本轮审查报告中的所有问题都必须被归类：`execute now` / `phase-local defer` / `future phase` 三选一，不允许 silent drop。
- 新计划必须覆盖四大面向：
  1. production architecture / boundary tightening
  2. tests / scripts / governance drift repair
  3. contributor docs / support / release workflow / security posture
  4. audit checklist / residual arbitration / next-phase handoff
- 若某问题超出原始 `Phase 23` 的实现边界，可放入后续 wave 或 follow-up checklist，但必须写入计划产物。

### Installer / User Experience

- `install.sh` 与 README/README_zh 中的**默认**安装方式继续以 `ARCHIVE_TAG=latest` 作为主入口。
- tag 固定安装、`main` 安装、镜像安装仍需保留，并在文档中说明各自适用场景。
- 计划中如涉及 installer / docs 改动，必须避免把“默认 latest”改成“默认 pinned tag”。

### Architecture Guardrails

- 不得恢复第二套正式主链。
- 不得把 raw vendor payload 再穿透进 runtime / entity。
- 不得为图省事新增新的 compat shell / wrapper story。
- 对现存 compat / residual / fallback，只能继续收口，不能重新合法化。

## Audit-Derived Must-Cover Items

以下问题来自本轮主代理审查与并行子代理审查，新增计划必须全部覆盖或显式处置：

### A. Production / Architecture

- `custom_components/lipro/fan.py` preset / option contract 不一致（`gentle_wind`、vent `off`）。
- `custom_components/lipro/control/runtime_access.py` 通过修改 `__dict__` 伪造 runtime entry，并在 telemetry 缺失时回退读取 coordinator internals。
- `custom_components/lipro/entities/base.py` 仍直接调用 coordinator command path，未完全收敛到文档所述 `Entity -> Service -> Runtime` 叙事。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 仍在 runtime 里做 compat row normalization，应评估继续下沉到 protocol boundary。
- `custom_components/lipro/control/service_router.py`、`custom_components/lipro/core/utils/developer_report.py`、`custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/api/client.py` 仍是热点文件，需要拆分/减重计划。
- `control` 与 `services` 之间仍存在双向耦合，需要在计划中显式拆解路径。
- broad `except Exception` 在 coordinator / protocol / mqtt / control 等处仍偏多，需要纳入 typed-failure hardening checklist。

### B. Tests / Scripts / Governance Assets

- `.planning/codebase/TESTING.md` 统计数字已漂移，必须刷新派生图谱或建立刷新门禁。
- `scripts/check_architecture_policy.py` 依赖 `tests.helpers`，`scripts/export_ai_debug_evidence_pack.py` 依赖 `tests.harness`；需评估脚本独立性与 authority purity。
- 多个 meta/tests 仍偏字面文案守卫，需纳入“结构化 guard vs wording guard” 的后续收口清单。
- 超大测试文件与对 coordinator 私有内部的强耦合，应形成拆分/降耦计划。

### C. Docs / Open Source / Release

- release workflow 仍缺 provenance / SBOM / signature / code scanning 等现代供应链增强项。
- CODEOWNERS / SECURITY / SUPPORT / maintainer model 体现单维护者脆弱性，需规划治理加固，但不得强行承诺仓库当前没有的人力配置。
- bug template 与 `docs/TROUBLESHOOTING.md` 在“developer report 是否强制”口径上需重新对齐。
- `docs/README.md`、PR template、release runbook、evidence index 的对外导航与内部 `.planning/*` 暴露方式需重新仲裁。
- `custom_components/lipro/firmware_support_manifest.json` 缺 manifest-level metadata（schema/version/generated_at/source/signature 一类），需在计划中评估是否进入本 phase 或明确 defer。

## Non-Negotiable Constraints

- 既有 `23-01..03` 视为历史已完成资产，不得删除或重写成与当时真相冲突的内容。
- 新增计划必须在 phase 23 目录内产出，且编号连续、可供 `gsd-execute-phase` 消费。
- 计划必须显式标注哪些事项适合在本 phase 直接执行，哪些更适合作为 follow-up / future-phase checklist。
- 若某项超出单次执行的安全/复杂度预算，不得硬塞进一个巨计划里；应拆成可验证的小计划。
- 任何 installer/doc 方案都必须遵守：**默认 `latest`，高级场景再谈 pinned tag**。
- 不得为了迎合审查结论而破坏现有 north-star / baseline / review authority order。

## Specific Planning Expectations

- 优先把新增计划组织成若干波次，例如：
  - Wave 1：真实功能/边界缺口与低风险契约修复
  - Wave 2：热点减重与 control/services/runtime 收口
  - Wave 3：tests/scripts/governance asset repair
  - Wave 4：docs/release/security/open-source posture hardening
- 每个计划必须附 `files_modified` 候选集合、验证命令、must_haves，并能追溯回本轮审查项。
- 计划里应出现一份“审查问题覆盖表”或等价结构，证明没有漏项。

## Existing Plan Disposition

- `23-01..03`：保留，作为历史完成记录。
- 本轮 planner 应新增 `23-04+`，并在必要时引用 `23-01..03` 作为已完成前置条件或背景事实。
