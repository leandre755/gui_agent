"""Algorithmes cinématiques et temporisation pseudo-aléatoire mimant le comportement humain."""

from __future__ import annotations

import random
import time


def sleep_human(base_delay: float = 0.05) -> None:
    """Introduit un délai pseudo-aléatoire réaliste pour simuler un humain."""
    if not isinstance(base_delay, (int, float)) or base_delay < 0:
        base_delay = 0.05

    jitter = random.normalvariate(base_delay, base_delay * 0.3)
    time.sleep(max(0.01, jitter))


def type_char_human(char: str, base_delay: float = 0.06) -> bool:
    """Simule la frappe d'un caractère avec temporisation naturelle."""
    if not isinstance(char, str) or len(char) != 1:
        return False
    sleep_human(base_delay)
    return True


def translate_key(key: str) -> str:
    """Traduit les touches système abrégées en symboles standards X11/evdev."""
    if not isinstance(key, str) or len(key) == 0:
        return ""
    key_map = {
        "super": "Super_L",
        "win": "Super_L",
        "enter": "Return",
        "return": "Return",
        "escape": "Escape",
        "esc": "Escape",
        "backspace": "BackSpace",
        "tab": "Tab",
        "space": "space",
        "ctrl": "control",
        "control": "control",
        "alt": "alt",
        "shift": "shift",
        "up": "Up",
        "down": "Down",
        "left": "Left",
        "right": "Right",
    }
    return key_map.get(key.lower(), key)


def generate_smooth_path(start_x: int, start_y: int, end_x: int, end_y: int, steps: int = 20) -> list[tuple[int, int]]:
    """Génère une trajectoire cinématique continue interpolée entre deux points."""
    if steps <= 1:
        return [(start_x, start_y), (end_x, end_y)]

    points: list[tuple[int, int]] = []
    for i in range(steps + 1):
        t = i / float(steps)
        # Courbe sigmoïde douce (smoothstep) : 3t^2 - 2t^3
        smooth_t = t * t * (3.0 - 2.0 * t)
        curr_x = round(start_x + (end_x - start_x) * smooth_t)
        curr_y = round(start_y + (end_y - start_y) * smooth_t)
        points.append((curr_x, curr_y))
    return points
