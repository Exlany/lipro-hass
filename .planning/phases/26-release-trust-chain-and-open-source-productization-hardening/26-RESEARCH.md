# Phase 26 Research

**Status:** `research complete`
**Date:** `2026-03-17`
**Requirement:** `GOV-21`, `QLT-03`

## Executive Judgment

`26` 的核心不是“多写几句 README”，而是把 **default supported install story + release tail + public support/security contract** 同时拉到同一条成熟开源故事线上。

最优拆分是 `4 plans / 4 waves`：

1. `26-01`：把 installer 与默认 shell/manual story 切到 verified release assets
2. `26-02`：给 release workflow 增加 installer asset、SBOM 与 provenance attestation，并更新 runbook
3. `26-03`：统一 public docs / support / security / contributor / metadata 口径
4. `26-04`：冻结 phase closeout truth、validation evidence 与 next-focus handoff

## Current Defect Chain

### 1. Default shell installer still teaches `wget | bash`

README / README_zh / troubleshooting 仍把 `ARCHIVE_TAG=latest` + 远程脚本执行作为默认支持路径，这与更强 supply-chain posture 冲突。

### 2. Installer checksum path is soft-fail and tool-dependent

`install.sh` 在缺失 `sha256sum`、缺失 `SHA256SUMS` 或找不到 release asset 时仍可能继续；这不符合 trusted release install 的硬门槛。

### 3. Release workflow still stops at `zip + SHA256SUMS`

当前 `.github/workflows/release.yml` 只产出 zip 与 checksums；runbook 还把 provenance / SBOM / signing 记录为 defer note。

### 4. Public support / security / contributor paths do not yet say the same thing

README / README_zh / SUPPORT / SECURITY / CONTRIBUTING / runbook 对“支持哪个安装路径”“支持哪个版本窗口”“`main` 是否支持”“单维护者现实”尚未统一。

## Recommended Contract

### A. Verified release-asset install is the supported shell path

- 支持路径：下载 `install.sh` + `lipro-hass-vX.Y.Z.zip` + `SHA256SUMS`（及 provenance/SBOM 辅助资产）后本地执行安装。
- `ARCHIVE_TAG=main` / mirror / branch fallback 只保留为显式 preview / unsupported path。

### B. Release tail publishes stronger identity evidence

- release assets 至少包括：zip、`SHA256SUMS`、`install.sh`、SBOM、artifact attestation。
- runbook 必须把这些资产写成 required post-release checks，而不是 deferred posture note。

### C. Productization docs stay honest

- 单维护者模型必须被明确记录；maintainer redundancy 目前是现实缺口，不得伪装成已解决。
- 双语导航必须说明哪些路径是 canonical public support/security entry points，并保持 README / README_zh 一致。

## Recommended Plan Structure

### Plan 26-01 — harden installer and move the supported shell story to verified release assets

**File focus:**
- `install.sh`
- `README.md`
- `README_zh.md`
- `docs/TROUBLESHOOTING.md`
- `tests/meta/test_install_sh_guards.py`
- `tests/meta/test_governance_guards.py`

### Plan 26-02 — publish installer, SBOM and provenance from the existing release tail

**File focus:**
- `.github/workflows/release.yml`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_governance_guards.py`
- `tests/meta/test_version_sync.py`

### Plan 26-03 — unify public support/security/contributor/productization truth

**File focus:**
- `SUPPORT.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `pyproject.toml`
- `.github/CODEOWNERS`
- `custom_components/lipro/manifest.json`
- `tests/meta/test_governance_guards.py`

### Plan 26-04 — close out active truth and verification evidence

**File focus:**
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/26-release-trust-chain-and-open-source-productization-hardening/26-VALIDATION.md`
- `.planning/phases/26-release-trust-chain-and-open-source-productization-hardening/26-VERIFICATION.md`

## Validation Architecture

### Targeted regression slices

- `uv run pytest -q tests/meta/test_install_sh_guards.py tests/meta/test_governance_guards.py -k "installer or release or support or codeowners"`
- `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py`

### High-risk scenarios that must be locked

- README / README_zh 不再默认推荐 `wget | bash`
- `install.sh` 能在不依赖 `sha256sum` 的情况下强制校验 release assets
- release workflow 产出 installer / SBOM / attestation，不旁路既有 CI gate
- SUPPORT / SECURITY / CONTRIBUTING / runbook 对单维护者现实与支持窗口讲同一条诚实故事
