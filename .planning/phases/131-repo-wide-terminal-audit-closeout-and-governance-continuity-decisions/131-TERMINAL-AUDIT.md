# Phase 131 Terminal Audit

status: complete
updated: 2026-04-01

## Scope & Inventory

- 审阅范围覆盖 production Python、tests、scripts、docs、workflows、governance selectors 与 review ledgers。
- 本轮静态盘点基线：`322` 个 production Python 文件 / `48,139` 行，`418` 个测试文件 / `68,374` 行，`21` 个脚本 / `3,199` 行，`19` 份当前 docs / `2,823` 行，`7` 个 workflow / `1,357` 行。
- phase 129 / 130 的 sanctioned hotspot 收口结果被视为本轮前置真相；`Phase 131` 不再重开大规模生产拆分，而是完成 repo-wide terminal audit closeout、docs/governance sync 与 final validation evidence。

## Executive Verdict

- **架构 verdict：Strong, north-star aligned.** 单一正式主链已基本稳定：`LiproProtocolFacade` 是唯一 protocol root，`Coordinator` 是唯一 runtime root，`control/` 是唯一正式控制面 home。
- **代码质量 verdict：Good with bounded hotspots.** 当前问题主要集中在少数 sanctioned formal homes 的 breadth / review cost，而不是双主链、mixin 复活、raw vendor payload 渗透或 uncontrolled residual。
- **治理与开源 readiness verdict：Honest and strong, but still conditional.** docs-first、private-access、single-maintainer、no-hidden-delegate、no-guaranteed-non-GitHub-private-fallback 等关键事实已经诚实 codify；仍不能把这些仓外限制包装成已解决能力。

## What Is Strong

- 单主链稳定：protocol / runtime / control / domain / assurance 五平面关系清晰，HA 根模块继续保持 thin adapter。
- no-active-residual posture 真实且可仲裁：`RESIDUAL_LEDGER` 与 `KILL_LIST` 没有把 sanctioned hotspot 伪装成 residual family 或 delete campaign。
- 测试/治理守卫成熟：docs、route、release、toolchain、fixtures 与 hotspot no-regrowth 都已有 focused pytest / script guards。
- public/docs honesty 成熟：public first hop、conditional GitHub surfaces、single-maintainer continuity、release trust stack 都有明确 contract。

## Issues Found This Phase

### Fixed in Phase 131

1. **live docs route drift**
   - `docs/developer_architecture.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 仍停在 `v1.36 archived` wording，与当前 active milestone route 不一致。
   - 本轮已前推到 `v1.37 active milestone route / starting from latest archived baseline = v1.36`，并明确 `Phase 131 complete / closeout-ready`。

2. **docs-first wording conflict**
   - `docs/README.md` 之前把 `docs/TROUBLESHOOTING.md -> SUPPORT.md` 既放进 public fast path，又在 phase-asset identity 里写成“不属于 public first hop”。
   - 本轮已改成：troubleshooting/support 是 public follow-up routes；maintainer runbook 才不是 public first hop。

3. **contributor onboarding mixed signal**
   - `CONTRIBUTING.md` 的 clone 示例先给出仓库地址，private-access 前提却晚于 quick-start。
   - 本轮已把 access-mode note 紧邻 clone 步骤，减少外部贡献者误判。

4. **Python/toolchain truth mismatch**
   - `pyproject.toml` / registry / installer floor 与 CI / devcontainer / pre-commit / mypy 的 minor-version target 曾被写成同一个概念，导致 `>=3.14` 与 `>=3.14.2` 两套故事互相打架。
   - 本轮已把 machine-readable truth 改成双层契约：最低支持版本保持 `>=3.14.2`（与 Home Assistant 依赖底线一致），而开发 / CI 继续对齐 `3.14` minor family，并补充对应 meta guard。

5. **machine-readable install honesty gap**
   - registry 曾把 `HACS` 记入 stable install path，和文档里“private-access / future public mirror 条件成立时才可达”的口径不完全一致。
   - 本轮已把 stable path 收敛为 `verified_release_assets`，并新增 `conditional_paths = ["HACS"]`。

6. **promoted evidence allowlist drift**
   - `PROMOTED_PHASE_ASSETS.md` 尚未显式登记 `Phase 129 / 130`，本轮也需要把 `Phase 131` closeout 资产纳入长期治理证据。
   - 本轮已补齐 `129 / 130 / 131` allowlist。

## Remaining Honest Boundaries

这些项在本轮被**明确登记为 boundary / next-wave candidate**，而不是伪装成“已解决”：

- **repo-external continuity / private fallback**：仓内只能 freeze promises、保持 docs/security/support honesty，不能凭空创造 guaranteed non-GitHub private fallback、delegate stewardship 或 backup maintainer。
- **sanctioned hotspot breadth**：`rest_facade.py`、`runtime_types.py`、`request_policy.py`、`dispatch.py`、`auth/manager.py`、`firmware_update.py` 仍是 formal homes 中最值得继续减压的文件，但当前已经是 bounded hotspot，而非 dual-root blocker。
- **meta/governance test bulk**：测试/治理的体量已经高于 production hotspots，后续应优先做 table-driven / topic-driven 收口，降低 review 噪音。
- **platform helper sanctioned seam**：`helpers/platform.py` 仍保留单一 `entry.runtime_data` runtime-entry seam；当前 guard 明确允许其 localized 存在，因此本轮不把它误写成 active regression，但应作为 future tightening candidate。

## Hotspot Ranking (Current Review-Cost Order)

1. `custom_components/lipro/core/api/rest_facade.py`
2. `custom_components/lipro/runtime_types.py`
3. `custom_components/lipro/core/api/request_policy.py`
4. `custom_components/lipro/core/command/dispatch.py`
5. `custom_components/lipro/core/auth/manager.py`
6. `custom_components/lipro/entities/firmware_update.py`
7. `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
8. `custom_components/lipro/core/command/result_policy.py`

## Naming & Structure Verdict

- **优点**：目录结构已高度按平面和职责划分；`control/`, `core/protocol/`, `core/coordinator/`, `core/device/`, `entities/`, `tests/meta/` 边界清晰。
- **问题**：`_support` / `test_phase*` / `_guards` 数量偏多，命名 discoverability 越来越像“治理历史索引”而非“当前领域语义”；但这更像未来 maintainability 优化项，不是当前 correctness blocker。
- **结论**：结构清晰度整体优秀，命名规范大体一致，少数历史/治理密度偏高模块需要在后续里程碑继续主题化降噪。

## Open-Source & Governance Verdict

- public entry、support、security、release trust、single-maintainer continuity 的合同都已具备“honesty over optics”特征。
- 当前仓库的主要开源不足不再是“缺文档”，而是**仓外现实限制仍然存在**：private-access、conditional GitHub surfaces、no documented delegate、no guaranteed non-GitHub private fallback。
- 本轮结论：这些限制已被正确 codify，因此属于 **honest unresolved governance boundary**，不是治理失真。

## Recommended Next Wave

- 若继续治理代码，而非进入 milestone archive，优先处理 bounded hotspot 与 wide-contract tightening，而不是再开新故事线：
  1. `runtime_types.py` 按 `schedule / ota / developer_diagnostics / telemetry` inward split 为 sibling contract modules，再由 root re-export。
  2. `rest_facade.py` 继续压缩 auth/request/telemetry seam 的审阅密度。
  3. 对 2~3 个最大 meta/governance tests 做 table-driven 收口，降低文案字面量依赖。
- 若遵守本轮 closeout boundary，则下一步应先执行 `$gsd-complete-milestone v1.37`，把 current closeout-ready truth 提升为 archived baseline，而不是继续在 `v1.37` 上隐性扩写。

