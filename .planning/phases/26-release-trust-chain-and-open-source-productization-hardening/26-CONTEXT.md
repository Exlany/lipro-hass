# Phase 26 Context

**Phase:** `26 Release trust chain and open-source productization hardening`
**Milestone:** `v1.3 Quality-10 Remediation & Productization`
**Date:** `2026-03-17`
**Status:** `Ready for planning`
**Source:** `Phase 25` route map + `Phase 25.2` closeout + release/install/open-source productization review

## Why Phase 26 Exists

仓库已经有不错的 CI / governance 骨架，但对外安装与发布故事线仍停在“`wget | bash` + checksum soft-fail + runbook defer provenance/SBOM”阶段。若按国际成熟开源标准，这条 trust chain 还不够硬，公开支持与版本策略也还不够诚实。

## Goal

1. 把默认 shell/manual 安装故事线收口到“下载 release 资产 → 校验 → 安装”。
2. 把 release workflow 从“zip + SHA256SUMS”升级为带 attestation / SBOM / installer asset 的正式发布尾链。
3. 让 README / README_zh / SUPPORT / SECURITY / CONTRIBUTING / runbook / metadata 对支持窗口、安装路径、单维护者现实与双语导航讲同一条故事。

## Decisions (Locked)

- 本 phase 不伪造“已有第二维护者”；维护者冗余若尚不存在，必须诚实写成单维护者现实与显式风险。
- 远程 `wget | bash` 不再是默认支持路径；若保留，也只能是明确标记的 advanced / unsupported preview path。
- release hardening 优先接入 GitHub 原生 provenance attestation 与可发布 SBOM；不另立第二条发版故事线。
- checksum 验证必须内建于 installer / workflow，不依赖用户本机是否预装 `sha256sum`。

## Non-Negotiable Constraints

- 不得绕开 `.github/workflows/ci.yml` 另起发版通道。
- 不得把 `main` / mirror / branch fallback 继续包装成默认支持安装路径。
- 不得为了“看起来成熟”伪造 maintainer redundancy 或未实际存在的支持承诺。
- 不得顺手扩题到 Phase 27 的架构瘦身 / 测试巨石拆分。
