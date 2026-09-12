"""Gestion et ciblage des fenêtres pour Linux (xdotool / wmctrl / EWMH)."""

from __future__ import annotations

from .layers.window_management import (
    activate_window,
    process_list,
    process_run,
)

__all__ = [
    "activate_window",
    "process_list",
    "process_run",
]
