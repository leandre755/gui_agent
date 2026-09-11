"""Couche d'Émulation d'Entrées Bas-Niveau (uinput/evdev)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("gui_agent.layers.input_emulation")


def screen_capture(show_grid: bool = False, grid_step: int = 100) -> dict[str, Any]:
    """Capture le framebuffer avec grille optionnelle."""
    return {"status": "not_implemented", "show_grid": show_grid, "grid_step": grid_step, "message": "Phase 3 (#132)."}


def mouse_click_at(x: int, y: int, button: str = "left") -> dict[str, Any]:
    """Émet un clic absolu via uinput."""
    if not isinstance(x, int) or not isinstance(y, int) or isinstance(x, bool) or isinstance(y, bool):
        return {"status": "error", "message": "Les coordonnées x et y doivent être des entiers."}
    return {"status": "not_implemented", "action": "click", "x": x, "y": y, "button": button}


def mouse_drag_smooth(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> dict[str, Any]:
    """Interpolation cinématique continue de glisser-déposer."""
    return {"status": "not_implemented", "action": "drag_smooth", "start": (start_x, start_y), "end": (end_x, end_y)}


def mouse_scroll(clicks: int, direction: str = "down") -> dict[str, Any]:
    """Émet des événements de défilement."""
    return {"status": "not_implemented", "action": "scroll", "clicks": clicks, "direction": direction}


def key_tap(key_sequence: str) -> dict[str, Any]:
    """Injecte des événements d'entrée clavier via evdev."""
    if not key_sequence:
        return {"status": "error", "message": "Séquence de touches vide."}
    return {"status": "not_implemented", "action": "key_tap", "key_sequence": key_sequence}
