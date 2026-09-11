"""Algorithmes cinématiques et temporisation pseudo-aléatoire mimant l'humain."""

from __future__ import annotations

import math
import os
import random
import shutil
import subprocess
import time


def sleep_human(base_delay: float = 0.05) -> None:
    """Introduit un délai pseudo-aléatoire réaliste."""
    if not isinstance(base_delay, (int, float)) or not math.isfinite(base_delay) or base_delay < 0:
        delay = 0.05
    else:
        delay = float(base_delay)
    val = random.normalvariate(delay, delay * 0.3)
    if not math.isfinite(val):
        val = delay
    time.sleep(max(0.01, min(60.0, val)))


def type_char_human(char: str, base_delay: float = 0.06) -> bool:
    """Simule la frappe d'un caractère avec temporisation naturelle."""
    if not isinstance(char, str) or len(char) != 1:
        return False
    sleep_human(base_delay)
    xdotool_bin = shutil.which("xdotool") or "xdotool"
    try:
        env = os.environ.copy()
        env["DISPLAY"] = env.get("DISPLAY", ":0")
        res = subprocess.run([xdotool_bin, "type", char], env=env, capture_output=True, check=False, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def translate_key(key: str) -> str:
    """Traduit les touches système abrégées en symboles standards."""
    if not isinstance(key, str) or not key:
        return ""
    km = {
        "super": "Super_L",
        "win": "Super_L",
        "enter": "Return",
        "return": "Return",
        "ctrl": "control",
        "escape": "Escape",
        "esc": "Escape",
    }
    return km.get(key.lower(), key)


def generate_smooth_path(start_x: int, start_y: int, end_x: int, end_y: int, steps: int = 20) -> list[tuple[int, int]]:
    """Génère une trajectoire cinématique continue interpolée entre deux points."""
    if steps <= 1:
        return [(start_x, start_y), (end_x, end_y)]
    res = []
    for i in range(steps + 1):
        t = (i / steps) ** 2 * (3.0 - 2.0 * (i / steps))
        res.append((round(start_x + (end_x - start_x) * t), round(start_y + (end_y - start_y) * t)))
    return res
