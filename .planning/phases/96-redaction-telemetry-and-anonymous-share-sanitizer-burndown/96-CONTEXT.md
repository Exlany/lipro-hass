# Phase 96: Redaction, telemetry, and anonymous-share sanitizer burndown - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

`Phase 96` 聚焦 shared redaction truth 与 sanitizer complexity：`custom_components/lipro/control/redaction.py`、`custom_components/lipro/core/telemetry/exporter.py`、`custom_components/lipro/core/anonymous_share/manager.py` 等热点需要继续收口复杂度、统一 fail-closed 语义，并避免再次长出局部 secret-like key truth。
</domain>

<decisions>
## Implementation Decisions
- **D-01:** shared redaction registry 是唯一裁决源；任何新 helper 都只能消费它。
- **D-02:** complexity burn-down 优先通过 inward split / pure helper / normalized contract 完成，而不是用新 wrapper 掩盖大函数。
- **D-03:** 必须补 focused tests 证明 diagnostics / telemetry / anonymous-share 的 redaction 与 sanitizer 语义一致。
</decisions>
