"""Focused predecessor guards for Phase 108 MQTT transport-runtime de-friendization."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import CURRENT_MILESTONE_DEFAULT_NEXT, CURRENT_ROUTE

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / '.planning' / 'PROJECT.md'
_ROADMAP = _ROOT / '.planning' / 'ROADMAP.md'
_REQUIREMENTS = _ROOT / '.planning' / 'REQUIREMENTS.md'
_STATE = _ROOT / '.planning' / 'STATE.md'
_MILESTONES = _ROOT / '.planning' / 'MILESTONES.md'
_VERIFICATION_MATRIX = _ROOT / '.planning' / 'baseline' / 'VERIFICATION_MATRIX.md'
_FILE_MATRIX = _ROOT / '.planning' / 'reviews' / 'FILE_MATRIX.md'
_RESIDUAL = _ROOT / '.planning' / 'reviews' / 'RESIDUAL_LEDGER.md'
_KILL = _ROOT / '.planning' / 'reviews' / 'KILL_LIST.md'
_TESTING = _ROOT / '.planning' / 'codebase' / 'TESTING.md'
_DEV_ARCH = _ROOT / 'docs' / 'architecture_archive.md'
_TRANSPORT = _ROOT / 'custom_components' / 'lipro' / 'core' / 'mqtt' / 'transport.py'
_RUNTIME = _ROOT / 'custom_components' / 'lipro' / 'core' / 'mqtt' / 'transport_runtime.py'
_REFACTORED_TEST = _ROOT / 'tests' / 'core' / 'mqtt' / 'test_transport_refactored.py'
_PHASE_DIR = _ROOT / '.planning' / 'phases' / '108-mqtt-transport-runtime-de-friendization'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_phase108_predecessor_bundle_remains_visible_under_phase109_route() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    verification_doc = _read(_PHASE_DIR / '108-VERIFICATION.md')
    validation_doc = _read(_PHASE_DIR / '108-VALIDATION.md')

    for text in (
        project_text,
        roadmap_text,
        requirements_text,
        state_text,
        milestones_text,
        verification_text,
    ):
        assert CURRENT_ROUTE in text
        assert CURRENT_MILESTONE_DEFAULT_NEXT in text

    assert '### Phase 108: MQTT transport-runtime de-friendization' in roadmap_text
    assert 'Phase 108 MQTT Transport-runtime De-friendization Note' in dev_arch_text
    assert '# Phase 108 Verification' in verification_doc
    assert '# Phase 108 Validation Contract' in validation_doc


def test_phase108_ledgers_testing_and_file_matrix_freeze_predecessor_story() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    residual_text = _read(_RESIDUAL)
    kill_text = _read(_KILL)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)

    for path in (
        'custom_components/lipro/core/mqtt/transport.py',
        'custom_components/lipro/core/mqtt/transport_runtime.py',
        'tests/core/mqtt/test_transport_refactored.py',
        'tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py',
    ):
        assert path in file_matrix_text
    assert 'focused predecessor guard home for Phase 108 MQTT transport-runtime de-friendization' in file_matrix_text
    assert '## Phase 108 Residual Delta' in residual_text
    assert '## Phase 108 Status Update' in kill_text
    assert '## Phase 108 Testing Freeze' in testing_text
    assert_testing_inventory_snapshot(testing_text)
    assert '## Phase 108 MQTT Transport-runtime De-friendization' in verification_text
    for token in (
        '$gsd-discuss-phase 110',
        'tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py',
        '.planning/phases/108-mqtt-transport-runtime-de-friendization/{108-01-SUMMARY.md,108-02-SUMMARY.md,108-03-SUMMARY.md,108-VERIFICATION.md,108-VALIDATION.md}',
    ):
        assert token in verification_text


def test_phase108_code_boundaries_keep_explicit_runtime_contract_visible() -> None:
    transport_text = _read(_TRANSPORT)
    runtime_text = _read(_RUNTIME)
    refactored_tests_text = _read(_REFACTORED_TEST)

    for token in (
        'self._runtime_callbacks = MqttTransportCallbacks(',
        'self._runtime_state = MqttTransportOwnerState()',
        'self._runtime_owner = MqttTransportRuntimeOwner(',
        'process_message_entrypoint_provider=lambda: self._process_message,',
        'transport_runtime = MqttTransportRuntime(self._runtime_owner)',
        'def _connected(self) -> bool:',
        'def _task(self) -> asyncio.Task[None] | None:',
        'def _reconnect_delay(self) -> float:',
    ):
        assert token in transport_text

    for token in (
        'class MqttTransportCallbacks:',
        'class MqttTransportOwnerState:',
        'class MqttTransportRuntimeOwner:',
        'def process_message_entrypoint(self) -> Callable[[aiomqtt.Message], None]:',
        'async def connect_and_listen(self) -> None:',
        'self._owner.process_message_entrypoint(message)',
        'await self._owner.connection_manager.run_connection_loop(',
    ):
        assert token in runtime_text

    for token in (
        'def test_transport_initializes_explicit_runtime_owner_contract() -> None:',
        'def test_transport_runtime_owner_reads_latest_collaborator_replacements() -> None:',
    ):
        assert token in refactored_tests_text
