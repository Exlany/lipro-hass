# Phase 41 Remediation Roadmap

## North-Star Rules

- 只做收敛，不重开第二主链。
- 先清高杠杆边界与验证盲区，再做美化式整理。
- execution-trace 资产默认不升格为长期治理真源。
- 每项动作都要绑定验证门禁，避免“修了一点、又长回来”。

## P0 Immediate Risk Reduction

| Priority | Action | Why now | Suggested checks |
|---|---|---|---|
| P0 | 建立 maintainer delegate / security fallback contact | 降低 bus factor，是当前最大的开源治理风险 | `SUPPORT.md` / `SECURITY.md` / `.github/CODEOWNERS` 同步；模板与 runbook 回写 |
| P0 | 给 release 增加 artifact install smoke lane | 当前 release 更像“结构正确”而非“产物可用” | 在 `.github/workflows/release.yml` 中用 `install.sh` 安装 release zip 到临时 HA 目录 |
| P0 | 将覆盖率升级为“总量 + 变更面”双门禁 | 避免高历史覆盖稀释新增低覆盖代码 | CI 增加 changed-files 或 diff coverage gate |

## P1 High-Leverage Structural Fixes

| Priority | Action | Why now | Suggested checks |
|---|---|---|---|
| P1 | 解开 `control/` ↔ `services/` 双向缠绕 | 这是当前最核心的架构黏连点 | 针对 `tests/core/test_control_plane.py`、`tests/services/*`、`tests/meta/test_dependency_guards.py` |
| P1 | 把 `RuntimeAccess` 升级为 typed read-model contract | 当前仍含反射/MagicMock 兼容味道 | 新增 runtime public read API 后跑 `tests/core/test_diagnostics.py`、`tests/core/test_system_health.py` |
| P1 | 拆 `services/maintenance.py` 的 runtime infra 职责 | service helper 不应继续承载 runtime infra | `tests/services/test_maintenance.py` + lifecycle/init focused suites |
| P1 | 处理超热点文件与长函数 | 复杂度已集中到少数高杠杆模块 | `rest_decoder_support.py`、`diagnostics_api_service.py`、`share_client.py`、`message_processor.py` focused tests |

## P2 Governance and Documentation Hygiene

| Priority | Action | Why now | Suggested checks |
|---|---|---|---|
| P2 | 清理 `.planning/phases/**` 跟踪策略 | 当前 tracked 执行资产过量，侵蚀真源清晰度 | `.gitignore` / `PROMOTED_PHASE_ASSETS.md` / docs truth sync |
| P2 | 统一 façade 时代官方术语 | ADR / docs / code comments 仍有 `Client` / `mixin` 漂移 | `tests/meta/test_governance_guards.py` 可补词汇守卫 |
| P2 | 拆分 contributor fast-path 与 maintainer governance appendix | 当前外部贡献入口过重 | `CONTRIBUTING.md`、`docs/README.md`、PR 模板 联动改造 |
| P2 | 制定双语边界策略 | 当前 bilingual promise 不够可信 | README / CHANGELOG / SUPPORT / docs 的双语规则明文化 |

## P3 Long-Term Evolution

| Priority | Action | Why now | Suggested checks |
|---|---|---|---|
| P3 | 压缩多层同名转发链 | 减少跨层追踪成本 | public-surface + dependency guards |
| P3 | 将布尔失败返回升级为 typed result / reason code | 提升诊断颗粒度 | diagnostics/share focused tests |
| P3 | benchmark 从留证据升级到防回退 | 形成性能演进约束 | baseline compare / threshold warnings |
| P3 | 引入兼容性前瞻 lane | 提前感知 HA / 依赖变更 | scheduled beta/patch lane + deprecation gate |

## Suggested Future Phase Seeds

- **Phase 42**：control/services decoupling, runtime-access typed read model, maintenance home cleanup
- **Phase 43**：release/install E2E, diff coverage, local-vs-CI parity, deprecation preview lane
- **Phase 44**：phase asset pruning, docs/ADR terminology convergence, contributor fast-path, bilingual policy
- **Phase 45**：hotspot decomposition (`rest_decoder_support` / diagnostics / anonymous share / message processor) and result-typing improvements

## Quick Wins Checklist

- 在 `.github/workflows/release.yml` 的 `security_gate` 加显式 `setup-python`
- 把 `README.md` / `README_zh.md` 的版本示例改成占位符
- 删除 `custom_components/lipro/core/api/endpoints/devices.py:13` 与 `custom_components/lipro/core/api/endpoints/misc.py:32` 的 legacy/mixin 词汇
- 为 `SECURITY.md` 增补备用联系路径
- 在 `scripts/lint` 中更明确提示“未跑 governance/pytest/shellcheck”

## Sequencing Advice

1. 先补 **治理/验证硬伤**：delegate、release smoke、diff coverage。
2. 再拆 **control/services / runtime_access**：这是最大架构收益点。
3. 然后收 **docs/ADR/phase assets**：降低认知噪音与真源歧义。
4. 最后切 **热点文件**：避免在边界未稳前做局部重构反复回流。
