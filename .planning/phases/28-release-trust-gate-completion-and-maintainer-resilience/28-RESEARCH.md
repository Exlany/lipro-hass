# Phase 28 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Requirement:** `GOV-22`, `QLT-04`

## Executive Judgment

`Phase 28` 的核心不是再做一次 `Phase 26` 的文档润色，而是把 **release identity hard gate** 与 **maintainer continuity assets** 同时从“诚实说明”推进到“机器化 + 可审计 + 可演练”的正式姿态。

最优拆分是 `4 plans / 4 waves`：

1. `28-01`：收紧 release gate / security posture / required workflow truth
2. `28-02`：把 maintainer continuity / emergency access / release custody 写成真实 runbook 资产
3. `28-03`：统一 public docs / CODEOWNERS / support-lifecycle / triage ownership truth
4. `28-04`：冻结 phase closeout truth、meta guards 与 evidence

## Current Truth Snapshot

### 1. Release tail 已有 provenance，但 hard identity posture 仍未闭环

当前 `.github/workflows/release.yml` 已发布 zip、`install.sh`、`SHA256SUMS`、SBOM，并生成 GitHub artifact attestation；release 仍复用 `.github/workflows/ci.yml` 的上游门禁。这说明仓库已经有可信 release tail，但 hard signing / explicit release-only security preflight / code-scanning release gate 仍未被制度化为更强的 blocking contract。

### 2. Security checks 在 CI 里存在，但 release-specific gate story 仍偏隐式

`.github/workflows/ci.yml` 已运行 runtime `pip-audit`，dev audit 也是 documented advisory lane；然而 `Phase 28` 要解决的是“对 release identity posture 讲同一条故事”：release 是否需要额外 fail-fast security/preflight truth、runbook 是否明确要求这些 gate、public docs 是否与 maintainer-only path 对齐。

### 3. 单维护者现实已被诚实记录，但 continuity 仍不够制度化

`SUPPORT.md`、`SECURITY.md`、`.github/CODEOWNERS` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 都明确仓库当前是 single-maintainer model，backup maintainer 未建立。这是诚实的，但还不是 10 分姿态：缺少 emergency access、release custody、冻结条件、delegate/backup review、坏 tag 恢复、凭据恢复与 incident checklist 等结构化资产。

### 4. 支持窗口与 triage 路由已存在，但 ownership 粒度仍可增强

`SUPPORT.md` 已描述 supported versions / install paths / routing；`SECURITY.md` 已有 disclosure path 与响应目标；`CONTRIBUTING.md` 已把 release/security/tooling flow 讲清楚。但这些信息仍偏散，尚未形成“一眼可审计”的 continuity/ownership bundle。

## Recommended Contract

### A. Release hardening 必须沿既有 CI → release 主链推进

- 不允许旁路 `.github/workflows/ci.yml` 另起发布通道。
- 若增加更硬 gate，应优先使用仓库现有 security posture、GitHub release identity 能力与现有 runbook，而不是引入第二套身份基础设施。
- 最终公开叙事必须是：`CI gate` → `tag verification` → `release assets + SBOM + attestation` → `maintainer post-release checks`。

### B. Maintainer continuity 必须是“真实可执行资产”，不是装饰性文案

- 明确 single-maintainer reality 仍成立。
- 允许建立：emergency access checklist、release custody checklist、freeze / rollback conditions、delegate review placeholder、credential recovery path、bad-tag follow-up path。
- 不允许写出未实际存在的 backup maintainer 名单、值班承诺或 SLA。

### C. Public docs / runbook / ownership truth 必须一源一致

- `SUPPORT.md`、`SECURITY.md`、`CONTRIBUTING.md`、`.github/CODEOWNERS`、`README.md` / `README_zh.md`、runbook 必须对 supported installs、triage ownership、security routing、release custody 讲同一条故事。
- 若引入新的 continuity 术语或 hard-gate wording，必须同步 guard；否则又会回到人工记忆治理。

## Recommended Plan Structure

### Plan 28-01 — harden release gate posture and required security/release checks

**File focus:**
- `.github/workflows/release.yml`
- `.github/workflows/ci.yml`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_governance_closeout_guards.py`

### Plan 28-02 — institutionalize maintainer continuity and emergency/release custody assets

**File focus:**
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/CODEOWNERS`
- `tests/meta/test_governance_guards.py`

### Plan 28-03 — sync public ownership, support lifecycle, and contributor truth

**File focus:**
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/CODEOWNERS`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_version_sync.py`

### Plan 28-04 — close out governance truth and evidence

**File focus:**
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/28-release-trust-gate-completion-and-maintainer-resilience/28-VALIDATION.md`
- `.planning/phases/28-release-trust-gate-completion-and-maintainer-resilience/28-VERIFICATION.md`
- `tests/meta/test_governance_closeout_guards.py`

## Validation Architecture

### Targeted validation slices

- `uv run pytest -q tests/meta/test_governance_guards.py -k "release or support or security or codeowners or maintainer"`
- `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`
- `uv run ruff check tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py`

### High-risk truths that must be locked

- release 继续只走正式 `CI -> tag -> release tail` 主链，不产生第二条发版故事线
- hard gate / signing / scanning wording 必须与真实 workflow 能力一致，不能写成 aspirational fiction
- single-maintainer reality 继续明确存在，但 continuity assets 明显更可执行、更可审计
- public docs / runbook / CODEOWNERS / guards 对 release custody、support lifecycle、security routing 与 escalation 讲同一条故事
