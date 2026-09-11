"""Moteur d'exécution local CodeAct : Exécute des scripts Python/Bash avec mcp_core préchargé."""

from __future__ import annotations

import contextlib
import logging
import os
import signal
import subprocess
import sys
import time
from typing import Any

logger = logging.getLogger("gui_agent.core.repl")


def execute_script(code: str, timeout: float = 30.0) -> dict[str, Any]:
    """Exécute un script Python localement dans un processus isolé avec mcp_core préchargé."""
    if not code or not code.strip():
        return {"status": "error", "message": "Code à exécuter vide."}
    start = time.monotonic()
    futures = [ln for ln in code.splitlines(keepends=True) if ln.strip().startswith("from __future__ import")]
    body = "".join(ln for ln in code.splitlines(keepends=True) if not ln.strip().startswith("from __future__ import"))
    runner = (
        "".join(futures) + "import sys, os, time\nsys.path.insert(0, os.getcwd())\n"
        "import gui_agent.core.mcp_core as _mcp\nsys.modules['mcp_core'] = _mcp\n"
        f"from gui_agent.core.mcp_core import mcp_core\n{body}"
    )
    stdout, stderr, status, err = "", "", "success", None
    try:
        proc = subprocess.Popen(
            [sys.executable, "-c", runner],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=max(0.1, float(timeout)))
            if proc.returncode != 0:
                status, err = "error", stderr.strip() or f"Code {proc.returncode}"
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGKILL)
            with contextlib.suppress(Exception):
                proc.wait(timeout=1.0)
            status, err = "error", f"Timeout ({timeout}s)."
    except Exception as exc:
        status, err = "error", f"{type(exc).__name__}: {exc!s}"

    dur = round((time.monotonic() - start) * 1000, 2)
    res: dict[str, Any] = {"status": status, "stdout": stdout, "stderr": stderr, "duration_ms": dur}
    if err:
        res["error"] = err
    return res
