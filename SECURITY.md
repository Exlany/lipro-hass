# Security Policy / 安全策略

## Supported Versions / 支持范围

| Version | Status |
| --- | --- |
| Latest tagged release / 最新标签版本 | Supported / 支持 |
| Current HACS install matching latest tag / 与最新标签一致的 HACS 安装 | Supported / 支持 |
| Older tagged releases / 较早标签版本 | Best effort only / 尽力而为 |
| `main` / preview installer path | Best effort only / 尽力而为，不承诺稳定支持 |

The contributor guides and public troubleshooting paths assume a minimum supported Home Assistant version of `2026.3.1`.
贡献文档与公开排障路径统一以 `2026.3.1` 作为最低支持的 Home Assistant 版本口径。

The canonical source is the `homeassistant==2026.3.1` pin in `pyproject.toml`.
唯一真源是 `pyproject.toml` 中的 `homeassistant==2026.3.1`。

The runtime dependency envelope is declared in `pyproject.toml` (full runtime floor/bounds) plus `custom_components/lipro/manifest.json` (Home Assistant-installed subset).
运行时依赖边界以 `pyproject.toml`（完整 runtime floor/bounds）和 `custom_components/lipro/manifest.json`（Home Assistant 安装子集）共同为准。

Supported shell/manual installs should start from verified GitHub Release assets (`install.sh` + release zip + `SHA256SUMS`). Preview paths such as `ARCHIVE_TAG=main`, branch fallback, or mirror installs are best effort only.
默认支持的 shell / 手动安装路径应从经过校验的 GitHub Release 资产（`install.sh` + release zip + `SHA256SUMS`）开始；`ARCHIVE_TAG=main`、branch fallback 与 mirror 安装仅属于尽力而为的预览路径。

Current release trust evidence includes published `SHA256SUMS`, `SBOM`, GitHub artifact `attestation` / `provenance`, keyless `cosign` signature bundles, the tagged runtime `pip-audit` gate, and a fail-closed tagged `CodeQL` gate. Artifact attestation / provenance is still release-identity evidence; `cosign` bundles are the artifact-signing layer.
当前 release trust 证据包括已发布的 `SHA256SUMS`、`SBOM`、GitHub artifact `attestation` / `provenance`、keyless `cosign` 签名 bundle、tagged runtime `pip-audit` 门禁，以及 fail-closed 的 tagged `CodeQL` 门禁。Artifact attestation / provenance 仍属于 release identity 证据；`cosign` bundle 才是 artifact signing 这一层。

If a tagged `CodeQL` analysis is missing, open alerts remain, or signature verification fails, the release must block rather than silently downgrade to a softer trust posture.
若缺少 tagged `CodeQL` analysis、仍存在 open alerts，或签名校验失败，则 release 必须阻断，而不是静默降级为更弱的 trust posture。

For private repositories or forks, CI skips HACS validation because HACS only supports public GitHub repositories.
若仓库或 fork 为私有，CI 会跳过 HACS validation，因为 HACS 只支持公开 GitHub 仓库。

This repository currently follows a single-maintainer security review model; acknowledgement and remediation timing are therefore best effort. No documented delegate or backup maintainer exists today in `.github/CODEOWNERS`.
本仓库当前采用单维护者安全审查模式，因此确认与修复节奏均为 best effort；`.github/CODEOWNERS` 中当前没有已文档化的 delegate 或备用维护者。

If your report is not security-sensitive, use `docs/TROUBLESHOOTING.md` and `SUPPORT.md` instead of the private disclosure path.
若问题并非安全敏感，请优先使用 `docs/TROUBLESHOOTING.md` 与 `SUPPORT.md`，不要占用私密披露通道。

## Triage / Continuity Truth / 分流与连续性真相

- Security triage owner: the maintainer listed in `.github/CODEOWNERS`.
- Documented delegate: none currently; do not imply hidden backup maintainers or unpublished emergency access.
- Release custody remains centralized; if the maintainer is unavailable, freeze new tagged releases and new release promises, keep the private advisory path plus best-effort support intake active, and do not bypass CI / security gates.
- Custody restoration: update `.github/CODEOWNERS` and `docs/MAINTAINER_RELEASE_RUNBOOK.md` before resuming tagged releases under a new custodian or real delegate.
- Best effort does **not** mean silent defer: unresolved high-risk issues must still be recorded explicitly.

- 安全分流 owner：`.github/CODEOWNERS` 中列出的维护者。
- 当前没有已记录的 delegate；不要暗示存在隐藏的备用维护者或未公开的紧急访问。
- 发版 custody 仍集中在当前单维护者模型；若维护者不可用，应冻结新的 tagged release 与 release 承诺，保持私密 advisory 路径与 best-effort support intake 可用，并且不要绕过 CI / security gate。
- custody 恢复条件：只有在 `.github/CODEOWNERS` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 先记录新的 custodian 或真实 delegate 后，才可恢复 tagged release。
- best effort **不等于** silent defer：未解决的高风险问题仍必须显式登记。

## Reporting a Vulnerability / 漏洞报告

Please do **not** open a public GitHub issue for security vulnerabilities.
安全漏洞请**不要**直接提交公开 GitHub Issue。

- Preferred private path / 首选私密路径：`https://github.com/Exlany/lipro-hass/security/advisories/new`
- Policy landing page / 安全策略入口：`https://github.com/Exlany/lipro-hass/security/policy`
- Include / 请附带：integration version、Home Assistant version、reproduction steps、impact assessment、redacted logs

## Private Disclosure Process / 私密披露流程

1. Use GitHub private vulnerability reporting before any public disclosure.
   在任何公开披露之前，先使用 GitHub 私密漏洞上报。
2. Give maintainers time to reproduce, mitigate, and prepare a coordinated release.
   给维护者留出复现、缓解与协调发版的时间。
3. Release handling must still reuse the normal CI gate plus the tagged release security gate; see `docs/MAINTAINER_RELEASE_RUNBOOK.md` for the maintainer-side flow.
   发版处理仍必须复用常规 CI 门禁与 tagged release security gate；维护者侧流程见 `docs/MAINTAINER_RELEASE_RUNBOOK.md`。
4. After a fix is ready, coordinate public disclosure and changelog notes.
   修复准备完成后，再协调公开披露与变更说明。

## Response Expectations / 响应预期

- Initial acknowledgement target: within 7 days / 初始确认目标：7 天内
- Status updates target: every 14 days while remediation is active / 修复期间尽量每 14 天更新一次状态
