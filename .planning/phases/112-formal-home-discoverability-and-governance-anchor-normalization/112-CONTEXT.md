# Phase 112: Formal-home discoverability and governance-anchor normalization - Context

**Gathered:** 2026-03-31
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段只处理 `formal-home discoverability` 与 `governance-anchor normalization`：
- 让 maintainer 在 north-star / developer docs / planning / baseline / runbook 中看到同一条当前主线故事；
- 明确根级 formal homes（尤其是 `runtime_infra.py`、`runtime_types.py`、`entry_auth.py`）的 sanctioned ownership；
- 清理仍停留在 archived-only 时代的 stale milestone / default-next / route-truth anchors；
- 维持 public-first docs 与 maintainer-only appendix 的边界，不让 support/security/public docs 回流成第二条 internal route ledger。

本阶段**不**处理：
- `Phase 111` 已关闭的 entity/control → runtime concrete bypass；
- 大范围 hotspot burn-down、模块继续 inward split 或大型重命名（留给 `Phase 113`）；
- public reachability、security fallback、delegate identity 的现实闭环（留给 `Phase 114`）；
- 为了“更整齐”而创造新的根目录真源、compat shell 或 second root。

</domain>

<decisions>
## Implementation Decisions

### Formal-home ownership
- **D-01:** `custom_components/lipro/runtime_infra.py`、`custom_components/lipro/runtime_types.py`、`custom_components/lipro/entry_auth.py` 在 `Phase 112` 默认按 **sanctioned root-level formal homes** 明确登记；本阶段优先做 ownership/discoverability normalization，而不是立刻做物理迁移。
- **D-02:** 若这些 root-level homes 只是 outward formal home + inward helper split 的结果，文档必须解释“为什么它们保留在根级”；不得让目录拓扑看起来像 accidental leftovers。
- **D-03:** 除非发现纯 alias / compat shell / second-root 痕迹，否则 `Phase 112` 不做高风险文件搬迁；若 discoverability 仍不足，再把 code-side rename/move 作为 `Phase 113` follow-up。

### Governance-anchor normalization
- **D-04:** `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 是 **live active-route selector**；`.planning/MILESTONES.md` 只保留 archive chronology，不承担当前 phase selector。
- **D-05:** `docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.planning/baseline/VERIFICATION_MATRIX.md` 以及相关 governance docs 必须同步承认 `v1.31 active route / latest archived baseline = v1.30`，清理 stale `no active milestone route` / `$gsd-new-milestone` 叙事。
- **D-06:** 本阶段优先统一 **current route truth、latest archived pointer、default next command、formal-home wording** 四类锚点；不要扩写无关路线史料。

### Public vs maintainer docs boundary
- **D-07:** `SUPPORT.md`、`SECURITY.md`、`docs/README.md`、`README.md`、`README_zh.md` 继续保持 **public-first / honest-by-default**；它们可以引用 maintainer appendix，但不得承载 internal route ledger。
- **D-08:** maintainer continuity、custody、archived evidence pointer 与 release route truth 继续收敛到 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 planning/baseline docs；public docs 只讲 guaranteed first hop 与 honest caveats。

### Naming / discoverability wording
- **D-09:** 清理误导性表述，如 `coordinator.coordinator`、archived-only “current route” 词法、以及让 root-level homes 像 accidental leftovers 的文案。
- **D-10:** 命名与说明优先使用 plane/home 词汇：`runtime root`、`control-plane home`、`auth/bootstrap home`、`protocol root`、`support-only helper`；不要新增新的中间术语层。
- **D-11:** 优先复用已有 authoritative docs/tables 完成 discoverability，不新增第二份 formal-home registry 或 shadow authority file。

### the agent's Discretion
- 可决定 sanctioned-home mapping 最终落在 `docs/developer_architecture.md` 的哪个 section，或是否需要在 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` / `.planning/baseline/DEPENDENCY_MATRIX.md` 补一行交叉引用，只要 authority order 不分叉。
- 可决定 stale-anchor cleanup 采用“逐文档显式替换”还是“集中术语表 + 少量 cross-link”策略，只要 maintainer 读任一官方文档都不会再落到 archived-only story。
- 可决定是否为 `Phase 112` 增加 focused governance guards；但新增守卫必须验证 current-route truth / formal-home wording，而不是复制 prose-only 锁文案测试。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Route truth / planning authority
- `.planning/PROJECT.md` — 当前 `v1.31` active route、latest archived baseline 与 current follow-up target 的正式真源。
- `.planning/ROADMAP.md` — `Phase 112` 的目标、success criteria 与 phase sequencing。
- `.planning/REQUIREMENTS.md` — `ARC-29` / `GOV-72` 的正式 requirement truth。
- `.planning/STATE.md` — 当前 phase、progress、default next command 与 session continuity 真源。
- `.planning/MILESTONES.md` — archive chronology only；用于确认它**不**承担 live selector 角色。

### Architecture / formal-home authority
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — single mainline、formal homes、no second root / no compat shell comeback 的最高裁决。
- `docs/developer_architecture.md` — 当前 developer-facing home map、plane vocabulary 与 maintainer entrypoints；本阶段需清理 archived-only stale anchors。
- `.planning/baseline/ARCHITECTURE_POLICY.md` — formal-home / bypass / policy family 的 machine-checkable治理 companion。
- `.planning/baseline/DEPENDENCY_MATRIX.md` — plane-to-plane 依赖方向与 sanctioned home 语义。
- `.planning/baseline/VERIFICATION_MATRIX.md` — current route story、default next command、focused governance proof 的正式 acceptance truth。

### Public / maintainer documentation boundary
- `docs/README.md` — public docs-first entry map 与 maintainer appendix reachability boundary。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — maintainer-only release custody、archived evidence pointer、continuity truth 的正式 home。
- `SUPPORT.md` — public support routing 与 continuity wording；不得成为 second internal route ledger。
- `SECURITY.md` — security reporting / private disclosure truth；需与 support / runbook 保持 honest boundary。
- `README.md` — public first hop；不得回流 maintainer continuity 与 internal route truth。
- `README_zh.md` — 中文 public first hop；必须与 `README.md` 保持等价导航边界。

### Root-level homes under review
- `custom_components/lipro/runtime_infra.py` — shared runtime infrastructure outward home；device-registry listener / runtime infra ownership 当前落点。
- `custom_components/lipro/runtime_types.py` — shared runtime coordinator protocols；root-level typed contract home。
- `custom_components/lipro/entry_auth.py` — config-entry auth/bootstrap helper home；需澄清其为何作为根级 auth/bootstrap formal home 保留。
- `custom_components/lipro/control/runtime_access.py` — control-plane sanctioned runtime read surface；用于对照“哪些应在 control home，哪些不应回流 root helper”。

### Supporting context from prior phases
- `.planning/phases/111-entity-runtime-boundary-sealing-and-dependency-guard-hardening/111-CONTEXT.md` — 刚完成的 runtime-boundary sealing 决策；`Phase 112` 不得回退其闭环。
- `.planning/phases/111-entity-runtime-boundary-sealing-and-dependency-guard-hardening/111-VERIFICATION.md` — `Phase 111` 已完成证据。
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-CONTEXT.md` — root-level helper / public-doc honesty 的旧裁决，供本阶段复用而不是重造。
- `.planning/phases/72-runtime-bootstrap-convergence-lifecycle-orchestration-and-runtime-access-probe-retirement/72-CONTEXT.md` — runtime bootstrap / runtime-access home map 的 predecessor context。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `custom_components/lipro/runtime_infra.py`：已经自带“outward formal home / inward helper split”说明，可直接作为 sanctioned-home discoverability 的样板。
- `custom_components/lipro/runtime_types.py`：已承担 shared runtime protocol truth，适合在 docs 中被明确登记为 root-level typed contract home。
- `custom_components/lipro/entry_auth.py`：已集中 config-entry auth/bootstrap seed、token persistence、setup exceptions；适合被解释为 auth/bootstrap formal home，而不是 accidental helper。
- `docs/README.md`：已经把 public fast path、maintainer appendix、bilingual boundary 拆得很清楚，可直接复用其 public-vs-maintainer boundary 语义。

### Established Patterns
- active route truth 现已固定在 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`；`MILESTONES.md` 是 archive chronology。
- public-first docs 与 maintainer appendix 已有明确边界：`docs/README.md` / `SUPPORT.md` / `SECURITY.md` 面向外部，`docs/MAINTAINER_RELEASE_RUNBOOK.md` 面向维护者。
- 代码层已偏好“formal outward home + support-only helper sibling”；`Phase 112` 应解释这个模式，而不是新增 registry 或 second root。

### Integration Points
- 预计会触碰 `docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`SUPPORT.md`、`SECURITY.md`、可能的 `docs/README.md` 交叉引用。
- planning/baseline 侧预计会触碰 `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/baseline/VERIFICATION_MATRIX.md`，必要时补 `.planning/baseline/DEPENDENCY_MATRIX.md` / `.planning/baseline/AUTHORITY_MATRIX.md` 的 wording。
- governance assurance 侧预计会触碰 `tests/meta/governance_current_truth.py`、`tests/meta/test_governance_route_handoff_smoke.py`、相关 docs/governance focused guards。

</code_context>

<specifics>
## Specific Ideas

- “把 `runtime_infra.py` / `runtime_types.py` / `entry_auth.py` 明确成 sanctioned homes，不急着挪文件。”
- “让 `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 停止讲 archived-only current story。”
- “public first hop 继续留在 `docs/README.md` / `SUPPORT.md` / `SECURITY.md`，不要把 active route truth 再塞回外部入口。”
- “先修 wording / ownership / anchor truth；若 docs 仍解释不清，再把 code-side relocation 留到 follow-up phase。”

</specifics>

<deferred>
## Deferred Ideas

- 若 `runtime_infra.py` / `runtime_types.py` / `entry_auth.py` 在 docs normalization 后仍显得像 accidental leftovers，则把物理迁移 / 更激进的 file rename 留到 `Phase 113`。
- top-priority implementation hotspot 的继续 inward split 与 no-regrowth guards 属于 `Phase 113`。
- public reachability、security fallback、delegate identity、backup maintainer 现实授权仍属于 `Phase 114` / `GOV-73` / `OSS-15` follow-up。
- 不在本阶段新增 public endpoint、mirror、delegate story 或 emergency fallback 叙事。

</deferred>

---

*Phase: 112-formal-home-discoverability-and-governance-anchor-normalization*
*Context gathered: 2026-03-31*
