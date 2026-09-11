"""Moteur d'exécution local CodeAct : Exécute des scripts Python/Bash avec mcp_core préchargé."""

from __future__ import annotations

import contextlib
import logging
import os
import select
import signal
import subprocess
import sys
import time
from typing import Any

logger = logging.getLogger("gui_agent.core.repl")
MAX_OUTPUT_CHARS = 1_000_000
RUNNER_HARNESS = (
    "import sys, os\nsys.path.insert(0, os.getcwd())\n"
    "import gui_agent.core.mcp_core as _sdk\nsys.modules['mcp_core'] = sys.modules['gui_agent.core.mcp_core']\n"
    "code = sys.stdin.read()\nexec(compile(code, '<repl>', 'exec'), {'__name__': '__main__', 'mcp_core': _sdk})\n"
)


def execute_script(code: str, timeout: float = 30.0, max_output_chars: int = MAX_OUTPUT_CHARS) -> dict[str, Any]:
    """Exécute un script Python localement dans un processus isolé avec mcp_core préchargé."""
    if not code or not code.strip():
        return {"status": "error", "message": "Code à exécuter vide."}
    start = time.monotonic()
    status, err = "success", None
    out_ch: list[str] = []
    err_ch: list[str] = []
    try:
        proc = subprocess.Popen(
            [sys.executable, "-c", RUNNER_HARNESS],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        if proc.stdin is None or proc.stdout is None or proc.stderr is None:
            return {"status": "error", "message": "Échec d'ouverture des flux d'exécution."}
        in_fd, out_fd, err_fd = proc.stdin.fileno(), proc.stdout.fileno(), proc.stderr.fileno()
        for fd in (in_fd, out_fd, err_fd):
            os.set_blocking(fd, False)
        inp, off, in_closed, out_len, err_len, readers = code.encode("utf-8"), 0, False, 0, 0, [out_fd, err_fd]

        while True:
            el = time.monotonic() - start
            if el > timeout:
                _kill_proc(proc)
                status, err = "error", f"Timeout ({timeout}s)."
                break
            wl = [in_fd] if (not in_closed and off < len(inp)) else []
            if not readers and not wl:
                if proc.poll() is None:
                    try:
                        proc.wait(timeout=max(0.01, timeout - el))
                    except subprocess.TimeoutExpired:
                        _kill_proc(proc)
                        status, err = "error", f"Timeout ({timeout}s)."
                break
            r, w, _ = select.select(readers, wl, [], min(max(0.01, timeout - el), 0.05))
            if w and not in_closed:
                try:
                    off += os.write(in_fd, inp[off:])
                    if off >= len(inp):
                        proc.stdin.close()
                        in_closed = True
                except OSError:
                    proc.stdin.close()
                    in_closed = True
            for fd in r:
                chunk = _safe_read(fd)
                if not chunk:
                    if fd in readers:
                        readers.remove(fd)
                    continue
                (out_ch if fd == out_fd else err_ch).append(chunk)
                out_len += len(chunk) if fd == out_fd else 0
                err_len += len(chunk) if fd != out_fd else 0
                if out_len > max_output_chars or err_len > max_output_chars:
                    _kill_proc(proc)
                    status, err = "error", f"Taille de sortie maximale dépassée ({max_output_chars} caractères)."
                    break
            if err or (proc.poll() is not None and not r):
                break

        for fd in readers:
            c = _safe_read(fd)
            if c:
                (out_ch if fd == out_fd else err_ch).append(c)
        with contextlib.suppress(Exception):
            proc.wait(timeout=0.5)
        for s in (proc.stdin, proc.stdout, proc.stderr):
            with contextlib.suppress(Exception):
                if s:
                    s.close()
        if proc.returncode != 0 and status == "success":
            status, err = "error", "".join(err_ch).strip() or f"Code {proc.returncode}"
    except Exception as exc:
        status, err = "error", f"{type(exc).__name__}: {exc!s}"

    dur = round((time.monotonic() - start) * 1000, 2)
    res: dict[str, Any] = {"status": status, "stdout": "".join(out_ch), "stderr": "".join(err_ch), "duration_ms": dur}
    if err:
        res["error"] = err
    return res


def _safe_read(fd: int) -> str:
    with contextlib.suppress(OSError):
        return os.read(fd, 4096).decode("utf-8", errors="replace")
    return ""


def _kill_proc(proc: subprocess.Popen[str]) -> None:
    with contextlib.suppress(Exception):
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=0.5)
