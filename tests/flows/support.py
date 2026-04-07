"""Shared helpers for config-flow topical tests."""

from __future__ import annotations

import voluptuous as vol


def _get_schema_field(schema: vol.Schema, key: str):
    """Return field validator for a voluptuous schema key."""
    for field, validator in schema.schema.items():
        if isinstance(field, (vol.Required, vol.Optional)) and field.schema == key:
            return validator
    return None


def _get_schema_marker(schema: vol.Schema, key: str):
    """Return marker metadata (required/optional) for a voluptuous schema key."""
    for field in schema.schema:
        if isinstance(field, (vol.Required, vol.Optional)) and field.schema == key:
            return field
    return None
