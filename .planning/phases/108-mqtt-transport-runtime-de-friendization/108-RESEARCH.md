# Phase 108: MQTT transport-runtime de-friendization - Research

**Researched:** 2026-03-30
**Domain:** MQTT transport/runtime boundary contraction in `core/mqtt`
**Confidence:** HIGH

<user_constraints>
## User Constraints

No `*-CONTEXT.md` exists for this phase yet. Using the direct user prompt as the active constraint source.

### Locked Constraints
- Only analyze `custom_components/lipro/core/mqtt/transport.py`, `custom_components/lipro/core/mqtt/transport_runtime.py`, `custom_components/lipro/core/mqtt/connection_manager.py`, `custom_components/lipro/core/mqtt/subscription_manager.py`, `tests/core/mqtt/test_transport_runtime_*.py`, and `tests/core/mqtt/test_transport_refactored.py`.
- Find the concrete friend-class / private-state reach-through problems in the current implementation.
- Recommend the smallest change set that still closes the problem thoroughly.
- Do not change the outward contract of `MqttTransport`.
- Do not introduce a second root.
- Research only; do not change production code in this phase handoff artifact.

### Claude's Discretion
- Choose the exact shape of the explicit owner/state contract.
- Decide which existing private helper names should remain as thin wrappers vs be deleted as test-only residuals.
- Recommend the narrowest sufficient test reshaping.

### Deferred Ideas (OUT OF SCOPE)
- Broader MQTT redesign outside the listed files.
- New public surfaces or package exports.
- Cross-plane architecture surgery outside Phase 108.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RUN-10 | `transport_runtime.py` / `transport.py` must move to an explicit owner/state contract and remove friend-style private-state reach-through. | Hotspot list identifies exact reach-through sites; recommended refactor replaces whole-owner injection with a private state contract. |
| ARC-27 | Maintain single-root / explicit-collaborator truth; no second formal surface or backdoor. | Recommendation keeps `MqttTransport` as sole root and leaves `MqttConnectionManager` / `MqttSubscriptionManager` as focused collaborators. |
| TST-37 | Freeze behavior with focused regressions / no-regrowth guards. | Test section rewrites delegate-wiring tests into behavior and no-regrowth assertions. |
| QLT-45 | Touched scope must pass targeted validation and quality checks. | Validation architecture defines the smallest sufficient `uv run pytest` / `ruff` commands for this phase. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `AGENTS.md` is the canonical repository contract; `CLAUDE.md` does not override it.
- Required read order starts from `AGENTS.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, and the `.planning/*` truth set.
- Current focus and next phase routing must follow `.planning/STATE.md`.
- Do not create or rely on `agent.md`.

## Summary

Phase 108 is not a "replace MQTT architecture" task. It is a boundary-contraction task: keep `MqttTransport` as the sole concrete transport root, keep `MqttConnectionManager` and `MqttSubscriptionManager` as focused collaborators, and remove the current pattern where `MqttTransportRuntime` receives the whole transport object and reaches through nearly every private field in it.

The current smell has two layers. First, `transport_runtime.py` uses whole-file `SLF001` and directly reads/writes owner-private collaborators, callbacks, locks, events, and mutable state. Second, `transport.py` rebinds runtime methods back onto its own private namespace, so runtime logic calls back through transport aliases that point right back to runtime methods. That creates a friend-class loop, hides real ownership, and trains tests to lock onto private delegate wiring instead of behavior.

**Primary recommendation:** keep `MqttTransport` as the only root, introduce one private runtime-state contract object, inject that contract plus explicit collaborators into `MqttTransportRuntime`, delete test-only delegate aliases, and rewrite tests to freeze behavior rather than private wiring.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `MqttTransport` | repo local | Sole concrete MQTT transport root | Governance already defines it as the canonical localized transport, not a public export. |
| `MqttTransportRuntime` | repo local | Private helper for connect/listen loop only | Keeps runtime-heavy logic out of the root file, as long as it is fed an explicit contract instead of the whole owner. |
| `MqttConnectionManager` | repo local | Callback/error/backoff policy | Already a focused collaborator with explicit callback injection. |
| `MqttSubscriptionManager` | repo local | Topic batching and live subscription diff/apply | Already a focused collaborator; no owner reach-through inside it. |
| `aiomqtt` | `2.5.0` | MQTT client runtime | Existing pinned dependency in `uv.lock`; no new dependency needed. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `asyncio` | Python `3.13.5` stdlib | Tasks, lock, event orchestration | Transport lifecycle and wait semantics. |
| `pytest` | `9.0.0` | Test runner | Focused MQTT regressions and no-regrowth guards. |
| `ruff` | `0.15.4` | Lint / static hygiene | Phase gate for touched scope. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Private state contract | Merge all runtime code back into `transport.py` | Removes friend-class smell, but regrows the root hotspot and undoes prior collaborator extraction. |
| Private state contract | New exported owner adapter / facade | Adds another story and risks a second root. |
| Keep focused managers | Push transport state logic into `connection_manager.py` / `subscription_manager.py` | Broadens collaborators into pseudo-roots and blurs responsibility. |

**Installation:** no new packages recommended. Existing environment already pins required tooling.

**Version verification:** verified from `uv.lock`: `aiomqtt 2.5.0` (upload time `2026-01-04`), `pytest 9.0.0`, `ruff 0.15.4`.

## Architecture Patterns

### Recommended Project Structure
```
custom_components/lipro/core/mqtt/
├── transport.py            # sole root + public contract
├── transport_runtime.py    # private runtime helper + private state contract
├── connection_manager.py   # callback/error/backoff policy
└── subscription_manager.py # subscription diff/batch/apply policy
```

### Pattern 1: Transport-owned private state contract
**What:** `MqttTransport` owns one private mutable state object; `MqttTransportRuntime` receives that state plus explicit collaborators, not the whole transport owner.

**When to use:** When a helper must mutate connection/task/error/TLS state but must not become an owner or a public surface.

**Example:**
```python
@dataclass(slots=True)
class _MqttTransportState:
    subscribed_devices: set[str]
    pending_unsubscribe: set[str]
    broker_client: aiomqtt.Client | None
    task: asyncio.Task[None] | None
    last_error: Exception | None
    running: bool
    connected: bool
    connected_lock: asyncio.Lock
    connected_event: asyncio.Event
    tls_context: ssl.SSLContext | None


self._runtime = MqttTransportRuntime(
    credentials=self._credentials,
    state=self._state,
    on_message=self._on_message,
    on_connect=self._on_connect,
    message_processor=self._message_processor,
    connection_manager=self._connection_manager,
    subscription_manager=self._subscription_manager,
    clear_task_ref=self._clear_task_ref,
)
```

### Pattern 2: Runtime calls itself, not owner aliases
**What:** Inside `MqttTransportRuntime`, pass `self.connect_and_listen`, `self.set_last_error`, and `self.handle_disconnect` to `MqttConnectionManager`, and call `self.process_message()` / `self.invoke_callback()` directly.

**When to use:** Whenever a helper is already the active execution context and does not need to bounce through the root.

### Anti-Patterns to Avoid
- **Whole-owner injection:** `MqttTransportRuntime(self)` with `self._transport._...` reach-through.
- **Bound-method backfill:** copying runtime methods onto `transport._...` and then calling them back from runtime.
- **Test-only private surface:** keeping `_build_topic_pairs` / `_batched_topic_pairs` alive only because one test patches them.
- **Shadow reconnect state:** storing `_reconnect_delay` on transport while real backoff lives inside `MqttConnectionManager`.

## Hotspot List

1. **Whole-file owner-private reach-through in `transport_runtime.py`**
   - `custom_components/lipro/core/mqtt/transport_runtime.py:1` suppresses `SLF001` for the whole file.
   - `custom_components/lipro/core/mqtt/transport_runtime.py:45`, `:60`, `:87`, `:96`, `:107`, `:115-188` directly touch owner-private collaborators, callbacks, connection state, lock/event primitives, and error storage.
   - This means runtime owns no explicit contract; it effectively has unrestricted friend access.

2. **Method rebinding hides the real owner and enlarges private surface**
   - `custom_components/lipro/core/mqtt/transport.py:65-77` copies runtime methods onto transport-private names.
   - Two of those methods, `_build_topic_pairs` and `_batched_topic_pairs`, are production-dead; only `tests/core/mqtt/test_transport_refactored.py:54` and `:75` call them.
   - Production subscription batching already belongs to `MqttSubscriptionManager` at `custom_components/lipro/core/mqtt/subscription_manager.py:24-43` and `:45-209`.

3. **Self-referential callback loop inside runtime**
   - `custom_components/lipro/core/mqtt/transport_runtime.py:141-149` calls `self._transport._invoke_callback`, `self._transport._clear_last_error`, `self._transport._process_message`, and `self._transport._handle_disconnect` even though these are rebound runtime methods.
   - `custom_components/lipro/core/mqtt/transport_runtime.py:156-160` passes `self._transport._connect_and_listen`, `self._transport._set_last_error`, and `self._transport._handle_disconnect` back into `MqttConnectionManager.run_connection_loop()`.
   - The resulting path is runtime → transport alias → runtime again.

4. **Mutable runtime state crosses the boundary without structure**
   - Transport creates and mutates `_subscribed_devices`, `_pending_unsubscribe`, `_broker_client`, `_task`, `_last_error`, `_connected`, `_connected_lock`, `_connected_event`, and `_tls_context` at `custom_components/lipro/core/mqtt/transport.py:46-56` and `:107-165`.
   - Runtime mutates the same owner fields directly at `custom_components/lipro/core/mqtt/transport_runtime.py:115-188`.
   - That is the concrete missing "owner/state contract" named by Phase 108.

5. **Dead reconnect shadow state**
   - `_reconnect_delay` is initialized at `custom_components/lipro/core/mqtt/transport.py:56` and reset at `custom_components/lipro/core/mqtt/transport_runtime.py:129`.
   - It is never read. Actual reconnect backoff is purely local to `custom_components/lipro/core/mqtt/connection_manager.py:133-176`.

6. **Tests currently freeze the smell instead of the behavior**
   - `tests/core/mqtt/test_transport_refactored.py:45-47`, `:54-75`, `:86-117`, `:157-195` assert internal helper wiring and aliased private methods.
   - `tests/core/mqtt/test_transport_runtime_lifecycle.py:66-67`, `:79`, `:98-115`, `:127-133`, `:199-217` directly read/write owner internals.
   - `tests/core/mqtt/test_transport_runtime_subscriptions.py:29-218` and `tests/core/mqtt/test_transport_runtime_connection_loop.py:50`, `:62-63`, `:171`, `:205`, `:238`, `:271`, `:307` also rely heavily on those internals.

## Recommended Refactor Plan

1. **Keep `MqttTransport` as the sole root**
   - Do not add a new façade, owner adapter, or public state object.
   - `MqttTransportRuntime` remains a private collaborator only.

2. **Introduce one private runtime-state contract**
   - Put a private `_MqttTransportState` dataclass in `transport_runtime.py` or `transport.py`.
   - Give it only the mutable state that is truly shared across transport/runtime.
   - Exclude `_reconnect_delay`; it is residual.

3. **Inject explicit collaborators into runtime**
   - Runtime constructor should receive `credentials`, `state`, `on_message`, `on_connect`, `message_processor`, `connection_manager`, `subscription_manager`, and `clear_task_ref`.
   - After this, `transport_runtime.py` should no longer import `MqttTransport` for friend-style field access beyond typing needs.

4. **Delete alias-only private surface**
   - Remove `_build_topic_pairs` and `_batched_topic_pairs`; they are not production API.
   - For methods still convenient on transport (`_process_message`, `_handle_disconnect`, `_connect_and_listen`, `_connection_loop`, `_set_last_error`, `_clear_last_error`, `_invoke_callback`, `_async_finalize_connection_task`), either make them real thin wrappers or route transport internals directly to `self._runtime.*`.

5. **Make runtime call itself, not owner aliases**
   - `connection_loop()` should pass `self.connect_and_listen`, `self.set_last_error`, and `self.handle_disconnect` to `MqttConnectionManager.run_connection_loop()`.
   - `connect_and_listen()` should call `self.invoke_callback()`, `self.clear_last_error()`, `self.process_message()`, and `self.handle_disconnect()` directly.

6. **Do not move policy logic into the managers**
   - `MqttConnectionManager` and `MqttSubscriptionManager` are already the right focused homes.
   - The missing piece is explicit state ownership between transport and runtime, not more policy decomposition.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reconnect backoff | transport-level duplicate delay state | `MqttConnectionManager.run_connection_loop()` | Real backoff already lives there; `_reconnect_delay` is dead residual. |
| Topic validation/batching | transport-private `_build_topic_pairs` / `_batched_topic_pairs` | `MqttSubscriptionManager` + `MqttTopicBuilder` | Existing focused seam already handles invalid IDs and batching. |
| Callback error capture | ad-hoc try/except in transport/runtime root | `MqttConnectionManager.invoke_callback()` / `set_last_error()` | Keeps callback failure semantics centralized. |

**Key insight:** this phase should contract the boundary, not invent a new abstraction layer.

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — scoped files manage process-local memory only. | None |
| Live service config | None — no UI/database-backed external config in the scoped files. | None |
| OS-registered state | None — no systemd/launchd/task registration touched by this scope. | None |
| Secrets/env vars | None in phase scope beyond existing in-memory MQTT credentials object. | None |
| Build artifacts | None specific to this refactor. | None |

## Common Pitfalls

### Pitfall 1: Replacing friend access with a new pseudo-root
**What goes wrong:** A new adapter or facade is introduced and starts looking like an alternate owner.
**Why it happens:** Trying to hide state mutation behind a new object instead of making ownership explicit.
**How to avoid:** Keep `MqttTransport` as the only root; make the state object private and non-exported.
**Warning signs:** New package exports, new runtime adapter names, tests importing a new owner object.

### Pitfall 2: Keeping alias rebinding for test convenience
**What goes wrong:** Reach-through is reduced, but private delegate loops remain.
**Why it happens:** Tests are cheaper to keep than to rewrite.
**How to avoid:** Delete test-only aliases and rewrite tests around behavior.
**Warning signs:** `transport_runtime.py` still calls `self._transport._...` after the refactor.

### Pitfall 3: Breaking `wait_until_connected()` semantics while moving state
**What goes wrong:** Event/lock ordering drifts and callers observe false positives or hangs.
**Why it happens:** `connected`, `connected_event`, and disconnect cleanup move at different times.
**How to avoid:** Preserve the current lock-protected async assignment path for handshake transitions.
**Warning signs:** flaky tests around `wait_until_connected()` or message-stream end.

### Pitfall 4: Losing pending-unsubscribe replay semantics
**What goes wrong:** Failed unsubscribes stop replaying after reconnect or sync.
**Why it happens:** State moves but `pending_unsubscribe` ownership becomes unclear.
**How to avoid:** Keep `pending_unsubscribe` in the shared state contract and let `MqttSubscriptionManager` continue to own replay/apply behavior.
**Warning signs:** reconnect tests stop clearing pending removals after success.

## Code Examples

Verified pattern to implement in Phase 108:

```python
class MqttTransport:
    def __init__(...) -> None:
        self._state = _MqttTransportState(...)
        self._runtime = MqttTransportRuntime(
            credentials=self._credentials,
            state=self._state,
            on_message=self._on_message,
            on_connect=self._on_connect,
            message_processor=self._message_processor,
            connection_manager=self._connection_manager,
            subscription_manager=self._subscription_manager,
            clear_task_ref=self._clear_task_ref,
        )

    async def start(self, device_ids: list[str]) -> None:
        ...
        self._state.task = asyncio.create_task(self._runtime.connection_loop())


class MqttTransportRuntime:
    async def connection_loop(self) -> None:
        await self._connection_manager.run_connection_loop(
            is_running=lambda: self._state.running,
            connect_and_listen=self.connect_and_listen,
            set_last_error=self.set_last_error,
            handle_disconnect=self.handle_disconnect,
        )
```

## State of the Art

| Old Approach | Current Recommended Approach | When Changed | Impact |
|--------------|------------------------------|--------------|--------|
| `MqttTransportRuntime(self)` + owner-private reach-through | Private `_MqttTransportState` + explicit collaborator injection | Phase 108 target | Removes friend-class access without changing outward transport contract. |
| Runtime methods rebound onto transport private namespace | Runtime kept as private collaborator; transport only exposes real root methods | Phase 108 target | Shrinks private surface and test coupling. |
| `_reconnect_delay` stored on transport | Backoff state stays only in `MqttConnectionManager` | Phase 108 target | Removes dead state and false ownership. |

**Deprecated/outdated:**
- Whole-file `SLF001` as a permanent exception for `transport_runtime.py`.
- Private delegate aliases that exist only to satisfy `test_transport_refactored.py`.

## Open Questions

1. **Should transport keep thin private wrappers for `_process_message` / `_connect_and_listen` / `_connection_loop`?**
   - What we know: public contract does not require these names, but current tests use them heavily.
   - What's unclear: whether maintainers prefer smaller code churn now or a more aggressive private-surface cleanup.
   - Recommendation: keep only wrappers that materially reduce risk for existing behavior tests; delete pure test-only aliases immediately.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | Validation commands | ✓ | `0.10.9` | — |
| `python3` | Runtime / tests | ✓ | `3.13.5` | — |

**Missing dependencies with no fallback:**
- None

**Missing dependencies with fallback:**
- None

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 9.0.0` + `pytest-asyncio` |
| Config file | `pyproject.toml:68` |
| Quick run command | `uv run pytest tests/core/mqtt/test_transport_runtime_*.py tests/core/mqtt/test_transport_refactored.py -q` |
| Full suite command | `uv run pytest tests/core/mqtt tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RUN-10 | runtime no longer depends on whole-owner private reach-through | unit / focused integration | `uv run pytest tests/core/mqtt/test_transport_refactored.py tests/core/mqtt/test_transport_runtime_connection_loop.py -q` | ✅ |
| ARC-27 | no second root / no export drift | meta + unit | `uv run pytest tests/core/mqtt/test_transport_refactored.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py -q` | ✅ |
| TST-37 | current lifecycle / ingress / subscription behavior remains frozen | unit | `uv run pytest tests/core/mqtt/test_transport_runtime_lifecycle.py tests/core/mqtt/test_transport_runtime_ingress.py tests/core/mqtt/test_transport_runtime_subscriptions.py -q` | ✅ |
| QLT-45 | touched scope stays lint-clean and behavior-clean | lint + unit | `uv run ruff check custom_components/lipro/core/mqtt tests/core/mqtt && uv run pytest tests/core/mqtt/test_transport_runtime_*.py tests/core/mqtt/test_transport_refactored.py -q` | ✅ |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/core/mqtt/test_transport_runtime_*.py tests/core/mqtt/test_transport_refactored.py -q`
- **Per wave merge:** `uv run pytest tests/core/mqtt tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q`
- **Phase gate:** `uv run ruff check custom_components/lipro/core/mqtt tests/core/mqtt` and the full suite above must pass before verify-work.

### Wave 0 Gaps
- [ ] `tests/core/mqtt/test_transport_refactored.py` — rewrite away from delegate-wiring assertions toward behavior / no-regrowth guards.
- [ ] `tests/core/mqtt/test_subscription_manager.py` — optional but strongly recommended focused coverage so transport tests do not have to freeze manager internals indirectly.

## Sources

### Primary (HIGH confidence)
- `custom_components/lipro/core/mqtt/transport.py:46` - current state ownership, alias rebinding, and public contract.
- `custom_components/lipro/core/mqtt/transport_runtime.py:1` - whole-file `SLF001` and owner-private reach-through.
- `custom_components/lipro/core/mqtt/connection_manager.py:25` - focused callback/error/backoff seam.
- `custom_components/lipro/core/mqtt/subscription_manager.py:17` - focused subscription seam.
- `tests/core/mqtt/test_transport_refactored.py:45` - current tests freezing private delegate wiring.
- `tests/core/mqtt/test_transport_runtime_lifecycle.py:66` - current tests mutating owner internals.
- `tests/core/mqtt/test_transport_runtime_subscriptions.py:29` - current subscription-state assertions.
- `tests/core/mqtt/test_transport_runtime_connection_loop.py:20` - current connect/listen and retry behavior coverage.
- `.planning/ROADMAP.md:65` - formal Phase 108 goal.
- `.planning/REQUIREMENTS.md:55` - formal Phase 108 requirement `RUN-10`.
- `.planning/phases/106-terminal-audit-follow-through-endpoint-boundary-cleanup-and-hotspot-slimming/106-AUDIT.md:10` - prior audit naming `transport_runtime.py` as remaining friend-class hotspot.
- `.planning/phases/106-terminal-audit-follow-through-endpoint-boundary-cleanup-and-hotspot-slimming/106-REMEDIATION-ROADMAP.md:24` - prior remediation seed for explicit owner/state contract.

### Secondary (MEDIUM confidence)
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md:36` - single-root and no-bypass constraints applied to the recommendation.
- `.planning/baseline/PUBLIC_SURFACES.md:104` - `MqttTransport` locality / non-public-surface rule.

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all recommendations stay inside existing repo-local helpers and pinned dependencies.
- Architecture: HIGH - driven directly by Phase 108 requirement text, Phase 106 audit notes, and current code structure.
- Pitfalls: HIGH - derived from concrete private reach-through sites and current test coupling.

**Research date:** 2026-03-30
**Valid until:** 2026-04-13 (active code hotspot; refresh after implementation starts)
