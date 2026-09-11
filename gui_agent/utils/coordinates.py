"""Gestion des coordonnées géométriques multi-écrans et normalisation."""

from __future__ import annotations

import math
import os
import mss


def check_display_env() -> None:
    """Vérifie la présence d'un serveur d'affichage graphique valide."""
    if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
        raise RuntimeError("Aucun serveur graphique détecté (DISPLAY ou WAYLAND_DISPLAY requis).")


def get_monitor_geometry(monitor_index: int = 1) -> tuple[int, int, int, int]:
    """Obtient les coordonnées (left, top, width, height) d'un moniteur spécifique."""
    if not isinstance(monitor_index, int) or isinstance(monitor_index, bool):
        raise TypeError(f"monitor_index doit être un entier, reçu : {type(monitor_index).__name__}")
    check_display_env()
    with mss.mss() as sct:
        if monitor_index < 0 or monitor_index >= len(sct.monitors):
            raise ValueError(
                f"Index de moniteur invalide : {monitor_index}. Index valides : 0 à {len(sct.monitors) - 1}."
            )
        m = sct.monitors[monitor_index]
        return m["left"], m["top"], m["width"], m["height"]


def normalize_coordinates(
    x: float, y: float, normalized: bool = False, inverse: bool = False, monitor_index: int = 1
) -> tuple[int, int]:
    """Convertit des coordonnées du référentiel [0, 1000] vers les pixels réels (ou inversement)."""
    if not isinstance(normalized, bool) or not isinstance(inverse, bool):
        raise TypeError("Les paramètres normalized et inverse doivent être des booléens.")
    if isinstance(x, bool) or isinstance(y, bool) or not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
        raise TypeError("Les coordonnées x et y doivent être des nombres réels (int ou float).")
    if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
        raise ValueError("Les coordonnées x et y ne peuvent pas être NaN ou Infinity.")
    left, top, width, height = get_monitor_geometry(monitor_index)
    if inverse:
        rx = round(max(0.0, min(1000.0, ((float(x) - left) / max(1, width - 1)) * 1000.0)))
        ry = round(max(0.0, min(1000.0, ((float(y) - top) / max(1, height - 1)) * 1000.0)))
        return rx, ry
    if normalized:
        fx, fy = max(0.0, min(1000.0, float(x))), max(0.0, min(1000.0, float(y)))
        return left + round((fx / 1000.0) * float(max(0, width - 1))), top + round(
            (fy / 1000.0) * float(max(0, height - 1))
        )
    return round(max(float(left), min(float(left + max(0, width - 1)), float(x)))), round(
        max(float(top), min(float(top + max(0, height - 1)), float(y)))
    )
