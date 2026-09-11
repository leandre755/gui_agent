"""Couche de Perception Visuelle & Reconnaissance Optique (OCR) : Localisation spatiale sur le framebuffer."""

from __future__ import annotations

import logging

logger = logging.getLogger("gui_agent.layers.visual_perception")


def find_text(text: str, confidence: float = 0.85) -> dict[str, int] | None:
    """
    Analyse le framebuffer local via OCR (RapidOCR) et renvoie les coordonnées (x, y) du centre du texte.
    Permet d'isoler spatialement les éléments textuels sans imposer l'ingestion de flux d'images brutes au modèle.
    """
    if not text or not text.strip():
        return None
    # TODO(#132): Implémentation du moteur RapidOCR avec onnxruntime
    logger.debug(f"Perception visuelle : recherche du texte '{text}' avec seuil de confiance >= {confidence}")
    return None
