# Phase 106 Audit

**Date:** 2026-03-30
**Scope:** whole repo inventory + targeted production hotspots + docs terminology consistency

## Repository Inventory Snapshot

| Metric | Value |
|---|---:|
| Python files | 733 |
| Markdown files | 26 |
| YAML files | 5 |
| JSON files | 41 |
| TOML files | 1 |

## Production Hotspot Snapshot

| File | LOC | Verdict |
|---|---:|---|
| `custom_components/lipro/core/anonymous_share/manager.py` | 435 | still a future-phase hotspot |
| `custom_components/lipro/core/protocol/boundary/rest_decoder.py` | 425 | large but boundary-owned and purposeful |
| `custom_components/lipro/entities/firmware_update.py` | 418 | feature-rich but coherent |
| `custom_components/lipro/core/api/rest_facade.py` | 418 | still large; keep on future slimming radar |
| `custom_components/lipro/core/api/status_fallback_support.py` | 414 | still dense; best tackled in dedicated phase |
| `custom_components/lipro/flow/options_flow.py` | 388 | improved in this phase |

## Fixed Now

1. **Private collaborator reach-through removed**
   - Before: `endpoints/payloads.py` read `client._auth_api`
   - After: reads sanctioned `client.auth_api`
   - Impact: protocol child collaborators now depend on explicit surface, not facade internals

2. **Status batch orchestration slimmed**
   - Before: one function owned batching + task construction + concurrency + flattening
   - After: split into helper trio with unchanged outward behavior
   - Impact: lower cognitive load, easier future tuning

3. **Options schema composition slimmed**
   - Before: repeated loops lived directly in flow methods
   - After: reusable field builders + spec tables
   - Impact: config-surface growth no longer requires extending monolithic methods

4. **Device-filter codec convergence begun**
   - Before: options-flow normalization and runtime parsing followed similar but duplicated semantics
   - After: both sides share one codec family for mode normalization and list tokenization
   - Impact: lowers UI/runtime drift risk without coupling flow back into runtime internals

5. **ADR terminology corrected**
   - Before: `Client` still named as one architectural layer
   - After: aligned to `Protocol façade / transport collaborators`
   - Impact: doc language now better matches ADR-0005 and current formal topology

## Deferred Findings (Need Formal Milestone)

- `core/anonymous_share/manager.py` still exceeds the preferred single-file budget
- `flow/options_flow.py` 与 `core/coordinator/runtime/device/filter.py` 之间仍有 device-filter codec 语义分散；本轮先收窄 schema composition，shared codec 仍应在正式 milestone 中统一
- `core/mqtt/transport_runtime.py` 仍以 file-level `SLF001` 维持 friend-class 风格的 transport private-state 穿透，需要 dedicated phase 才适合拔除
- `core/api/status_fallback_support.py` remains a density hotspot with recursive fallback complexity
- `core/api/rest_facade.py` continues to accumulate outward protocol conveniences plus collaborator ownership
- `core/coordinator/runtime/device/snapshot.py` remains a broad snapshot-assembly carrier
- organizational maintainer/delegate continuity risk remains non-code and unresolved by refactor
