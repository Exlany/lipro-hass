# Phase 106 Summary

## What Changed

- `LiproRestFacade` now exposes a sanctioned `auth_api` surface for endpoint collaborators
- REST endpoint payload adapter no longer pierces private auth internals
- `query_device_status()` now delegates task construction, execution, and merge concerns to smaller helpers
- `options_flow` now builds init/advanced schemas via reusable helper functions and spec tuples
- ADR-0001 terminology now aligns better with current `facade / transport collaborator` vocabulary

## Why It Matters

本轮没有改变 outward behavior，却把几处“不会立刻炸、但会持续提高维护成本”的残留真正降了密度。这样下一次复查时，看到的将是更清晰的边界，而不是更多“先这样用着”的局部例外。

## Integrity Notes

- 未重开 archived-only governance route
- 未引入新依赖
- 未扩大 public surface
- 未把 phase execution trace 误提升为 current governance truth
