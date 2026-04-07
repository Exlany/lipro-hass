# Phase 28 Verification

status: passed

## Goal

- 核验 `Phase 28: release trust gate completion and maintainer resilience` 是否完成 `GOV-22` / `QLT-04`：把 release trust chain 从“诚实记录”推进到 machine-verifiable release identity + tagged release security gate，同时把 maintainer continuity / support lifecycle 收敛成可执行、可审计的治理 bundle。
- 终审结论：**`GOV-22` 与 `QLT-04` 已在 2026-03-17 完成；仓库现在以 tagged release security gate、artifact attestation verification、release identity manifest 与 explicit continuity procedure bundle 形成单一正式 story。**

## Reviewed Assets

- Phase 资产：`28-CONTEXT.md`、`28-RESEARCH.md`、`28-VALIDATION.md`
- 已生成 summaries：`28-01-SUMMARY.md`、`28-02-SUMMARY.md`、`28-03-SUMMARY.md`
- synced truth：`.github/workflows/{ci.yml,release.yml}`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`README.md`、`README_zh.md`、`SUPPORT.md`、`SECURITY.md`、`CONTRIBUTING.md`、`.github/CODEOWNERS`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`tests/meta/{test_governance_guards.py,test_governance_closeout_guards.py,test_toolchain_truth.py,test_version_sync.py}`

## Must-Haves

- **1. Hardened release identity without a second release story — PASS**
  - tagged source release workflow 现要求 `security_gate`、artifact attestation verification 与 release identity manifest。
  - 所有 hardening 仍 anchored 在 `ci.yml -> release.yml` 单链，没有并行发版故事线。

- **2. Repo-visible blocking release security posture — PASS**
  - blocking runtime `pip-audit` 既在常规 CI，也在 tagged release 上被显式执行。
  - `code scanning` 继续被登记为 defer，而不是被冒充成已 blocking 的现状。

- **3. Executable maintainer continuity and support lifecycle truth — PASS**
  - public docs、support/security policy、CODEOWNERS 与 maintainer runbook 对 triage owner、release custody、freeze posture、best-effort boundary 讲同一条故事。
  - `GOV-22` / `QLT-04` 已从 seeded 状态升为 complete，并被 closeout guard 冻结。

## Evidence

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py -k "release or attestation or provenance or signing"` → `4 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py -k "runbook or release"` → `4 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py -k "security or code or scanning or release"` → `7 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -k "security or contributor or runbook"` → `6 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py -k "maintainer or support or security or codeowners"` → `5 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -k "readme or support or security or contributor"` → `8 passed`
- `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_guards.py` → `43 passed`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` → `78 passed`
- `uv run ruff check tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` → `All checks passed!`
- `node /home/claudeuser/.codex/get-shit-done/bin/gsd-tools.cjs verify phase-completeness 28` → `complete: true`, `summary_count: 3`, `errors: []`

## Risks / Notes

- 本 phase 没有虚构第二维护者；continuity posture 只把真实单维护者约束写成可执行 procedure bundle。
- signing 与 hard `code scanning` 仍是显式 defer，不得被未来 wording 漂移改写成“已完成”。
- 下一阶段应回到 `LiproRestFacade` hotspot slimming，而不是在 release governance 侧继续堆叠第二故事线。
