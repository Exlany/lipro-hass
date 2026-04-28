"""Deterministic replay driver for protocol fixtures and canonical assertions."""

from __future__ import annotations

from typing import assert_never

from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.core.protocol.boundary import (
    decode_mqtt_message_envelope_payload,
    decode_mqtt_properties_payload,
    decode_mqtt_topic_payload,
)
from custom_components.lipro.core.telemetry.models import (
    build_failure_summary_from_exception,
    empty_failure_summary,
)
from tests.harness.protocol.replay_loader import load_replay_fixture
from tests.harness.protocol.replay_models import (
    LoadedReplayFixture,
    ReplayExecutionResult,
    ReplayManifest,
    ReplayOperation,
)

_PUBLIC_PATH_BY_OPERATION: dict[ReplayOperation, str] = {
    "protocol.boundary.decode_mqtt_topic": "core.protocol.boundary.decode_mqtt_topic_payload",
    "protocol.boundary.decode_mqtt_message_envelope": "core.protocol.boundary.decode_mqtt_message_envelope_payload",
    "protocol.boundary.decode_mqtt_properties": "core.protocol.boundary.decode_mqtt_properties_payload",
    "protocol.contracts.normalize_mqtt_config": "LiproProtocolFacade.contracts.normalize_mqtt_config",
    "protocol.contracts.normalize_list_envelope": "LiproProtocolFacade.contracts.normalize_list_envelope",
    "protocol.contracts.normalize_device_list_page": "LiproProtocolFacade.contracts.normalize_device_list_page",
    "protocol.contracts.normalize_device_status_rows": "LiproProtocolFacade.contracts.normalize_device_status_rows",
    "protocol.contracts.normalize_mesh_group_status_rows": "LiproProtocolFacade.contracts.normalize_mesh_group_status_rows",
    "protocol.contracts.normalize_schedule_json": "LiproProtocolFacade.contracts.normalize_schedule_json",
}


def _public_path_for_operation(operation: ReplayOperation) -> str:
    """Return the formal public-path contract for one replay operation."""
    return _PUBLIC_PATH_BY_OPERATION[operation]


def _build_success_result(
    *,
    fixture: LoadedReplayFixture,
    public_path: str,
    canonical: object,
    fingerprint: str | None = None,
) -> ReplayExecutionResult:
    """Return the canonical replay result for one successful execution."""
    manifest = fixture.manifest
    return ReplayExecutionResult(
        manifest=manifest,
        public_path=public_path,
        started_at=manifest.controls.clock_baseline,
        finished_at=manifest.controls.clock_baseline,
        canonical=canonical,
        drift_flags=(),
        error_category=None,
        error_type=None,
        failure_summary=empty_failure_summary(),
        fingerprint=fingerprint,
    )


class ProtocolReplayDriver:
    """Run replay scenarios through the formal protocol public path only."""

    def __init__(
        self,
        *,
        protocol_factory: type[LiproProtocolFacade] = LiproProtocolFacade,
    ) -> None:
        self._protocol_factory = protocol_factory

    def run_manifest(self, manifest: ReplayManifest) -> ReplayExecutionResult:
        """Load one manifest and run it through the formal path."""
        return self.run_fixture(load_replay_fixture(manifest))

    def run_fixture(self, fixture: LoadedReplayFixture) -> ReplayExecutionResult:
        """Execute one loaded replay fixture deterministically."""
        manifest = fixture.manifest
        operation = manifest.operation
        public_path = _public_path_for_operation(operation)
        try:
            if operation == "protocol.boundary.decode_mqtt_topic":
                metadata = fixture.authority_metadata
                topic = metadata.get("topic")
                expected_biz_id = metadata.get("expected_biz_id")
                topic_result = decode_mqtt_topic_payload(
                    topic,
                    expected_biz_id=expected_biz_id,
                )
                return _build_success_result(
                    fixture=fixture,
                    public_path=public_path,
                    canonical=topic_result.canonical,
                    fingerprint=topic_result.fingerprint,
                )
            if operation == "protocol.boundary.decode_mqtt_message_envelope":
                metadata = fixture.authority_metadata
                payload = metadata.get("payload")
                envelope_result = decode_mqtt_message_envelope_payload(payload)
                return _build_success_result(
                    fixture=fixture,
                    public_path=public_path,
                    canonical=envelope_result.canonical,
                    fingerprint=envelope_result.fingerprint,
                )
            if operation == "protocol.boundary.decode_mqtt_properties":
                metadata = fixture.authority_metadata
                payload = metadata.get("payload")
                properties_result = decode_mqtt_properties_payload(payload)
                return _build_success_result(
                    fixture=fixture,
                    public_path=public_path,
                    canonical=properties_result.canonical,
                    fingerprint=properties_result.fingerprint,
                )

            protocol = self._protocol_factory(
                "replay-phone-id",
                entry_id=f"replay:{manifest.scenario_id}",
            )
            canonical: object
            if operation == "protocol.contracts.normalize_mqtt_config":
                canonical = protocol.contracts.normalize_mqtt_config(
                    fixture.authority_payload
                )
            elif operation == "protocol.contracts.normalize_list_envelope":
                canonical = protocol.contracts.normalize_list_envelope(
                    fixture.authority_payload
                )
            elif operation == "protocol.contracts.normalize_device_list_page":
                canonical = protocol.contracts.normalize_device_list_page(
                    fixture.authority_payload
                )
            elif operation == "protocol.contracts.normalize_device_status_rows":
                canonical = protocol.contracts.normalize_device_status_rows(
                    fixture.authority_payload
                )
            elif operation == "protocol.contracts.normalize_mesh_group_status_rows":
                canonical = protocol.contracts.normalize_mesh_group_status_rows(
                    fixture.authority_payload
                )
            elif operation == "protocol.contracts.normalize_schedule_json":
                canonical = protocol.contracts.normalize_schedule_json(
                    fixture.authority_payload
                )
            else:
                assert_never(operation)

            return _build_success_result(
                fixture=fixture,
                public_path=public_path,
                canonical=canonical,
            )
        except (
            AssertionError,
            AttributeError,
            LookupError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as err:
            failure_summary = build_failure_summary_from_exception(
                err,
                failure_origin="protocol.replay",
            )
            return ReplayExecutionResult(
                manifest=manifest,
                public_path=public_path,
                started_at=manifest.controls.clock_baseline,
                finished_at=manifest.controls.clock_baseline,
                canonical=None,
                drift_flags=("driver_error",),
                error_category=failure_summary["failure_category"],
                error_type=failure_summary["error_type"],
                failure_summary=failure_summary,
            )

    @staticmethod
    def authority_canonical(fixture: LoadedReplayFixture) -> object | None:
        """Return the canonical contract recorded on one authority fixture, if any."""
        return fixture.authority_metadata.get("canonical")

    @staticmethod
    def authority_fingerprint(fixture: LoadedReplayFixture) -> str | None:
        """Return the authority fingerprint recorded on one fixture, if any."""
        fingerprint = fixture.authority_metadata.get("fingerprint")
        return fingerprint if isinstance(fingerprint, str) else None
