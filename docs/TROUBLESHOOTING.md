# Lipro Troubleshooting Guide

## Start Here

- Canonical minimum supported Home Assistant version: `2026.3.1` (install metadata: `hacs.json`; kept in sync with `pyproject.toml`).
- Continuity note / 连续性说明：support、security 与 release custody 仍是单维护者模型；当前没有已记录的 delegate。若维护者不可用，应 freeze new tagged releases 与 new release promises，同时保持 `SUPPORT.md` / `SECURITY.md` intake 有效，而不是假定存在隐藏冗余；只有当 `.github/CODEOWNERS` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 共同记录真实 successor / delegate 后，custody 才能恢复。
- Private repositories and forks skip CI HACS validation because HACS only supports public GitHub repositories.
- Security reports do **not** belong in public issues; follow `SECURITY.md` instead.
- Maintainer-facing release and packaging steps live in `docs/MAINTAINER_RELEASE_RUNBOOK.md`.
- Supported shell installs should use verified GitHub Release assets (`install.sh` + release zip + `SHA256SUMS`); `ARCHIVE_TAG=main` is preview-only. If `install.sh` runs in remote mode without a pinned archive/tag, it resolves the latest tagged release by default, but stable public guidance still prefers verified release assets.

## Before Opening an Issue

1. Confirm the integration version, Home Assistant version, and installation method.
2. Read `SUPPORT.md` to choose the right path for usage questions, bug reports, and security issues.
3. Enable debug logging and reproduce the problem once with fresh logs.
4. Download Home Assistant diagnostics for the Lipro config entry.
5. If diagnostics still do not explain the issue, or a maintainer asks for deeper debugging, enable debug mode and export `lipro.get_developer_report` or submit `lipro.submit_developer_feedback`.

```yaml
logger:
  default: info
  logs:
    custom_components.lipro: debug
```

## Quick Checks

### Authentication Failed

- Verify the phone number, password, and region in the Lipro app first.
- If the password changed, use reconfigure/update credentials instead of removing the integration.
- When reauth keeps failing, attach diagnostics first; add the redacted developer report only when diagnostics still do not explain the failure or when a maintainer asks for it.
- If available, include `failure_summary` / `failure_entries` from diagnostics, system health, or developer-report exports.

### Devices Not Discovered

- Confirm the device already exists in the Lipro app.
- Reload the integration or run `lipro.refresh_devices` after adding hardware.
- Gateway devices are bridges only; they do not become Home Assistant entities by themselves.

### State Not Updating / MQTT Looks Stale

- MQTT push is best effort; polling still acts as the safety net.
- Check whether the device works in the Lipro app and whether the integration is still authenticated.
- If state drift persists, include diagnostics and note whether the issue is cloud polling, MQTT push, or a Home Assistant entity projection problem.
- If the affected path exposes `failure_summary` or aggregated `failure_entries`, include those fields in the issue as well.

### OTA / Firmware Update Questions

- Certified firmware truth comes from the bundled local trust-root asset `custom_components/lipro/firmware_support_manifest.json` (historical filename retained).
- Update entities may surface uncertified firmware, but uncertified installs require explicit confirmation.
- If OTA data looks wrong, include the firmware entity attributes first; add the developer report when diagnostics alone are not enough.

### Developer / Diagnostics Services

- These services are escalation paths after diagnostics, not hard prerequisites for every public bug report.
- `lipro.get_developer_report` keeps vendor diagnosis identifiers such as `iotName`, but anonymizes user-defined labels before upload when using `lipro.submit_developer_feedback`.
- If a report or diagnostics export already contains `failure_summary` / `failure_entries`, keep those fields intact when filing the issue; they are part of the shared failure vocabulary.
- `lipro.get_anonymous_share_report` is the safe preview path before anonymous sharing.
- If a developer service fails, mention the exact service name, arguments, and whether debug mode was enabled.

## What Is Safe to Share

- Home Assistant diagnostics exports are redacted automatically.
- Developer feedback uploads keep vendor/device diagnosis identifiers needed for support, but anonymize local labels such as room/panel/IR names.
- Never paste plaintext passwords, raw tokens, or private security findings into public issues.

## Escalation Paths

- Usage questions or expected-behavior clarification: `SUPPORT.md` and GitHub Discussions.
- Confirmed bugs or regressions: GitHub bug template plus diagnostics first; add developer report / one-click feedback when diagnostics are insufficient or a maintainer asks for deeper debugging.
- Security concerns: `SECURITY.md` private disclosure path.
- Maintainer-only release, tag, or packaging issues: `docs/MAINTAINER_RELEASE_RUNBOOK.md` (including `break-glass verify-only` / `non-publish rehearsal` verification drills).
