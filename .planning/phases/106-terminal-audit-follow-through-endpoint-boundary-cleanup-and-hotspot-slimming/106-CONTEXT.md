# Phase 106: Terminal Audit Follow-through, Endpoint Boundary Cleanup, and Hotspot Slimming - Context

**Status:** Executed as an archived-baseline follow-through pack under `v1.29`; formal milestone activation still waits for `$gsd-new-milestone`.
**Baseline:** `v1.29` latest archived baseline
**Why now:** 契约者要求继续以顶级架构师视角做全仓终极复审，并把仍具备维护成本的非阻塞残留收口，而不是停留在“closeout 已完成”的心理安全区。

## Scope

- 全仓 inventory：`733` 个 Python 文件、`26` 个 Markdown 文件、`5` 个 YAML 文件、`41` 个 JSON 文件、`1` 个 TOML 文件
- 重点 production scope：`custom_components/lipro/**`、`docs/adr/**`、`docs/developer_architecture.md`
- 核查方法：repo-wide inventory + smell scan + hotspot ranking + targeted source reading + focused regression

## Findings Driving This Follow-through

1. `custom_components/lipro/core/api/endpoints/payloads.py` 通过 `client._auth_api` 穿透私有 collaborator，违背“显式 surface 优于私有耦合”。
2. `custom_components/lipro/core/api/status_service.py` 的 `query_device_status()` 承担了批处理编排、并发调度与结果拼装三种职责，热点继续增稠。
3. `custom_components/lipro/flow/options_flow.py` 的 advanced schema 构建逻辑重复且偏长，后续增配项时容易继续膨胀。
4. `docs/adr/0001-coordinator-as-single-orchestration-root.md` 仍保留偏 legacy 的 `Client` 层表达，和当前 `facade / transport collaborator` 术语契约存在认知位移。
5. 仍有更大的 production hotspots 未在本轮直接改动：`core/anonymous_share/manager.py`、`core/api/status_fallback_support.py`、`core/api/rest_facade.py`、`core/coordinator/runtime/device/snapshot.py`。

## Constraints

- 不重新激活 `v1.29` current-route，不伪造 active milestone。
- 不引入新依赖、不改 public surface、不制造第二条 protocol/runtime/control 故事线。
- phase 资产只作为执行证据包；正式 current-route 仍以 archived-only governance contract 为准。
