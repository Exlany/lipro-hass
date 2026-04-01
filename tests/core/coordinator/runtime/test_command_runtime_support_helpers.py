"""Direct helper tests for CommandRuntime support seam."""

from __future__ import annotations

from unittest.mock import Mock

from custom_components.lipro.core.coordinator.runtime.command_runtime_support import (
    _build_failure_summary,
    _build_request_trace,
    _CommandRequest,
    _handle_command_dispatch_result,
)

pytest_plugins = ('tests.core.coordinator.runtime.test_command_runtime_support',)


def test_build_request_trace_uses_shared_trace_fields(mock_device) -> None:
    mock_device.iot_name = 'iot-name'
    mock_device.physical_model = 'model-x'
    request = _CommandRequest(
        device=mock_device,
        command='POWER_ON',
        properties=[{'key': 'powerState', 'value': '1'}],
        fallback_device_id='fallback-1',
    )

    trace = _build_request_trace(
        request=request,
        redact_identifier=lambda value: f'redacted:{value}' if value else None,
    )

    assert trace['device_id'] == 'redacted:test_serial_123'
    assert trace['requested_fallback_device_id'] == 'redacted:fallback-1'
    assert trace['requested_command'] == 'POWER_ON'
    assert trace['requested_property_keys'] == ['powerState']


def test_handle_command_dispatch_result_returns_msg_sn_without_failure(mock_device) -> None:
    record_failure = Mock()
    request = _CommandRequest(
        device=mock_device,
        command='POWER_ON',
        properties=None,
        fallback_device_id=None,
    )

    msg_sn = _handle_command_dispatch_result(
        request=request,
        result={'pushSuccess': True, 'msgSn': '12345'},
        trace={},
        route='iot',
        logger=Mock(),
        record_failure=record_failure,
    )

    assert msg_sn == '12345'
    record_failure.assert_not_called()


def test_handle_command_dispatch_result_records_push_failure(mock_device) -> None:
    record_failure = Mock(return_value={'reason': 'push_failed'})
    request = _CommandRequest(
        device=mock_device,
        command='POWER_ON',
        properties=None,
        fallback_device_id=None,
    )

    msg_sn = _handle_command_dispatch_result(
        request=request,
        result={'pushSuccess': False, 'message': 'boom'},
        trace={},
        route='iot',
        logger=Mock(),
        record_failure=record_failure,
    )

    assert msg_sn is None
    record_failure.assert_called_once()
    assert record_failure.call_args.kwargs['error_type'] == 'PushFailed'


def test_handle_command_dispatch_result_records_missing_msg_sn(mock_device) -> None:
    record_failure = Mock(return_value={'reason': 'missing_msg_sn'})
    request = _CommandRequest(
        device=mock_device,
        command='POWER_ON',
        properties=None,
        fallback_device_id=None,
    )

    msg_sn = _handle_command_dispatch_result(
        request=request,
        result={'pushSuccess': True},
        trace={},
        route='device_direct',
        logger=Mock(),
        record_failure=record_failure,
    )

    assert msg_sn is None
    record_failure.assert_called_once()
    assert record_failure.call_args.kwargs['error_type'] == 'CommandResultMissingMsgSn'


def test_build_failure_summary_marks_auth_failures() -> None:
    summary = _build_failure_summary(
        failure={'reason': 'api_error', 'route': 'iot', 'device_id': 'abc'},
        error_type='LiproAuthError',
        reauth_reason='auth_error',
    )

    assert summary['failure_category'] == 'auth'
    assert summary['reauth_reason'] == 'auth_error'
    assert summary['error_type'] == 'LiproAuthError'
