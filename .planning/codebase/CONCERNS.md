# Codebase Concerns

> Snapshot: `2026-03-19`
> Freshness: governance + release + entrypoint audit for `README*` / `CONTRIBUTING.md` / `SECURITY.md` / `SUPPORT.md` / `.github/*` / `install.sh` / top-level Python & config entrypoints.
> Repository: `/var/tmp/coolvibe/worktrees/edf26778937a-/lipro-hass`
> Focus: `concerns + governance`
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱不得反向充当当前治理真源，且必须同步回写、标记为过时，或注明历史观察。

**Analysis Date:** 2026-03-19

## Tech Debt

**Governance truth is duplicated across many public entrypoints:**
- Issue: continuity / release / support / disclosure truth is manually synchronized across `README.md:366`, `README_zh.md:367`, `CONTRIBUTING.md:68`, `SUPPORT.md:30`, `SECURITY.md:39`, `docs/TROUBLESHOOTING.md:1`, `docs/MAINTAINER_RELEASE_RUNBOOK.md:1`, `.github/CODEOWNERS:1`, `.github/ISSUE_TEMPLATE/bug.yml:13`, and `.github/pull_request_template.md:1`.
- Impact: wording is honest, but every governance change becomes a many-file edit; drift tax and review surface are both high.
- Fix approach: establish one machine-readable governance registry or generated include source for supported versions, continuity truth, and release trust stack, then lint or render downstream docs from that source.

**Contributor on-ramp carries unusually heavy process context:**
- Issue: the authority chain spans `AGENTS.md:1`, `docs/README.md:20`, `.planning/PROJECT.md:1`, `.planning/baseline/AUTHORITY_MATRIX.md:1`, `.planning/reviews/FILE_MATRIX.md:1`, `scripts/check_architecture_policy.py:303`, and `scripts/check_file_matrix.py:797`.
- Impact: maintainers get strong guardrails, but outside contributors must learn repo-specific governance before safely editing docs, wiring, or release paths.
- Fix approach: keep maintainer truth in `.planning/*`, but add a thin contributor-facing governance index that explains the minimum required reading and the smallest passing command set.

**Release process is secure but GitHub-coupled:**
- Issue: `.github/workflows/release.yml:18`, `.github/workflows/release.yml:85`, `.github/workflows/release.yml:198`, `.github/workflows/release.yml:212`, `.github/workflows/release.yml:257`, and `.github/workflows/release.yml:297` tie release trust to GitHub Actions, CodeQL, dependency-graph SBOM export, artifact attestation, OIDC signing, and GitHub Release publishing.
- Impact: supply-chain posture is strong, but release continuity depends on GitHub service availability and repo permissions; there is no lighter fallback release story.
- Fix approach: document a break-glass verification-only path plus a non-publish rehearsal path that a future delegate can execute before custody transfer.

## Known Bugs

**Governance routing bug in public entrypoints:**
- Symptoms: Not detected in the audited scope; `README.md:374`, `SUPPORT.md:48`, `SECURITY.md:53`, `.github/ISSUE_TEMPLATE/config.yml:1`, and `.github/ISSUE_TEMPLATE/bug.yml:13` route users consistently.
- Files: `README.md:374`, `SUPPORT.md:48`, `SECURITY.md:53`, `.github/ISSUE_TEMPLATE/config.yml:1`, `.github/ISSUE_TEMPLATE/bug.yml:13`
- Trigger: Not applicable
- Workaround: Not applicable

## Security Considerations

**Runtime dependency auditing is blocking; dev-toolchain auditing is advisory only:**
- Risk: `.github/workflows/ci.yml:129` blocks runtime `pip-audit`, but `.github/workflows/ci.yml:132` runs dev-environment audit only on `schedule` / `workflow_dispatch` with `continue-on-error`; local `scripts/lint:41` also audits dev dependencies only when `PIP_AUDIT_INCLUDE_DEV=1` is set.
- Files: `.github/workflows/ci.yml:129`, `.github/workflows/ci.yml:132`, `scripts/lint:41`, `scripts/lint:63`, `CONTRIBUTING.md:104`, `CONTRIBUTING.md:148`
- Current mitigation: daily `Dependabot` in `.github/dependabot.yml:1`, scheduled advisory scans, and pinned GitHub Actions SHAs in `.github/workflows/ci.yml:28` and `.github/workflows/release.yml:39`.
- Recommendations: define an allowlist / denylist policy for dev CVEs, and fail PRs when a dev dependency crosses a severity threshold instead of relying only on scheduled advisory output.

**Preview installer path is intentionally less trusted than release assets:**
- Risk: `install.sh` still supports `ARCHIVE_TAG=main`, branch fallback, and mirror-backed download modes via `install.sh:349` and `install.sh:364`; these paths do not inherit the full tagged release trust stack.
- Files: `install.sh:349`, `install.sh:364`, `install.sh:423`, `README.md:112`, `README.md:122`, `SUPPORT.md:20`
- Current mitigation: supported path is local verified release assets only (`README.md:87`, `install.sh:413`); the installer performs checksum verification on release assets plus zip preflight / path traversal checks at `install.sh:128` and `install.sh:458`.
- Recommendations: keep preview modes opt-in, and consider requiring an explicit second environment flag for mirror-backed installs to make accidental trust downgrades harder.

**Single release custodian is itself a security continuity risk:**
- Risk: `.github/CODEOWNERS:1`, `SUPPORT.md:30`, `SECURITY.md:39`, `docs/MAINTAINER_RELEASE_RUNBOOK.md:64`, and `custom_components/lipro/manifest.json:4` all centralize triage and release custody to one maintainer.
- Files: `.github/CODEOWNERS:1`, `custom_components/lipro/manifest.json:4`, `SUPPORT.md:30`, `SECURITY.md:39`, `docs/MAINTAINER_RELEASE_RUNBOOK.md:64`
- Current mitigation: the docs are honest about freeze posture and forbid pretending there is a hidden delegate.
- Recommendations: add a real delegate, require that person to rehearse `workflow_dispatch` release verification, and record custody restoration steps in the same sources before any incident happens.

## Performance Bottlenecks

**Human change throughput is gated by a heavy validation contract:**
- Problem: contributor and PR contracts require `ruff`, `mypy`, translation truth, architecture policy, file matrix, governance meta-tests, full tests with `95%` coverage, refactor-tool checks, and sometimes `shellcheck` in `CONTRIBUTING.md:145`, `CONTRIBUTING.md:181`, `.github/pull_request_template.md:2`, `.github/workflows/ci.yml:61`, and `.github/workflows/ci.yml:175`.
- Files: `CONTRIBUTING.md:145`, `CONTRIBUTING.md:181`, `.github/pull_request_template.md:2`, `.github/workflows/ci.yml:61`, `.github/workflows/ci.yml:175`
- Cause: the repository treats governance truth as code, so docs / config / release changes trigger many blocking gates.
- Improvement path: preserve the strong default gate, but publish a smaller docs-only / governance-only / release-only local command matrix so outside contributors can validate the smallest sufficient subset first.

## Fragile Areas

**Public governance narrative must stay cross-file synchronized:**
- Files: `README.md:366`, `README_zh.md:367`, `CONTRIBUTING.md:68`, `SUPPORT.md:30`, `SECURITY.md:39`, `docs/TROUBLESHOOTING.md:1`, `docs/MAINTAINER_RELEASE_RUNBOOK.md:1`, `.github/ISSUE_TEMPLATE/bug.yml:13`, `.github/pull_request_template.md:1`
- Why fragile: the same continuity, support, release-trust, and supported-version truths appear in many human-facing files and are also asserted by `tests/meta/test_governance_release_contract.py:39`, `tests/meta/test_toolchain_truth.py:307`, and `tests/meta/test_version_sync.py:165`.
- Safe modification: edit all public entrypoints in one change, then rerun the governance meta suite plus the relevant doc-sync tests.
- Test coverage: strong on wording / route parity, weaker on contributor usability and maintenance overhead.

**Release trust stack is strong but operationally brittle:**
- Files: `.github/workflows/release.yml:27`, `.github/workflows/release.yml:68`, `.github/workflows/release.yml:136`, `.github/workflows/codeql.yml:1`, `docs/MAINTAINER_RELEASE_RUNBOOK.md:21`
- Why fragile: the release chain depends on CI reuse, tagged CodeQL readiness, GitHub SBOM export, attestation generation, cosign signing, and GitHub Release publishing without a simpler fallback path.
- Safe modification: change workflow steps and runbook together; keep tag-only checkout, version-match checks, and verification commands aligned.
- Test coverage: good for existence and contract wording in `tests/meta/test_governance_release_contract.py:39` and `tests/meta/test_toolchain_truth.py:123`, but no rehearsal path for a second custodian exists.

**Installer trust story spans docs + shell + tests:**
- Files: `install.sh:128`, `install.sh:413`, `README.md:87`, `README_zh.md:87`, `tests/meta/test_install_sh_guards.py:10`
- Why fragile: supported and unsupported install modes coexist in one script, so doc drift or flag creep could blur the trust boundary.
- Safe modification: keep release-asset install as the only supported path, and add tests whenever new download modes, flags, or checksum behaviors appear.
- Test coverage: minimal but targeted; only one dedicated meta guard exists for archive preflight and symlink defense.

## Scaling Limits

**Bus factor remains 1 at the governance / release layer:**
- Current capacity: `.github/CODEOWNERS:3` and `custom_components/lipro/manifest.json:4` name a single owner; `SUPPORT.md:32` and `SECURITY.md:42` explicitly say no documented delegate exists today.
- Limit: if that maintainer is unavailable, new tagged releases and new release promises must freeze as stated in `README.md:370`, `SUPPORT.md:36`, `SECURITY.md:43`, and `docs/MAINTAINER_RELEASE_RUNBOOK.md:70`.
- Scaling path: add at least one documented delegate, split triage / release / doc custody, and rehearse the runbook before the next release.

**Documentation parity does not scale cheaply:**
- Current capacity: every governance-sensitive change may need synchronized edits across `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `docs/TROUBLESHOOTING.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/*`, and `.planning/reviews/V1_2_EVIDENCE_INDEX.md` as required by `CONTRIBUTING.md:75` and `.github/pull_request_template.md:8`.
- Limit: review cost and drift probability rise faster than code size, especially for bilingual and release-security narrative changes.
- Scaling path: centralize shared facts, generate downstream excerpts where possible, and reserve manual prose only for audience-specific guidance.

## Dependencies at Risk

**GitHub-hosted security / release services are critical operational dependencies:**
- Risk: release publish requires reusable GitHub workflows, CodeQL results, GitHub dependency-graph SBOM export, artifact attestation, OIDC identity, and GitHub Release asset publish.
- Impact: release continuity is vulnerable to platform outages, permission loss, or repo admin access gaps even when the code itself is ready.
- Migration plan: document a non-publishing verification fallback and maintain local verification commands in `docs/MAINTAINER_RELEASE_RUNBOOK.md:87` and `README.md:99`.

**Vendor API reverse-engineering remains an upstream continuity risk:**
- Risk: `README.md:364` states the integration depends on a reverse-engineered Lipro cloud API, so upstream protocol drift can outpace volunteer maintenance.
- Impact: governance discipline reduces reaction time, but cannot eliminate upstream breakage or closed-vendor changes.
- Migration plan: keep replay fixtures and boundary authorities current in `tests/fixtures/**`, `tests/meta/test_external_boundary_authority.py:1`, and `tests/meta/test_protocol_replay_assets.py:1`, while continuing to isolate protocol normalization in `custom_components/lipro/core/protocol/`.

## Missing Critical Features

**No documented delegate or backup maintainer:**
- Problem: the repository has an honest freeze story, but not an actual succession path.
- Blocks: resilient release custody, faster security response, and lower bus-factor risk.
- Files: `.github/CODEOWNERS:1`, `SUPPORT.md:30`, `SECURITY.md:39`, `docs/MAINTAINER_RELEASE_RUNBOOK.md:64`, `README.md:366`

**No single machine-readable governance manifest for shared public truths:**
- Problem: supported-version, continuity, release-trust, and routing facts are repeated across prose documents and templates rather than generated from one canonical data source.
- Blocks: low-friction doc maintenance, simpler contributor onboarding, and safer governance edits.
- Files: `README.md:74`, `README_zh.md:72`, `CONTRIBUTING.md:14`, `SUPPORT.md:12`, `SECURITY.md:3`, `docs/TROUBLESHOOTING.md:3`, `.github/ISSUE_TEMPLATE/bug.yml:13`, `.github/pull_request_template.md:1`

## Test Coverage Gaps

**Unsupported installer paths are lightly covered relative to their risk:**
- What's not tested: mirror-backed installs, branch fallback behavior, and warning-to-enforcement boundaries for unsupported remote paths.
- Files: `install.sh:349`, `install.sh:450`, `tests/meta/test_install_sh_guards.py:10`
- Risk: trust-boundary regressions on preview paths could slip in without a dedicated guard.
- Priority: Medium

**Dev dependency security posture has policy prose, but little failure-driven regression coverage:**
- What's not tested: a repo-level rule that escalates specific dev-toolchain CVEs from advisory to blocking, or that prevents silent weakening of local dev-audit defaults.
- Files: `.github/workflows/ci.yml:132`, `scripts/lint:63`, `CONTRIBUTING.md:148`
- Risk: supply-chain debt can accumulate outside the blocking runtime lane.
- Priority: Medium

**Continuity process is documented, not exercised:**
- What's not tested: delegate onboarding, custody restoration rehearsal, or a break-glass release-verification drill.
- Files: `.github/CODEOWNERS:1`, `SUPPORT.md:30`, `SECURITY.md:39`, `docs/MAINTAINER_RELEASE_RUNBOOK.md:64`
- Risk: the first true continuity incident becomes the rehearsal.
- Priority: High

---

*Concerns audit: 2026-03-19*
