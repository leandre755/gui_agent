"""Utilitaires et fonctions d'enregistrement vidéo sécurisé pour vision LLM."""

from __future__ import annotations

import contextlib
import os
import subprocess
import tempfile
import threading
import time
from typing import Any

# Verrou réentrant pour synchroniser les opérations d'enregistrement vidéo
video_recording_lock = threading.Lock()


def close_subprocess_streams(proc: subprocess.Popen[Any] | None) -> None:
    """Ferme de façon défensive les flux standard d'un sous-processus."""
    if proc is None:
        return
    for stream in (proc.stdin, proc.stdout, proc.stderr):
        if stream and not stream.closed:
            with contextlib.suppress(Exception):
                stream.close()


def validate_video_recording_params(
    output_path: str | None,
    fps: int,
    monitor_index: int,
    duration: int | None,
    default_dir: str | None = None,
) -> tuple[int, int, int | None, str] | dict[str, Any]:
    """Valide et normalise les paramètres d'enregistrement vidéo."""
    if isinstance(fps, bool):
        return {"status": "error", "message": "fps doit être un entier entre 1 et 30."}
    try:
        fps_val = max(1, min(30, int(fps)))
    except (ValueError, TypeError):
        return {"status": "error", "message": "fps doit être un entier entre 1 et 30."}

    if isinstance(monitor_index, bool):
        return {"status": "error", "message": "monitor_index doit être un entier positif ou nul."}
    try:
        mon_idx = int(monitor_index)
        if mon_idx < 0:
            return {"status": "error", "message": "monitor_index doit être un entier positif ou nul."}
    except (ValueError, TypeError):
        return {"status": "error", "message": "monitor_index doit être un entier positif ou nul."}

    dur_val = None
    if duration is not None:
        if isinstance(duration, bool):
            return {"status": "error", "message": "duration doit être un entier valide."}
        try:
            dur_val = int(duration)
            if dur_val <= 0:
                return {"status": "error", "message": "duration doit être un entier strictement positif."}
        except (ValueError, TypeError):
            return {"status": "error", "message": "duration doit être un entier valide."}

    if not output_path:
        base_dir = default_dir if default_dir is not None else tempfile.gettempdir()
        timestamp = int(time.time())
        output_path = os.path.join(base_dir, f"recording_{timestamp}.mp4")

    normalized_path = os.path.abspath(os.path.expanduser(str(output_path)))
    if os.path.isdir(normalized_path):
        return {"status": "error", "message": "output_path ne peut pas être un répertoire existant."}
    if not normalized_path.lower().endswith(".mp4"):
        return {"status": "error", "message": "output_path doit comporter l'extension .mp4."}

    return fps_val, mon_idx, dur_val, normalized_path
