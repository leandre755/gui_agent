"""Utilitaires d'enregistrement vidéo sécurisé pour vision LLM."""

from __future__ import annotations

import contextlib
import os
import subprocess
import tempfile
import threading
import uuid
from typing import Any

video_recording_lock = threading.Lock()


def close_subprocess_streams(proc: subprocess.Popen[Any] | None) -> None:
    """Ferme de façon défensive les flux standard d'un sous-processus."""
    if proc is None:
        return
    for s in (proc.stdin, proc.stdout, proc.stderr):
        if s and not s.closed:
            with contextlib.suppress(Exception):
                s.close()


def validate_video_recording_params(
    output_path: str | None,
    fps: int,
    monitor_index: int,
    duration: int | None,
    default_dir: str | None = None,
) -> tuple[int, int, int | None, str] | dict[str, Any]:
    """Valide et normalise les paramètres d'enregistrement vidéo."""
    try:
        if isinstance(fps, bool) or not (1 <= int(fps) <= 30):
            return {"status": "error", "message": "fps doit être un entier entre 1 et 30."}
        fps_val = int(fps)
    except (ValueError, TypeError):
        return {"status": "error", "message": "fps doit être un entier entre 1 et 30."}

    try:
        if isinstance(monitor_index, bool) or int(monitor_index) < 0:
            return {"status": "error", "message": "monitor_index doit être un entier positif ou nul."}
        mon_idx = int(monitor_index)
    except (ValueError, TypeError):
        return {"status": "error", "message": "monitor_index doit être un entier positif ou nul."}

    dur_val = None
    if duration is not None:
        try:
            if isinstance(duration, bool) or int(duration) <= 0:
                return {"status": "error", "message": "duration doit être un entier strictement positif."}
            dur_val = int(duration)
        except (ValueError, TypeError):
            return {"status": "error", "message": "duration doit être un entier valide."}

    path = output_path or os.path.join(default_dir or tempfile.gettempdir(), f"recording_{uuid.uuid4().hex}.mp4")
    norm_path = os.path.abspath(os.path.expanduser(str(path)))
    if os.path.isdir(norm_path):
        return {"status": "error", "message": "output_path ne peut pas être un répertoire existant."}
    if not norm_path.lower().endswith(".mp4"):
        return {"status": "error", "message": "output_path doit comporter l'extension .mp4."}
    return fps_val, mon_idx, dur_val, norm_path
