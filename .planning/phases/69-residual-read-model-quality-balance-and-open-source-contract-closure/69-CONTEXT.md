# Phase 69: Residual read-model closure, wrapper-path thinning, and quality-balance follow-through - Context

Date: 2026-03-24
Mode: Active current milestone route for `v1.17`

## Phase Boundary

本 phase 只处理 `Phase 68` 终审中明确保留的 non-blocking residual，不重开 `v1.16` 已完成的 hotspot/docs closeout，也不再做一轮新的 full-repository audit。目标是继续把少数“正确但仍偏厚/偏绕/偏不平衡”的 seam 压向更窄、更诚实的正式结构。

In scope:
- `runtime_access_support.py` / `runtime_infra.py` 的 read-model/support seam formalization
- schedule/service path 与 protocol-service / wrapper chain 的继续去协议化
- wrapper/shim/lazy-import / helper mirror / discoverability residue 的继续清理
- `scripts/check_*.py` coverage 可见性、focused integration depth、meta-shell maintainability 的平衡补强
- release-aware docs URL、machine-readable HA support truth、maintainer continuity wording 的 honest contract 对齐

Out of scope:
- 重开 `Phase 68` 已验证通过的 hotspot/docs closeout
- 大范围 public API 重命名或“为了更漂亮”而重构整个 protocol stack
- 虚构 delegate / maintainer team / release-doc hosting reality 来粉饰单维护者现实
- 在没有充分收益的情况下引入新的 facade/root/helper family

## Implementation Decisions

### Locked Decisions

1. `custom_components/lipro/control/runtime_access.py` 继续是唯一 control-plane runtime outward home；`runtime_access_support.py` 只能 inward formalization，不能长回第二 root。
2. schedule public/service path 必须继续把 protocol-shaped parameter choreography 往下压；不允许为“收口”新建第二条 schedule/service story。
3. `custom_components/lipro/core/protocol/boundary/*` 继续是协议 decode authority；MQTT/API wrapper residue 的处理只能 thin inward，不得把 decode/auth/service truth 重新拉回 helper shell。
4. 质量补强必须增加 behavior/integration/checker coverage，而不是只添加更多 prose-coupled meta/budget tests。
5. 开源治理只能讲 honest contract：允许明确记录 live-docs on `main`、machine-readable constraints 的不足与单维护者现实，但不允许虚构组织承诺。
6. `v1.16` 保持 closeout-ready baseline 身份；本 phase 只承接 residual，不回滚 `Phase 68` 的 current-story 完成态。

### the agent's Discretion

- 允许决定 `runtime_access_support.py` 与 `runtime_infra.py` 的最优 inward split 粒度，但必须避免新增 public root。
- 允许决定是补齐 tag-aware docs strategy，还是把 live-docs on `main` 明确写成 honest contract；前提是所有对外入口讲同一条真话。
- 允许调整 focused tests / scripts tests / integration suites 的组合，但必须解释为什么新门禁比旧 meta-only 方案更平衡。

## Canonical References

### Governance / current-story truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — north-star plane/root/authority law
- `AGENTS.md` — repo execution contract and documentation sync rules
- `.planning/PROJECT.md` — active milestone + latest archived baseline story
- `.planning/ROADMAP.md` — milestone/phase routing and future phase definition
- `.planning/REQUIREMENTS.md` — residual requirement basket for `Phase 69`
- `.planning/STATE.md` — current active milestone is `v1.17`, and `Phase 69` is the active execution route

### Closeout baseline to build from
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-SUMMARY.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VERIFICATION.md`
- `.planning/phases/68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening/68-VALIDATION.md`
- `.planning/reviews/V1_16_EVIDENCE_INDEX.md`

### Residual hotspots and governance families
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/runtime_access_support.py`
- `custom_components/lipro/runtime_infra.py`
- `custom_components/lipro/services/schedule.py`
- `custom_components/lipro/core/coordinator/services/protocol_service.py`
- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/endpoint_surface.py`
- `custom_components/lipro/core/mqtt/message_processor.py`
- `custom_components/lipro/core/mqtt/payload.py`
- `custom_components/lipro/core/mqtt/topics.py`
- `.github/workflows/ci.yml`
- `scripts/coverage_diff.py`
- `scripts/check_architecture_policy.py`
- `scripts/check_file_matrix.py`
- `scripts/check_translations.py`
- `pyproject.toml`
- `custom_components/lipro/manifest.json`
- `docs/README.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/CODEOWNERS`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`

## Specific Ideas

- 把 `runtime_access_support.py` 中 entry/coordinator/device lookup 与 telemetry projection 继续切成更诚实的 typed/read-model support，而不是维持“显式反射探测大集合”。
- 让 `services/schedule.py` 停止承担 protocol parameter compiler；mesh/device-type/protocol detail 应进一步下压。
- 收敛 `client.py` / `endpoint_surface.py` / `protocol_service.py` / MQTT shim 的 stable-import 与 wrapper residue，至少明确哪些是正式 outward home、哪些只是 localized helper。
- 给 `scripts/check_*.py` 增加更直接的行为测试/coverage 约束，并补更多 focused integration/regression，避免 residual phase 继续依赖 meta budget assertions。
- 统一 release/docs/support/security/manifest/pyproject 的 honest public contract：要么 tag-aware，要么明确 live-docs on `main`；同时收口 HA support truth 与 maintainer continuity wording。

## Deferred Ideas

- `v1.16` 的 milestone archive / complete 流程本身
- 全仓统一重命名所有 historical stable-import homes
- 全面替换所有 meta budget tests；本 phase 只做平衡与补强，不做推倒重来
- 超出 residual family 的新功能、性能重写或 provider 扩展
