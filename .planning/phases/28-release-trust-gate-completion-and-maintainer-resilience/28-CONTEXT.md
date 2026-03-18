# Phase 28 Context

**Phase:** `28 Release trust gate completion and maintainer resilience`
**Milestone:** `v1.3 Quality-10 Remediation & Productization`
**Date:** `2026-03-17`
**Status:** `planned — ready for execution`
**Source:** `ROADMAP` / `REQUIREMENTS` / `STATE` / `v1.3-HANDOFF` / `v1.3-MILESTONE-AUDIT` + current release/public-governance truth

## Why Phase 28 Exists

`Phase 26` 已把 release asset、SBOM、artifact attestation、支持入口与 installer 默认故事线拉到更成熟的开源姿态，但按“顶级价格、质量 10 分”标准，仍存在两类未闭环的 retained debt：

1. **release identity / hard gate 仍偏软**：当前 release workflow 已发布 zip、installer、`SHA256SUMS`、SBOM 与 GitHub artifact attestation，但更硬的 signing / code-scanning release gate / required preflight posture 仍未被制度化为一致的 hard gate。
2. **maintainer continuity 仍停留在诚实说明层**：`SUPPORT.md`、`SECURITY.md`、`CONTRIBUTING.md` 与 runbook 已诚实记录单维护者现实，但 emergency access、release custody、support window / EOL / triage ownership 还没有形成更制度化、可审计、可演练的 continuity bundle。

## Goal

1. 把 release posture 从“有 provenance 证据”推进到“有更硬 identity / scanning / release-entry gate”的机器化故事线。
2. 把 maintainer continuity、emergency access、release custody、triage ownership 与 support/EOL posture 从口头或文档说明升级成结构化、可检查的治理资产。
3. 让 public docs、release workflow、runbook、CODEOWNERS 与 meta guards 对上述 posture 讲同一条故事，不制造虚假成熟度。

## Decisions (Locked)

- 本 phase **不得虚构第二维护者**；若 backup maintainer / delegate 尚不存在，只能建立制度化 continuity 资产、交接流程、紧急访问与显式风险说明。
- 本 phase 只处理 `GOV-22` / `QLT-04`；不得顺手吞入 `Phase 29` 的 REST hotspot / mega-test topicization，也不得偷跑 `Phase 30/31` 的 typed hardening。
- release identity hardening 必须沿现有 `.github/workflows/ci.yml` + `.github/workflows/release.yml` 正式发布主链推进；不得旁路既有 CI 另起第二条发布通道。
- maintainer continuity 文档必须是**真实可执行**的运行资产：owner、触发条件、恢复路径、冻结条件、回滚条件、证据位置都要明确。
- 若选择 signing / scanning gate，必须优先使用现有平台能力与现有仓库真相，不为“看起来更强”引入第二套身份/发布故事线。

## Non-Negotiable Constraints

- 不得改写 `Phase 26` 已收口的“verified release assets 是默认支持安装路径”这一公开事实。
- 不得把单维护者现实包装成“已经具备冗余”或“已有轮值团队”。
- 不得为了 continuity 文档化而引入未实际存在的凭据、人员、支持承诺或 SLA。
- 不得破坏 `LiproProtocolFacade` / `Coordinator` 单一正式主链；本 phase 仅涉及 release / governance / public-support surfaces。

## Canonical References

- `.planning/ROADMAP.md` — `Phase 28` goal / success criteria / sequencing
- `.planning/REQUIREMENTS.md` — `GOV-22`, `QLT-04`
- `.planning/STATE.md` — 当前活跃 continuation 与 next-focus 真相
- `.planning/v1.3-HANDOFF.md` — retained debt、continuation 守则、validation expectations
- `.planning/v1.3-MILESTONE-AUDIT.md` — retained debt verdict 与 recommended route
- `.github/workflows/release.yml` — release identity / build / publish 主链
- `.github/workflows/ci.yml` — release reuse 的 upstream gate
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — maintainer-only release / incident / post-release checks
- `README.md` / `README_zh.md` — 对外安装与支持叙事
- `SUPPORT.md` / `SECURITY.md` / `CONTRIBUTING.md` / `.github/CODEOWNERS` — support lifecycle、security disclosure、triage ownership、maintainer truth

## Specifics To Lock During Planning

- `release.yml` 是否需要显式失败于 code-scanning / security gate 缺失，而不是只复用一般 CI
- `runbook` 是否需要新增 release freeze、credential recovery、emergency handoff、bad-tag follow-up 与 delegate review checklist
- `SUPPORT` / `SECURITY` / `CONTRIBUTING` / `CODEOWNERS` 是否需要引入更结构化的 ownership / escalation / response-truth wording
- meta guards 是否需要新增对 continuity wording、release hard-gate assets、runbook required sections 的结构化校验

## Expected Plan Shape

最优应为 `3-4 plans`：

1. release workflow / gate hardening
2. maintainer continuity / incident / custody assetization
3. public docs / ownership / support-lifecycle truth sync
4. phase closeout / guards / evidence freeze（如有必要）
