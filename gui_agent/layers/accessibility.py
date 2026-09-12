"""Couche d'Accessibilité Programmatique (AT-SPI / D-Bus)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("gui_agent.layers.accessibility")


def get_app_state(include_screenshot: bool = False) -> dict[str, Any]:
    """Extrait l'arbre d'accessibilité applicatif en JSON texte pur via AT-SPI."""
    return {"status": "not_implemented", "layer": "accessibility", "include_screenshot": include_screenshot}


def perform_action(element_id: str, action: str) -> bool:
    """Déclenche l'action du composant accessible par le bus."""
    return False


def set_value(element_id: str, text: str) -> bool:
    """Écrit directement la valeur textuelle dans la mémoire du composant."""
    return False
