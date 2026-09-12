"""Couche de Gestion de Fenêtrage & Processus Système."""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("gui_agent.layers.window_management")


def process_run(command: list[str], sudo_password: str | None = None, timeout: float = 30.0) -> dict[str, Any]:
    """Exécute un processus fils via PTY."""
    if not command:
        return {"status": "error", "message": "Commande vide non autorisée."}
    return {"status": "not_implemented", "command": command, "has_sudo": sudo_password is not None, "timeout": timeout}


def process_list() -> list[dict[str, Any]]:
    """Interroge /proc en lecture seule pour lister les processus."""
    if not os.path.exists("/proc"):
        logger.warning("Système /proc non disponible sur cette plateforme.")
        return [{"status": "error", "message": "Système de fichiers /proc non disponible sur cette plateforme."}]
    try:
        return [{"pid": int(e)} for e in os.listdir("/proc") if e.isdigit()]
    except Exception as e:
        logger.warning(f"Impossible d'inspecter /proc : {e}")
        return [{"status": "error", "message": f"Erreur d'inspection /proc : {e}"}]


def activate_window(window_id: str | None = None, title: str | None = None) -> dict[str, Any]:
    """Commute le focus auprès du compositeur par Window ID ou titre."""
    if not window_id and not title:
        return {"status": "error", "message": "Au moins window_id ou title doit être spécifié."}
    return {"status": "not_implemented", "window_id": window_id, "title": title}
