# v1.8 Milestone Seed

> Snapshot: `2026-03-21`
> Identity: proposal-only / pull-only planning seed for the next formal milestone.
> Authority: this document does **not** override `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`; it exists to help the next `$gsd-new-milestone` and `$gsd-plan-phase 51` start from audited evidence instead of conversation memory.

## 1. Arbitration Summary

`Phase 46 -> 50` has already completed the formalized `v1.7` follow-up route. The next correct move is **not** to reopen `v1.7`, but to start a new milestone using the highest-value remaining findings from the repo-wide audit and Phase 50 closeout.

Two gap clusters still matter:

1. **Operational continuity / governance automation gaps** — open-source maturity is still constrained by bus-factor reality, manual registry-to-doc sync, and release rehearsal friction.
2. **Code sustainment hotspots** — the main architecture is correct, but several canonical roots / helper families / mega-tests remain denser than ideal for long-term maintainability.

**Recommended order of attack:**

1. continuity automation / governance-registry projection / release rehearsal hardening
2. protocol-root second-round slimming
3. runtime + entry-root second-round throttling
4. helper-hotspot formalization (`anonymous_share`, diagnostics API, request policy)
5. mega-test topicization round 2 + repo-wide typing-metric stratification

## 2. Candidate Milestone

**Name:** `v1.8 Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2`

**Why now:** `v1.7` proved the repository is already on the correct north-star architecture and can execute focused cleanup phases without reopening a second public story. The highest remaining value is no longer “save the architecture,” but to make the project more durable under maintainer absence and to keep dense formal roots / helper families from quietly re-accumulating long-term drag.

**North-star fit:**

- does not reopen legacy names, compat shells, or a second root
- prioritizes operational continuity and execution safety before another broad code sweep
- continues inward slimming of already-canonical homes instead of introducing new wrappers
- treats typing and test topology as sustainment contracts, not cosmetic polish

## 3. Candidate Requirement Basket

These IDs are **tentative** until promoted by `$gsd-new-milestone`.

- `GOV-38` — delegate / custody / maintainer-unavailable drill must become executable and low-friction across support, security, runbook, templates, and CODEOWNERS.
- `GOV-39` — governance registry should act as a projection source for downstream public-maintenance metadata, reducing manual sync drift.
- `QLT-18` — release chain must support verify-only / non-publish rehearsal plus change-type-specific minimal validation guidance.
- `ARC-08` — `LiproProtocolFacade` must continue inward decomposition without changing its status as the sole protocol-plane root.
- `HOT-12` — runtime / entry formal roots (`Coordinator`, `__init__.py`, `EntryLifecycleController`) must continue to slim along existing seams.
- `HOT-13` — helper hotspots (`AnonymousShareManager`, diagnostics API, request policy) must be decomposed without growing new public surfaces.
- `TST-10` — second-wave mega-tests should be topicized so failures land on one concern family instead of broad mixed suites.
- `TYP-13` — repo-wide typing metrics must distinguish production debt from test/guard literals and continue shrinking non-REST `Any` clusters.

## 4. Proposed Phase Seeds

### Phase 51 — Continuity automation, governance-registry projection, and release rehearsal hardening

**Why first**
- highest remaining open-source maturity risk is still maintainer continuity, not architectural correctness
- this phase improves bus factor, support trust, and release resilience without perturbing runtime behavior

**Primary outcomes**
- turn continuity / delegate / custody wording into one executable drill
- reduce multi-file manual sync by projecting stable maintenance metadata from the governance registry (or an equivalent single-source helper)
- add an explicit verify-only / non-publish release rehearsal path and document minimal sufficient validation slices by change type

**Core files**
- `SUPPORT.md`
- `SECURITY.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/CODEOWNERS`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/workflows/release.yml`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `CONTRIBUTING.md`

**Verify anchors**
- `uv run pytest tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_governance*.py tests/meta/test_version_sync.py -q`

### Phase 52 — Protocol-root second-round slimming and request-policy isolation

**Why next**
- `LiproProtocolFacade` remains correct but still too dense for a long-term canonical root
- `request_policy.py` is a natural collaborator hotspot that can be narrowed without changing protocol truth

**Primary outcomes**
- continue inward decomposition of login / status / command / OTA / schedule / MQTT-attach behavior
- isolate request pacing / retry / 429 / busy semantics into clearer collaborator seams
- preserve `LiproProtocolFacade` as the only protocol-plane root and avoid any second façade story

**Core files**
- `custom_components/lipro/core/protocol/facade.py`
- `custom_components/lipro/core/api/request_policy.py`
- protocol-facing tests / contract suites

### Phase 53 — Runtime and entry-root second-round throttling

**Why next**
- `Coordinator`, `__init__.py`, and `EntryLifecycleController` are improved but still remain high-density orchestration homes
- maintainability gain is high if further splitting can happen without growing adapter folklore

**Primary outcomes**
- keep runtime decisions inside canonical homes while shrinking method/file density
- separate entry bootstrap, activation, reload, and unload concerns more clearly
- preserve lazy wiring and current public behavior

**Core files**
- `custom_components/lipro/core/coordinator/coordinator.py`
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/control/entry_lifecycle_controller.py`

### Phase 54 — Helper-hotspot formalization (`anonymous_share`, diagnostics API, request policy companions)

**Why next**
- helper families now carry more maintainability risk than architecture risk
- privacy-sensitive upload/report paths and diagnostics aggregation deserve smaller, more explicit seams

**Primary outcomes**
- slim `AnonymousShareManager` / `share_client.py` / `report_builder.py`
- reduce decision density in diagnostics API helper flows
- keep privacy / sanitization / service contracts stable while shrinking `Any`-heavy projections

**Core files**
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/core/anonymous_share/report_builder.py`
- `custom_components/lipro/core/api/diagnostics_api_service.py`

### Phase 55 — Mega-test topicization round 2 and repo-wide typing-metric stratification

**Why next**
- first-wave topicization succeeded; next value is to keep failure localization sharp as the repo matures
- repo-wide typing truth now needs better classification, not just touched-zone guards

**Primary outcomes**
- topicize remaining large API/MQTT/platform suites
- separate production typing debt metrics from test/guard literal debt
- extend no-growth guard posture beyond the REST-only slice where justified by evidence

**Core files**
- `tests/core/api/test_api_command_surface.py`
- `tests/core/mqtt/test_transport_runtime.py`
- `tests/platforms/test_light.py`
- `tests/platforms/test_fan.py`
- `tests/platforms/test_select.py`
- typing-metric / meta-guard assets

## 5. Deferred Low-Priority Polish

These are still worthwhile, but do not outrank the seeds above:

- further slimming of `README.md` weight and maintainer appendix noise
- English summary / handoff-friendly treatment for maintainer-only appendices
- more explicit honesty around localized compat shims that are no longer active residual families

## 6. Next Formal Steps

1. run `$gsd-new-milestone` and promote only the chosen phase order into `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, and `STATE.md`
2. start with `$gsd-plan-phase 51`
3. execute `$gsd-execute-phase 51` only after the milestone and requirement basket are formally promoted
4. keep `v1.7` closeout truth unchanged until that promotion happens
