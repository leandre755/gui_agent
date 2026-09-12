"""Émulation d'entrées clavier et souris pour Linux (X11 / uinput / evdev)."""

from __future__ import annotations

from .layers.input_emulation import (
    key_tap,
    mouse_click_at,
    mouse_drag_smooth,
    mouse_scroll,
    screen_capture,
)

__all__ = [
    "key_tap",
    "mouse_click_at",
    "mouse_drag_smooth",
    "mouse_scroll",
    "screen_capture",
]
