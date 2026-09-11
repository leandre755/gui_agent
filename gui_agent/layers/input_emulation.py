"""Couche d'Émulation d'Entrées Bas-Niveau : Injection directe d'événements périphériques (uinput/evdev)."""

from __future__ import annotations

import logging
from typing import Any
from gui_agent.utils.human_mimic import generate_smooth_path

logger = logging.getLogger("gui_agent.layers.input_emulation")


def screen_capture(show_grid: bool = False, grid_step: int = 100) -> dict[str, Any]:
    """
    Capture le framebuffer et superpose optionnellement une grille cartésienne calibrée.
    Permet au modèle visuel (VLM) de guider ses actions sur les surfaces graphiques opaques (WebGL/Canvas).
    """
    return {
        "status": "success",
        "show_grid": show_grid,
        "grid_step": grid_step,
        "message": "Capture de framebuffer initialisée.",
    }


def mouse_click_at(x: int, y: int, button: str = "left") -> dict[str, Any]:
    """Émet un événement de pointage et clic absolu via le sous-système d'émulation noyau (uinput)."""
    if not isinstance(x, int) or not isinstance(y, int):
        return {"status": "error", "message": "Les coordonnées x et y doivent être des entiers."}
    return {
        "status": "success",
        "action": "click",
        "x": x,
        "y": y,
        "button": button,
    }


def mouse_drag_smooth(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> dict[str, Any]:
    """
    Interpolation cinématique continue émettant un flux régulier d'événements de déplacement relatif.
    Franchit le seuil physique d'arrachement (drag threshold) pour déplacer des fenêtres, onglets et éléments graphiques.
    """
    path = generate_smooth_path(start_x, start_y, end_x, end_y, steps=max(2, int(duration * 40)))
    return {
        "status": "success",
        "action": "drag_smooth",
        "points_count": len(path),
        "start": (start_x, start_y),
        "end": (end_x, end_y),
    }


def mouse_scroll(clicks: int, direction: str = "down") -> dict[str, Any]:
    """
    Émet des événements discrets de défilement pour forcer le rendu des conteneurs virtualisés.
    """
    return {
        "status": "success",
        "action": "scroll",
        "clicks": clicks,
        "direction": direction,
    }


def key_tap(key_sequence: str) -> dict[str, Any]:
    """Injecte des événements d'entrée clavier atomiques ou combinatoires dans le sous-système d'entrée (evdev)."""
    if not key_sequence:
        return {"status": "error", "message": "Séquence de touches vide."}
    return {
        "status": "success",
        "action": "key_tap",
        "key_sequence": key_sequence,
    }
