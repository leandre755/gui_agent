"""Gestion des coordonnées géométriques multi-écrans et normalisation de l'espace d'affichage."""

from __future__ import annotations

import math
import os
import mss


def check_display_env() -> None:
    """Vérifie la présence d'un serveur d'affichage graphique valide (DISPLAY ou WAYLAND_DISPLAY)."""
    if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
        raise RuntimeError(
            "Aucun serveur graphique détecté. Vérifiez que la variable DISPLAY "
            "ou WAYLAND_DISPLAY est définie dans l'environnement."
        )


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
        mon = sct.monitors[monitor_index]
        return mon["left"], mon["top"], mon["width"], mon["height"]


def normalize_coordinates(
    x: float, y: float, normalized: bool = False, inverse: bool = False, monitor_index: int = 1
) -> tuple[int, int]:
    """
    Convertit des coordonnées du référentiel [0, 1000] x [0, 1000] vers les pixels réels de l'écran (ou inversement).
    Garantit l'indexation exacte dans les bornes [left, left + width - 1] et [top, top + height - 1].
    """
    if not isinstance(normalized, bool):
        raise TypeError(f"Le paramètre 'normalized' doit être un booléen, reçu : {type(normalized).__name__}")
    if not isinstance(inverse, bool):
        raise TypeError(f"Le paramètre 'inverse' doit être un booléen, reçu : {type(inverse).__name__}")
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))) or isinstance(x, bool) or isinstance(y, bool):
        raise TypeError("Les coordonnées x et y doivent être des nombres réels (int ou float).")
    if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
        raise ValueError("Les coordonnées x et y ne peuvent pas être NaN ou Infinity.")

    left, top, width, height = get_monitor_geometry(monitor_index)
    max_x = left + max(0, width - 1)
    max_y = top + max(0, height - 1)

    if inverse:
        rel_x = float(x) - float(left)
        rel_y = float(y) - float(top)
        denom_w = float(max(1, width - 1))
        denom_h = float(max(1, height - 1))
        norm_x = round(max(0.0, min(1000.0, (rel_x / denom_w) * 1000.0)))
        norm_y = round(max(0.0, min(1000.0, (rel_y / denom_h) * 1000.0)))
        return norm_x, norm_y

    if normalized:
        fx = float(x)
        if 0.0 <= fx <= 1.0:
            fx *= 1000.0
        fy = float(y)
        if 0.0 <= fy <= 1.0:
            fy *= 1000.0

        x_clamped = max(0.0, min(1000.0, fx))
        y_clamped = max(0.0, min(1000.0, fy))
        real_x = left + round((x_clamped / 1000.0) * float(max(0, width - 1)))
        real_y = top + round((y_clamped / 1000.0) * float(max(0, height - 1)))
    else:
        real_x = round(max(float(left), min(float(max_x), float(x))))
        real_y = round(max(float(top), min(float(max_y), float(y))))

    return real_x, real_y
