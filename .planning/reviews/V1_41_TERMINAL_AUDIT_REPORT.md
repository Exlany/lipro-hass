# V1.41 Terminal Audit Report

**Status:** `current-route verdict / closeout-ready (2026-04-02)`
**Scope:** `repo-wide Python + tests + docs + governance + config terminal residual audit`
**Coverage note:** `本轮以正式真源、focused code reading、governance route contracts、meta guards 与 targeted suites 为依据；不是浅层 grep，而是对 hotspot / route / docs / tests / open-source surface 的系统性审查。`

## Executive Verdict

- `lipro-hass` 的正式架构方向已明显优于普通 Home Assistant 集成：formal-home、protocol/runtime/control/domain 分层清楚，且 docs-first governance 已能约束实现而不是事后解释实现。
- 当前主要问题不是“缺少架构”，而是 **热点仍厚、manual delegation 仍重、部分观测/日志策略仍未完全统一、治理派生产物维护成本偏高**。
- `Phase 136` 已完成 current-route 范围内的首批高价值收口：vendor MD5 compatibility helper 统一、outlet-power / coordinator lifecycle 局部日志占位符收敛、schedule service shared-execution contract 回归、`v1.41` current-route governance 全链同步。
- 这份报告的含义是：**v1.41 范围内已 closeout-ready**，不是宣称“所有历史 debt 已自然清零”。后续深层清扫必须沿 charter 继续推进。

## Strengths

- `custom_components/lipro/core/protocol/facade.py`、`custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/coordinator/coordinator.py` 共同维持了 single formal root / child-facade 叙事。
- `custom_components/lipro/core/utils/background_task_manager.py`、`custom_components/lipro/runtime_infra_device_registry.py`、`custom_components/lipro/core/api/schedule_service_support.py` 体现了较成熟的并发清理纪律与边界感。
- 生产代码未见广泛 `except Exception` / 裸 `except` 滥用；当前问题更偏向可维护性与策略一致性，而不是低级错误堆积。
- `.planning/*`、`docs/*` 与 `tests/meta/*` 形成了较强的“实现—文档—守卫”闭环，这对开源长期维护是加分项。

## Naming / Directory / Open-Source Review

### Naming

- 大多数正式 formal-home 命名是稳定且语义一致的，如 `LiproProtocolFacade`、`LiproRestFacade`、`CoordinatorAuthService`、`RuntimeAccess`。
- 仍需改进的区域主要集中在“过厚类名无法反映职责密度”而不是低质量命名本身：`custom_components/lipro/core/auth/manager.py`、`custom_components/lipro/core/device/device.py`、`custom_components/lipro/core/command/dispatch.py`。
- 结论：**命名质量总体合格，真正的问题是职责切分不足导致名称看似正确、实际承载过多。**

### Directory & Ownership

- 顶层目录结构总体清晰：`custom_components/lipro/` 承载正式实现，`tests/` 承载验证，`docs/` 承载开发者与发布叙事，`.planning/` 承载治理真源与执行痕迹。
- 主要维护成本不在目录“乱”，而在 `.planning/baseline/*`、`.planning/reviews/*`、`tests/meta/*` 之间的派生同步压力较高；当前已是 formal governance，但人工维护成本偏高。
- `custom_components/lipro/core/` 内部 formal home 基本清楚，但 `rest_facade` / `auth manager` / `device facade` 等热点仍因体积过大而降低导航效率。
- 结论：**目录结构可维护，但热点文件厚度与治理派生产物数量是当前 discoverability 的主要摩擦源。**

### Open-Source Readiness

- 优点：`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SECURITY.md`、`SUPPORT.md`、`.github/*` 已形成较完整的开源协作表层；公开仓库所需的基础文件并不缺席。
- 不足：当前开源叙事仍较依赖治理资产与仓库内部语言，外部贡献者第一次进入时仍需要较强 maintainer 解释；`.planning` 体系对内部一致性很强，但对新贡献者的渐进学习成本仍偏高。
- 结论：**开源 readiness 基础面良好，但 contributor onboarding 仍可继续压缩为更薄的 first-hop narrative。**

## Findings By Severity

### High

1. **mega-facade/manual rebinding residual** 仍是当前最明显的二阶复杂度来源。
   - `custom_components/lipro/core/api/rest_facade.py:210`
   - `custom_components/lipro/core/protocol/facade.py:168`
   - 结论：已不再是 mixin 聚合，但仍是 manual delegation wall；导航、review、重命名成本高。

2. **auth hotspot 仍过厚**。
   - `custom_components/lipro/core/auth/manager.py:224`
   - `custom_components/lipro/core/auth/manager.py:261`
   - `custom_components/lipro/core/auth/manager.py:345`
   - `custom_components/lipro/core/auth/manager.py:377`
   - 结论：凭据持有、token 生命周期、自适应 expiry、refresh dedupe、re-login fallback 仍聚在单类内。

### Medium

3. **device facade 发现性与维护成本偏高**。
   - `custom_components/lipro/core/device/device.py:21`
   - `custom_components/lipro/core/device/device.py:86`
   - 结论：约 69 个 property relay + 9 个 method relay，适合短期 outward stability，不适合长期继续膨胀。

4. **dispatch 仍带 stringly command residual**。
   - `custom_components/lipro/core/command/dispatch.py:126`
   - `custom_components/lipro/core/command/dispatch.py:137`
   - 结论：虽然已集中化，但仍依赖 command string / prefix 规则，而不是 typed command model。

5. **失败信息衰减 / observability residual**。
   - `custom_components/lipro/core/api/status_service.py:277`
   - 结论：`query_connect_status` 在 API 失败时返回空映射，调用侧不易区分“全离线”与“查询失败”。

6. **governance derivation cost 偏高**。
   - `.planning/baseline/VERIFICATION_MATRIX.md:1`
   - `.planning/reviews/PROMOTED_PHASE_ASSETS.md:1`
   - `tests/meta/governance_followup_route_current_milestones.py:1`
   - 结论：当前治理强度高，但 current-route、archive history、promoted assets、verification baseline 之间仍需要较多手工同步。

### Low / Now reduced

7. **vendor MD5 compatibility drift** 已在本轮收口。
   - 修复前：`custom_components/lipro/core/api/auth_service.py:118`、`custom_components/lipro/core/auth/manager.py:162`
   - 正式 helper：`custom_components/lipro/core/utils/vendor_crypto.py:8`

8. **raw exception logging drift** 已在本轮局部收口。
   - 修复点：`custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py:210`、`custom_components/lipro/core/coordinator/lifecycle.py:64`
   - 说明：schedule service 继续保持 shared execution contract 的薄封装；其他外围位置仍可在后续 phase 继续统一。

9. **test typing residual** 已在本轮 targeted suites 中清理干净。
   - 当前 `tests/core` / `tests/meta` 不再保留真实 `type: ignore` 注释；剩余命中仅存在于元测试对字面量字符串的守卫断言。

## Completed In V1.41 / Phase 136

- 新增终极审查 verdict home：`V1_41_TERMINAL_AUDIT_REPORT.md`
- 新增后续 workstream charter：`V1_41_REMEDIATION_CHARTER.md`
- 统一 `md5_compat_hexdigest` 使用于 auth manager / auth service
- 收敛 outlet-power / coordinator lifecycle 的局部日志占位符策略，并让 schedule service 保持 shared execution contract 薄封装
- 把 current-route 投影切到 `v1.41 active milestone route / starting from latest archived baseline = v1.40`

## Changed Files Mapped This Round

- **Production fixes:** `custom_components/lipro/core/api/auth_service.py`, `custom_components/lipro/core/auth/manager.py`, `custom_components/lipro/core/coordinator/lifecycle.py`, `custom_components/lipro/core/coordinator/runtime/outlet_power_runtime.py`, `custom_components/lipro/services/schedule.py`
- **Focused tests:** `tests/services/test_services_schedule.py`, `tests/core/test_outlet_power_runtime.py`, `tests/core/test_identity_index.py`, `tests/core/coordinator/runtime/test_status_runtime.py`, `tests/core/test_log_safety.py`, `tests/core/test_anonymous_share_cov_missing.py`
- **Governance/current-route sync:** `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/MILESTONES.md`, `.planning/baseline/GOVERNANCE_REGISTRY.json`, `.planning/baseline/VERIFICATION_MATRIX.md`, `tests/meta/governance_followup_route_current_milestones.py`, `tests/meta/governance_archive_history.py`, `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- **Developer-facing docs:** `docs/developer_architecture.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- **Phase assets / review homes:** `.planning/phases/136-repo-wide-terminal-residual-audit-and-remediation-charter/*`, `.planning/reviews/V1_41_TERMINAL_AUDIT_REPORT.md`, `.planning/reviews/V1_41_REMEDIATION_CHARTER.md`

## Deferred On Purpose

- `rest_facade` / `protocol facade` 的 deeper decomposition
- `LiproAuthManager` 的职责拆分
- `LiproDevice` facade 瘦身与 public projection strategy 细化
- typed command model 替代 stringly route grammar
- broader derived-governance automation / file-matrix regeneration
- observability residual 的后续语义化与日志策略统一
