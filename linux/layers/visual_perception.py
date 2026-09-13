"""Couche de Perception Visuelle & Reconnaissance Optique (OCR)."""

from __future__ import annotations

import logging

logger = logging.getLogger("gui_agent.layers.visual_perception")


def find_text(text: str, confidence: float = 0.85) -> dict[str, int] | None:
    """Analyse le framebuffer local via OCR (RapidOCR) et renvoie les coordonnées (x, y)."""
    return None
