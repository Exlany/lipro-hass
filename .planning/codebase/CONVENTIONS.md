# Coding Conventions

**Analysis Date:** 2026-03-28

> Snapshot: `2026-03-28`
> Freshness: 基于 `pyproject.toml`、`CONTRIBUTING.md`、`scripts/lint`、`.pre-commit-config.yaml`、`.github/workflows/ci.yml`、`custom_components/lipro/**` 与 `tests/**` 的当前截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本文件不得反向充当当前治理真源。

## Naming Patterns

**Files:**
- Use `snake_case.py` everywhere; production files encode plane and role in the filename, such as `custom_components/lipro/core/protocol/facade.py`, `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/service_registry.py`, `custom_components/lipro/core/telemetry/models.py`, and `custom_components/lipro/services/diagnostics/helpers.py`.
- Use focused suffixes to show responsibility: `*_support.py` for inward helpers, `*_types.py` or `models.py` for typed contracts, `*_handlers.py` for service/diagnostics branches, `*_surface.py` for outward control-facing surfaces, and `*_registry.py` for lookup/registration truth.
- Keep new files inside the existing plane family instead of inventing neutral names. Examples already in use: `custom_components/lipro/core/coordinator/runtime/device/snapshot.py`, `custom_components/lipro/core/api/endpoints/schedule.py`, `custom_components/lipro/core/anonymous_share/share_client_submit.py`.
- Test files use `test_*.py`. Thin anchor roots remain intentionally stable, while topic siblings carry most assertions, e.g. `tests/meta/test_dependency_guards.py` plus `tests/meta/dependency_guards_*.py`, and `tests/core/api/test_protocol_contract_matrix.py` plus fixture-backed contract tests.

**Functions:**
- Use `async_*` for Home Assistant entrypoints and async collaborators, e.g. `custom_components/lipro/__init__.py`, `custom_components/lipro/config_flow.py`, and `custom_components/lipro/control/service_router.py`.
- Use verb-led helper prefixes to reveal return shape and scope: `_build_*`, `_coerce_*`, `_find_*`, `_iter_*`, `_normalize_*`, `_load_*`, `build_*`, `find_*`, `iter_*`, `is_*`.
- Keep helper names honest about locality. `runtime_access.py` delegates to `runtime_access_support.py`; new helpers should follow that split instead of growing hidden alternate roots.

**Variables:**
- Use uppercase `UPPER_SNAKE_CASE` for constants and service schemas such as `DOMAIN`, `SCHEMA_VERSION`, and `SERVICE_SEND_COMMAND_SCHEMA` in `custom_components/lipro/services/contracts.py`.
- Use `_LOGGER = logging.getLogger(__name__)` for module loggers, seen across `custom_components/lipro/flow/login.py`, `custom_components/lipro/services/diagnostics/helpers.py`, and `custom_components/lipro/firmware_manifest.py`.
- Reuse canonical identifier names already frozen in contracts: `entry_id`, `device_id`, `biz_id`, `phone_id`, `msg_sn`, `failure_summary`.

**Types:**
- Prefer PEP 695 aliases for local truth, e.g. `type RuntimeTelemetryView = dict[str, object]` in `custom_components/lipro/control/runtime_access.py` and `type DevicePropertyMap = dict[str, object]` in `custom_components/lipro/core/device/device.py`.
- Prefer `@dataclass(slots=True)` or `@dataclass(frozen=True, slots=True)` for structured runtime/control data, e.g. `custom_components/lipro/core/device/device.py` and `custom_components/lipro/control/models.py`.
- Prefer `TypedDict` and `Protocol` for payload and dependency seams, e.g. `custom_components/lipro/core/telemetry/models.py`, `custom_components/lipro/services/contracts.py`, and `custom_components/lipro/control/service_registry.py`.

## Code Style

**Formatting:**
- Run `uv run ruff format --check .` as the canonical formatter check from `pyproject.toml`, `.github/workflows/ci.yml`, `scripts/lint`, and `CONTRIBUTING.md`.
- Keep `from __future__ import annotations` at the top of modules. All sampled production modules follow that pattern, and AST scanning shows all `299` production Python files under `custom_components/lipro` carry a module docstring.
- Production docstrings are expected on public modules, classes, and functions. AST scanning shows `607/607` public production functions and `374/374` public classes carry docstrings; tests are intentionally looser.

**Linting:**
- Ruff is the main style gate. `pyproject.toml` uses `select = ["ALL"]` with curated ignores for HA callback shapes, docstring noise, complexity rules, and specific project realities.
- Respect per-file relaxations instead of re-litigating them in new code: `tests/**/*.py` relaxes docstrings, private access, import placement, and magic values; `custom_components/**/*.py` allows relative imports and avoids forcing `pathlib`.
- Mypy is strict for the repository root set `custom_components/lipro` and `tests`, but test modules explicitly disable `no-untyped-def` and `no-untyped-call`; new production code should stay fully typed, while new tests may be selectively typed when mocks would otherwise become noisy.

## Import Organization

**Order:**
1. Module docstring and `from __future__ import annotations`
2. Standard library imports
3. Third-party or Home Assistant imports
4. Local relative imports

**Path Aliases:**
- Use the alias conventions registered in `pyproject.toml`: `voluptuous as vol`, `homeassistant.helpers.config_validation as cv`, `device_registry as dr`, `entity_registry as er`, and `homeassistant.util.dt as dt_util`.
- Keep first-party imports within the established `homeassistant` and `custom_components.lipro` families; Ruff isort already marks them as first-party roots.

## Error Handling

**Patterns:**
- Raise translated Home Assistant-facing errors at the service/control edge, not raw lower-level exceptions. Examples: `custom_components/lipro/services/errors.py`, `custom_components/lipro/services/schedule.py`, and `custom_components/lipro/control/developer_router_support.py`.
- Keep protocol and auth recovery logic near the protocol plane. Large functions such as `handle_401_with_refresh` in `custom_components/lipro/core/api/auth_recovery.py` and `query_with_fallback` in `custom_components/lipro/core/api/status_fallback.py` are existing hotspots, not invitations to spread retry semantics elsewhere.
- Use typed result objects and failure summaries instead of stringly folklore. `custom_components/lipro/core/command/result.py`, `custom_components/lipro/core/command/result_policy.py`, and `custom_components/lipro/services/diagnostics/types.py` are the current contract homes.

## Logging

**Framework:** Standard library `logging`.

**Patterns:**
- Log with `_LOGGER`/`logger` and route sensitive values through redaction or safe placeholders. See `custom_components/lipro/flow/login.py`, `custom_components/lipro/control/redaction.py`, and `custom_components/lipro/core/api/response_safety.py`.
- Keep warnings and errors boundary-specific: service diagnostics helpers warn on optional capability failures in `custom_components/lipro/services/diagnostics/helpers.py`; flow/login code warns on auth and connection failures in `custom_components/lipro/flow/login.py`.
- Do not add raw credential, token, MAC, IP, or vendor payload dumps; the docs and diagnostics contracts in `README.md`, `SUPPORT.md`, and `tests/core/test_diagnostics_config_entry.py` assume redacted output.

## Comments

**When to Comment:**
- Prefer module and function docstrings over inline comments. Production code consistently explains purpose at module/class/public function level.
- Use inline comments sparingly for Home Assistant integration constraints, fixture topology, or governance mechanics. Examples: `tests/conftest.py` explains thin-shell collection rules; `scripts/lint` documents why runtime requirements are exported before `pip-audit`.

**JSDoc/TSDoc:**
- Not applicable. Python docstrings follow the Google convention configured in `pyproject.toml`.

## Function Design

**Size:**
- Production size discipline is good but not flat. AST scanning finds `41` production functions over `50` lines and only `2` over `80` lines; the biggest are `custom_components/lipro/core/coordinator/coordinator.py::__init__` and `custom_components/lipro/core/api/auth_recovery.py::handle_401_with_refresh`.
- Module size is controlled on the production side: `0` production files exceed `500` lines, but `13` exceed `400`. Current hotspots are `custom_components/lipro/core/coordinator/runtime/command_runtime.py`, `custom_components/lipro/core/anonymous_share/manager.py`, `custom_components/lipro/core/protocol/boundary/rest_decoder.py`, `custom_components/lipro/core/command/result.py`, `custom_components/lipro/entities/firmware_update.py`, and `custom_components/lipro/flow/options_flow.py`.
- New behavior should go into sibling concern files before these hotspots grow further. The repo repeatedly uses inward splits such as `runtime_access.py` → `runtime_access_support.py` and `share_client.py` → `share_client_submit.py`.

**Parameters:**
- Prefer explicit keyword-only dependency injection for builders and façades, as in `custom_components/lipro/core/protocol/facade.py` and `custom_components/lipro/__init__.py`.
- Prefer typed context bundles or protocols over free-form `dict[str, Any]` when crossing plane boundaries.

**Return Values:**
- Keep HA entrypoints returning `bool`/`None` as expected by the platform.
- Keep internal helpers honest about return shape: `build_*` returns dataclasses or typed payloads, `find_*` returns one object or `None`, and `iter_*` returns typed collections.

## Module Design

**Exports:**
- Use thin outward homes and keep helper siblings inward-only. Examples: `custom_components/lipro/core/protocol/facade.py`, `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/services/diagnostics/helpers.py`, and `custom_components/lipro/core/telemetry/models.py`.
- Use `__all__` only where it protects canonical outward surfaces, such as `custom_components/lipro/core/protocol/facade.py`.

**Barrel Files:**
- Package `__init__.py` files exist, but the codebase avoids broad catch-all barrels. The important root `custom_components/lipro/__init__.py` is a thin adapter/wiring module, not a dumping ground for unrelated helpers.
- Avoid reintroducing names the governance docs intentionally quarantine, especially generic `client`, `mixin`, or hidden compat roots. `tests/meta/toolchain_truth_docs_fast_path.py` and `tests/meta/test_governance_release_contract.py` reinforce that contract from the docs side.

## Documentation Contract

**Public docs path:**
- Treat `README.md` and `README_zh.md` as mirrored public first hops that must point to `docs/README.md`.
- Treat `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, and `.github/pull_request_template.md` as the contributor/support/security contract family.
- Treat `docs/MAINTAINER_RELEASE_RUNBOOK.md` as maintainer-only appendix, not a replacement for the public first hop.

**Sync rules:**
- If you change docs entrypoints, release wording, or continuity/security/support routing, update `docs/README.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `.github/pull_request_template.md`, and `.planning/baseline/GOVERNANCE_REGISTRY.json` together.
- If you change architecture-facing public language, keep `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, and the relevant `tests/meta/*docs*` or governance contract tests aligned.
- Keep bilingual parity at the root by mirroring `README.md` and `README_zh.md` in the same change.

## Recommendations

- Prefer adding new production logic beside the current formal home instead of growing hotspots such as `custom_components/lipro/flow/options_flow.py`, `custom_components/lipro/__init__.py`, or `custom_components/lipro/core/command/result*.py`.
- Prefer new names that encode plane and role immediately; do not add fresh `client`, `mixin`, or vague helper names when a `*_service.py`, `*_runtime.py`, `*_surface.py`, or `*_support.py` pattern already exists nearby.
- Prefer doc updates that preserve the established docs-first route. If a change touches contributor, support, security, or release language, treat the docs contract as code and update its guards in `tests/meta/` in the same patch.

---

*Convention analysis: 2026-03-27*


## Phase 90 Naming / Ownership Reminder

- Treat `client.py` as an import shell name, not as evidence of a second REST root.
- Treat large-but-correct modules as formal homes first; only explicit helper siblings, not outward shells, may absorb new implementation details.


## Phase 91 Naming / Contract Reminder

- Treat `protocol_facade_rest_methods.py` as a support-only live canonicalization seam under `LiproProtocolFacade`, not as a separate façade.
- Treat `RuntimeTelemetrySnapshot`, `MetricMapping`, and `TracePayload` aliases as shared truth contracts, not convenience dict suggestions.
