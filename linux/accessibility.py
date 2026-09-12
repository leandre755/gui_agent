"""Médiation sémantique d'accessibilité programmatique via AT-SPI2 / D-Bus sous Linux."""

from __future__ import annotations

from .layers.accessibility import (
    find_atspi_mediator_binary,
    get_app_state,
    perform_action,
    set_mock_action_handler,
    set_mock_state,
    set_mock_value_handler,
    set_value,
)

__all__ = [
    "find_atspi_mediator_binary",
    "get_app_state",
    "perform_action",
    "set_mock_action_handler",
    "set_mock_state",
    "set_mock_value_handler",
    "set_value",
]
