# Security Policy / 安全策略

## Supported Versions / 支持范围

| Version | Status |
| --- | --- |
| `main` | Supported / 支持 |
| Latest tagged release / 最新标签版本 | Supported / 支持 |

The contributor guides and public troubleshooting paths assume a minimum supported Home Assistant version of `2026.3.1`.
贡献文档与公开排障路径统一以 `2026.3.1` 作为最低支持的 Home Assistant 版本口径。

The canonical source is the `homeassistant==2026.3.1` pin in `pyproject.toml`.
唯一真源是 `pyproject.toml` 中的 `homeassistant==2026.3.1`。

For private repositories or forks, CI skips HACS validation because HACS only supports public GitHub repositories.
若仓库或 fork 为私有，CI 会跳过 HACS validation，因为 HACS 只支持公开 GitHub 仓库。

This repository currently follows a single-maintainer security review model; acknowledgement and remediation timing are therefore best effort.
本仓库当前采用单维护者安全审查模式，因此确认与修复节奏均为 best effort。

If your report is not security-sensitive, use `docs/TROUBLESHOOTING.md` and `SUPPORT.md` instead of the private disclosure path.
若问题并非安全敏感，请优先使用 `docs/TROUBLESHOOTING.md` 与 `SUPPORT.md`，不要占用私密披露通道。

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
3. Release handling must still reuse the normal CI gate; see `docs/MAINTAINER_RELEASE_RUNBOOK.md` for the maintainer-side flow.
   发版处理仍必须复用常规 CI 门禁；维护者侧流程见 `docs/MAINTAINER_RELEASE_RUNBOOK.md`。
4. After a fix is ready, coordinate public disclosure and changelog notes.
   修复准备完成后，再协调公开披露与变更说明。

## Response Expectations / 响应预期

- Initial acknowledgement target: within 7 days / 初始确认目标：7 天内
- Status updates target: every 14 days while remediation is active / 修复期间尽量每 14 天更新一次状态
