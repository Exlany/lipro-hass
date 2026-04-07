# Phase 41 PRD: Full-Spectrum Architecture, Code Quality, and Open-Source Audit

**Date:** 2026-03-20
**Requester:** 契约者
**Context:** `v1.6 Full-Spectrum Audit, Open-Source Excellence & Remediation Planning`

## Objective

对 `lipro-hass` 全仓进行一次终极审阅，覆盖所有 Python 代码、测试、文档、配置、CI/CD、治理与开源对外面。审阅必须不是泛泛而谈的“代码 review”，而是站在顶级架构师视角，结合本仓库北极星终态与优秀开源项目实践，对先进性、缺陷、残留、命名、目录、治理、产品化与维护体验做全方位裁决。

## Must Cover

1. `custom_components/lipro/**` 的正式 architecture：protocol / runtime / control / domain / assurance / entities / helpers / services 的边界、依赖方向、正式主链是否清晰。
2. 全部 Python 代码的质量观：命名、模块职责、热点文件、复杂度、异常边界、残留 compat/legacy 语义、老旧代码痕迹。
3. `tests/**`、`scripts/**`、`.github/workflows/**`、`pyproject.toml`、`.pre-commit-config.yaml`、`install.sh` 的质量门禁、工具链一致性、CI/release 风险与覆盖盲区。
4. `README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SECURITY.md`、`SUPPORT.md`、`CHANGELOG.md`、`docs/**`、Issue/PR 模板、`hacs.json`、`.devcontainer.json` 的开源成熟度、外部体验与治理一致性。
5. 仓库卫生：缓存/生成物、`__pycache__`、coverage 产物、egg-info、derived-map 身份边界、残留 phase/process 痕迹是否合理。
6. 用户未显式提出但对大师级审阅应包含的方面：可维护性、可演进性、可验证性、开源可协作性、发布/支持路径清晰度、治理文档真相分层。

## Deliverables

1. `41-AUDIT.md`：详尽终极审阅报告。
2. `41-REMEDIATION-ROADMAP.md`：可执行整改路线图。
3. `41-SUMMARY.md`：高层结论、亮点、核心问题、下一步建议。
4. `41-VERIFICATION.md`：本 phase 交付完整性与证据检查。

## Output Quality Bar

- 必须给出亮点，而非只报问题。
- 必须给出 severity（建议使用 Critical/High/Medium/Low）与优先级。
- 必须尽量引用具体文件位置。
- 必须解释“为什么这是问题 / 为什么当前做法优秀 / 为什么建议最优”。
- 必须区分“当前正式真源”“执行痕迹”“归档证据”“仓库卫生噪音”。
- 必须给出 quick wins、结构性重构、治理/文档修复、长期演进四层动作。

## Non-Goals

- 本 phase 不直接大规模重构实现代码。
- 本 phase 不把 execution-trace 资产误提升为长期治理真源。
- 本 phase 不重开已归档 milestone 的 current story。
