"""Moteur d'exécution local CodeAct : Exécute des scripts Python/Bash avec mcp_core préchargé."""

from __future__ import annotations

import io
import logging
import sys
import time
from typing import Any
from gui_agent.core.mcp_core import mcp_core

logger = logging.getLogger("gui_agent.core.repl")


def execute_script(code: str, timeout: float = 30.0) -> dict[str, Any]:
    """
    Exécute un script Python localement dans un environnement où le SDK `mcp_core` est préchargé.
    Élimine la latence RTT en permettant des boucles d'attente à 100 Hz en 1 seul aller-retour LLM.
    """
    if not code or not code.strip():
        return {"status": "error", "message": "Code à exécuter vide."}

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    start_time = time.monotonic()

    # Namespace d'exécution préchargé
    exec_globals: dict[str, Any] = {
        "__builtins__": __builtins__,
        "mcp_core": mcp_core,
        "time": time,
    }

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout_capture
    sys.stderr = stderr_capture

    status = "success"
    error_message: str | None = None

    try:
        # TODO(#131): Isolation de processus via PTYSession pour les boucles lourdes ou scripts Bash
        exec(code, exec_globals)
    except Exception as exc:
        status = "error"
        error_message = f"{type(exc).__name__}: {exc!s}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    duration_ms = round((time.monotonic() - start_time) * 1000, 2)
    output = stdout_capture.getvalue()
    err_output = stderr_capture.getvalue()

    result: dict[str, Any] = {
        "status": status,
        "stdout": output,
        "stderr": err_output,
        "duration_ms": duration_ms,
    }
    if error_message:
        result["error"] = error_message

    return result
