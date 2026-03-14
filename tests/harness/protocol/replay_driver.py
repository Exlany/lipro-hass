"""Deterministic replay driver for protocol fixtures and canonical assertions."""

from __future__ import annotations

from typing import assert_never

from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.core.protocol.boundary import (
    decode_mqtt_properties_payload,
)
from tests.harness.protocol.replay_loader import load_replay_fixture
from tests.harness.protocol.replay_models import (
    LoadedReplayFixture,
    ReplayExecutionResult,
    ReplayManifest,
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
        started_at = manifest.controls.clock_baseline
        finished_at = manifest.controls.clock_baseline
        try:
            operation = manifest.operation
            if operation == "protocol.boundary.decode_mqtt_properties":
                metadata = fixture.authority_metadata
                payload = metadata.get("payload")
                result = decode_mqtt_properties_payload(payload)
                return ReplayExecutionResult(
                    manifest=manifest,
                    public_path="core.protocol.boundary.decode_mqtt_properties_payload",
                    started_at=started_at,
                    finished_at=finished_at,
                    canonical=result.canonical,
                    drift_flags=(),
                    error_category=None,
                    fingerprint=result.fingerprint,
                )

            protocol = self._protocol_factory(
                "replay-phone-id",
                entry_id=f"replay:{manifest.scenario_id}",
            )
            canonical: object
            public_path: str
            if operation == "protocol.contracts.normalize_mqtt_config":
                canonical = protocol.contracts.normalize_mqtt_config(
                    fixture.authority_payload
                )
                public_path = "LiproProtocolFacade.contracts.normalize_mqtt_config"
            elif operation == "protocol.contracts.normalize_device_list_page":
                canonical = protocol.contracts.normalize_device_list_page(
                    fixture.authority_payload
                )
                public_path = "LiproProtocolFacade.contracts.normalize_device_list_page"
            elif operation == "protocol.contracts.normalize_device_status_rows":
                canonical = protocol.contracts.normalize_device_status_rows(
                    fixture.authority_payload
                )
                public_path = "LiproProtocolFacade.contracts.normalize_device_status_rows"
            elif operation == "protocol.contracts.normalize_mesh_group_status_rows":
                canonical = protocol.contracts.normalize_mesh_group_status_rows(
                    fixture.authority_payload
                )
                public_path = (
                    "LiproProtocolFacade.contracts.normalize_mesh_group_status_rows"
                )
            else:
                assert_never(operation)

            return ReplayExecutionResult(
                manifest=manifest,
                public_path=public_path,
                started_at=started_at,
                finished_at=finished_at,
                canonical=canonical,
                drift_flags=(),
                error_category=None,
            )
        except Exception as err:  # noqa: BLE001
            return ReplayExecutionResult(
                manifest=manifest,
                public_path=manifest.operation,
                started_at=started_at,
                finished_at=finished_at,
                canonical=None,
                drift_flags=("driver_error",),
                error_category=type(err).__name__,
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
