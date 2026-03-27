# Phase 89 Context

## Objective

继续站在北极星终态架构的裁决下，对 `lipro-hass` 做“归档后的第一轮 fresh follow-through”：把仍然影响长期可维护性和开源可协作性的边界泄漏、双装配、tooling coupling 与入口混信号收口掉。

## Authoritative Inputs

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md`
- `.planning/codebase/{ARCHITECTURE,STRUCTURE,STACK,INTEGRATIONS,CONVENTIONS,TESTING,CONCERNS}.md`

## Key Findings Feeding This Phase

### Production / Architecture

- entities 仍直连 runtime internals：`custom_components/lipro/entities/base.py:106`, `custom_components/lipro/entities/base.py:197`, `custom_components/lipro/entities/base.py:229`, `custom_components/lipro/entities/firmware_update.py:311`
- entity-facing runtime protocol 仍暴露 service/lock internals：`custom_components/lipro/runtime_types.py:222`
- `Coordinator` 与 `RuntimeOrchestrator` 双装配：`custom_components/lipro/core/coordinator/coordinator.py:79`, `custom_components/lipro/core/coordinator/coordinator.py:92`, `custom_components/lipro/core/coordinator/coordinator.py:106`

### Tooling / Governance

- architecture policy checker 仍吃 `tests.helpers`：`scripts/check_architecture_policy.py:10`, `scripts/check_architecture_policy.py:13`
- file-matrix / governance current truth 需要和 refreshed `.planning/codebase/*` 一起保持一致

### Open Source / Docs

- `README.md:15`, `docs/README.md:19`, `.github/ISSUE_TEMPLATE/bug.yml:18`, `.github/ISSUE_TEMPLATE/feature_request.yml:9` 仍有 repeated private-access wording
- `custom_components/lipro/manifest.json:6`, `custom_components/lipro/manifest.json:9` 的 docs/issue entry 仍不够清晰分流

## Constraints

- 不要新增第二正式 root、compat shell、backdoor 或 helper-owned public surface。
- 修改生产边界时，要优先用显式 verb / owned service home，而不是新增散乱 wrapper。
- docs/config 改动必须同步 current-story planning truth。
- 所有 Python 命令使用 `uv run ...`。

## Verification Floor

- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- 针对 runtime/entity、tooling、docs/metadata 变更的最小充分 pytest 套件
