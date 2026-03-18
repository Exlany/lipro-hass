# Phase 26 Verification

status: passed

## Goal

- 核验 `Phase 26: release trust chain and open-source productization hardening` 是否完成 `GOV-21` / `QLT-03`：让默认安装路径、release tail、support/security/contributor/product metadata 达到更成熟且更诚实的开源治理标准。
- 终审结论：**`GOV-21` 与 `QLT-03` 已在 2026-03-17 完成；verified release assets 现已成为默认支持安装链。**

## Reviewed Assets

- Phase 资产：`26-CONTEXT.md`、`26-RESEARCH.md`、`26-VALIDATION.md`
- 已生成 summaries：`26-01-SUMMARY.md`、`26-02-SUMMARY.md`、`26-03-SUMMARY.md`、`26-04-SUMMARY.md`
- synced truth：`install.sh`、`.github/workflows/release.yml`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`README.md`、`README_zh.md`、`docs/TROUBLESHOOTING.md`、`SUPPORT.md`、`SECURITY.md`、`CONTRIBUTING.md`、`pyproject.toml`、`.github/CODEOWNERS`、`custom_components/lipro/manifest.json`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`

## Must-Haves

- **1. Verified default install story — PASS**
  - 默认支持的 shell/manual 安装路径已改为“下载 release 资产 → 校验 → 安装”。
  - `ARCHIVE_TAG=main` / mirror / branch fallback 只再作为 preview / unsupported 路径存在。

- **2. Stronger release identity evidence — PASS**
  - release workflow 继续复用 `ci.yml`，并新增 installer asset、SBOM 与 GitHub artifact provenance attestation。
  - runbook 已把这些资产列为当前 posture 与 post-release checks。

- **3. Honest productization docs and metadata — PASS**
  - SUPPORT / SECURITY / CONTRIBUTING / metadata 现统一公开支持路径、支持窗口与单维护者现实。
  - maintainer redundancy 仍被诚实记录为现实缺口，而不是被伪装成已解决。

## Evidence

- `uv run pytest -q tests/meta/test_install_sh_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` → `56 passed`
- `shellcheck install.sh` → skipped (`shellcheck` not installed in local environment)
- `node /home/claudeuser/.codex/get-shit-done/bin/gsd-tools.cjs verify phase-completeness 26` → `complete: true`

## Risks / Notes

- 本 phase 并未虚构第二维护者；`.github/CODEOWNERS` 与 public docs 现在都诚实承认仍是 single-maintainer model。
- `signing` 与 hard `code scanning` release gate 仍属于显式 defer，不得被误读为 silent debt。
- 本 phase 不涉及 Phase 27 的 runtime/protocol hotspot slimming；后续 maintainability debt 仍需单独推进。
