# Phase 83 Research — Intake templates and maintainer stewardship contract

## Summary

`Phase 82` 已把 maintainer-facing release route 收口完成；`Phase 83` 的真实缺口现在集中在 community-health intake 与 maintainer stewardship surfaces。最佳策略不是新增文件族或提前扩 guards，而是把现有 issue / PR / security / support / contributor docs 收口为 minimum-sufficient-evidence contract，再把这组 truth 投影进 `GOVERNANCE_REGISTRY.json` 与既有 focused suites，并把 current-route freeze / broader guard coverage 明确留给 `Phase 84`。

## What the current repo already gets right

- `.github/ISSUE_TEMPLATE/bug.yml` 已经明确要求 diagnostics-first、把安全问题 reroute 到 `SECURITY.md`，并诚实承认 private-access / single-maintainer / no-hidden-delegate 约束
- `.github/ISSUE_TEMPLATE/config.yml` 已把 Documentation 链接指向 `docs/README.md`，没有把 GitHub UI 误写成默认 first hop
- `SUPPORT.md`、`SECURITY.md` 与 `.github/CODEOWNERS` 已形成一套真实的 continuity baseline：single-maintainer、no documented delegate、freeze new tagged releases and new release promises、restore custody only after documented successor/delegate
- `CONTRIBUTING.md` 与 `docs/README.md` 已把 contributor / support / security / maintainer appendix 的主路由分开，没有让 runbook 回流成 public first hop
- `tests/meta/test_governance_release_docs.py`、`tests/meta/test_governance_release_continuity.py` 与 `tests/meta/test_version_sync.py` 已提供足够的 regression baseline，可在本 phase 作为守旧验证，而无需提前做 `Phase 84` 的 guard 扩张

## Concrete gaps found

### 1. Issue templates still collect symptoms more than boundary-scoped evidence

`bug.yml` 已有 `Steps to Reproduce`、`Expected Behavior`、安装方式、日志与 developer report 升级路径，但没有显式字段去收集：

- 受影响的 boundary family / area
- 风险或影响面
- 验证命令、验证步骤或等价 proof

`feature_request.yml` 的现状更弱：只有 `Problem / Solution / Alternatives / Additional Context`，缺少 maintainer triage 真正需要的 boundary / impact / success-verification 信息。对照 `GOV-61`，当前 issue forms 还不算 minimum-sufficient-evidence router。

### 2. PR intake is governance-aware, but not yet evidence-first

`.github/pull_request_template.md` 的 CI checklist 很强，也明确要求在 continuity wording 变化时同步 `CODEOWNERS` 与 `GOVERNANCE_REGISTRY.json`。但 `Summary` 与 `Testing` 仍是自由文本，没有明确要求作者说明：

- 受影响 boundary family
- 风险 / 影响面
- 是否触及 disclosure / support / docs routing
- 哪个验证命令最能证明这次改动成立

这会让 maintainer review 仍依赖隐性追问，而不是在 intake 时先拿到最小充分证据。

### 3. Security routing exists, but structured intake requirements are still partial

`SECURITY.md` 已要求 `integration version`、`Home Assistant version`、`reproduction steps`、`impact assessment` 与 `redacted logs`，且明确 private disclosure path 与 best-effort response expectations。这是很好的起点。

真实缺口在于：

- 还没有把 boundary family / affected surface 写成明确 intake expectation
- 还没有要求报告者给出验证修复或缓解的方式
- 仓库里不存在 security advisory template 文件，因此唯一真实可改的 surface 只有 `SECURITY.md` 与 `.github/ISSUE_TEMPLATE/config.yml`

因此正确策略是收紧现有 policy wording，而不是编造新的 GitHub security form 文件。

### 4. Stewardship truth is present, but still split across contributor-facing docs

`SUPPORT.md` 已描述 triage owner、best-effort posture、maintainer-unavailable drill 与 custody restoration；`SECURITY.md` 也复用了同一 continuity truth；`.github/CODEOWNERS` 则是 owner truth source。

但对于普通贡献者来说，maintainer ownership / triage expectations / handoff rules 仍分散在多个文件里：

- `CONTRIBUTING.md` 更偏 setup / CI / PR mechanics
- `docs/README.md` 负责 role routing，但没有简洁地总结 stewardship contract
- `SUPPORT.md` 与 `SECURITY.md` 各自讲自己的 route，尚未抽成 contributor-facing 的统一 stewardship story

这正是 `OSS-11` 想消灭的“默认依赖口头知识”问题。

### 5. Governance registry does not yet model intake/stewardship detail

`.planning/baseline/GOVERNANCE_REGISTRY.json` 当前覆盖了 support route、documentation route、feature route 与 continuity phrases，但还没有表达：

- issue / PR / security 最小证据包
- triage / review expectations
- handoff / continuity projection targets beyond current wording

若 `Phase 83` 不把这部分 truth machine-readable 化，后续 docs/templates 很容易再次 drift；但 current-route freeze 与 broader verification matrix 对齐仍应留给 `Phase 84`。

## File-level implementation advice

### Intake surfaces (`83-01`)
- `.github/ISSUE_TEMPLATE/bug.yml`
  - 增补 boundary family、impact / risk、verification command / proof
  - 保留 diagnostics-first 与 private disclosure reroute，不把 developer report 变成硬门槛
- `.github/ISSUE_TEMPLATE/feature_request.yml`
  - 从“想要什么”升级为“问题背景 + 影响边界 + 成功验证信号”的最小 triage intake
- `.github/ISSUE_TEMPLATE/config.yml`
  - 调整 contact links wording，让 docs / security / discussion route 更明确地承认 evidence-first 分流
- `.github/pull_request_template.md`
  - 在 `Summary` / `Testing` 周围加入最小结构化提示：affected boundary family、risk / impact、docs / disclosure follow-up、关键验证命令
- `SECURITY.md`
  - 强化私密披露 payload 说明；不要新增不存在的 security template 文件

### Contributor-facing stewardship docs (`83-02`)
- `CONTRIBUTING.md`
  - 补上 maintainer review expectations、何时走 support/security route、以及 stewardship truth 的指向
- `SUPPORT.md`
  - 更明确地写出 support boundary、triage expectations、best-effort timing、handoff / restoration rules
- `SECURITY.md`
  - 与 `SUPPORT.md` / `CODEOWNERS` 保持同一 ownership / continuity story，但不复制完整 runbook
- `docs/README.md`
  - 只做 role-routing 层的 stewardship callout，不把 maintainer-only appendix 提升为 public first hop
- `.github/CODEOWNERS`
  - 若 wording 需要更精准，可同步精修；否则继续保持它是 owner truth source，而不是长篇流程文档

### Governance ledger + targeted proof (`83-03`)
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
  - 增加 intake / stewardship 的 machine-readable truth
- `tests/meta/test_governance_release_docs.py`
  - 冻结 docs-first/public-first-hop、maintainer appendix reachability 与模板/文档路由一致性
- `tests/meta/test_governance_release_continuity.py`
  - 冻结 single-maintainer / no-hidden-delegate / custody-restoration wording across templates/docs/CODEOWNERS
- `tests/meta/test_version_sync.py`
  - 冻结 registry projection、docs index route 与模板字段/版本同步 truth

## Verification strategy

本 phase 只做 regression-style 验证，不提前扩写 `Phase 84` focused guards：

```bash
uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py
uv run python scripts/check_file_matrix.py --check
```

若 `GOVERNANCE_REGISTRY.json` 结构发生变化，优先让既有 `test_version_sync.py`、`test_governance_release_docs.py` 与 `test_governance_release_continuity.py` 继续绿色；新增 broader guard coverage 与 current-route freeze 统一留到 `Phase 84`。

## Risks and mitigations

- **Risk: Phase 83 scope bleeds into Phase 84**
  - Mitigation: 不改 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES`，不碰 `VERIFICATION_MATRIX.md`，只扩现有 targeted suites 与 registry-backed truth。
- **Risk: inventing non-existent GitHub community-health files**
  - Mitigation: security 只改 `SECURITY.md` + `.github/ISSUE_TEMPLATE/config.yml`，其它只复用已存在的 issue / PR surfaces。
- **Risk: stewardship wording implies a hidden delegate**
  - Mitigation: 一切 ownership / custody / restoration 都回指 `.github/CODEOWNERS` 与现有 maintainer appendix truth。
- **Risk: templates become too heavy for contributors**
  - Mitigation: 只要求 minimum-sufficient evidence，不要求 maintainer-only details 或重复 CI checklist。

## Rejected alternatives

- **新增 `SECURITY_TEMPLATE.md` 或 GitHub advisory form 文件**：拒绝；仓库里没有这个 home，属于编造不存在的文件。
- **把 maintainer stewardship contract 全部塞进 `docs/MAINTAINER_RELEASE_RUNBOOK.md`**：拒绝；这会把 contributor-facing truth 重新藏回 maintainer-only appendix。
- **在 `Phase 83` 顺手冻结 active-route / route-handoff / focused guards**：拒绝；这是 `TST-26` / `QLT-34`，属于 `Phase 84`。
- **保留 PR/issue 模板的自由文本现状，依赖 maintainer 后续追问补证据**：拒绝；这无法满足 `GOV-61` 的“最小充分证据”目标。
