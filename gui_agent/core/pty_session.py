"""Gestionnaire de session PTY pour l'exécution interactive et sécurisée de sous-processus."""

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

if sys.platform != "win32":
    import pty

logger = logging.getLogger("gui_agent.core.pty")


MAX_PTY_OUTPUT_CHARS = 1_000_000


class PTYSession:
    """Session pseudo-terminal (PTY) gérant l'interaction avec stdin/stdout/stderr."""

    def __init__(self, timeout: float = 30.0, max_output_chars: int = MAX_PTY_OUTPUT_CHARS) -> None:
        self.timeout = timeout
        self.max_output_chars = max_output_chars

    def execute(
        self, cmd: list[str], stdin_payload: str | None = None, max_output_chars: int | None = None
    ) -> tuple[int, str]:
        """Exécute une commande dans un pseudo-terminal PTY isolé."""
        if sys.platform == "win32" or "pty" not in sys.modules:
            return -1, "PTY non supporté sur cette plateforme."
        limit = max_output_chars if max_output_chars is not None else self.max_output_chars
        master_fd, slave_fd = pty.openpty()
        chunks: list[str] = []
        total_chars = 0
        start = time.monotonic()
        proc: subprocess.Popen[Any] | None = None
        try:
            os.set_blocking(master_fd, False)
            proc = subprocess.Popen(
                cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, preexec_fn=os.setsid
            )
            with contextlib.suppress(OSError):
                os.close(slave_fd)
                slave_fd = -1

            payload, written, eof_sent = (stdin_payload.encode("utf-8") if stdin_payload else b""), 0, False
            while proc.poll() is None:
                if time.monotonic() - start > self.timeout:
                    _kill_pty(proc)
                    return -1, "Timeout d'exécution PTY dépassé."
                w = [master_fd] if (written < len(payload) or not eof_sent) else []
                rf, wf, _ = select.select([master_fd], w, [], 0.05)
                if wf:
                    if written < len(payload):
                        try:
                            written += os.write(master_fd, payload[written:])
                        except OSError:
                            written = len(payload)
                    elif not eof_sent:
                        eof_sent = True
                        eof = b"\x04" if (not payload or payload.endswith(b"\n")) else b"\x04\x04"
                        with contextlib.suppress(OSError):
                            os.write(master_fd, eof)
                if rf:
                    c = _read_pty(master_fd)
                    if c:
                        chunks.append(c)
                        total_chars += len(c)
                        if total_chars > limit:
                            _kill_pty(proc)
                            return -1, "Taille de sortie PTY maximale dépassée."

            while select.select([master_fd], [], [], 0.05)[0]:
                if time.monotonic() - start > self.timeout:
                    _kill_pty(proc)
                    break
                c = _read_pty(master_fd)
                if not c:
                    break
                chunks.append(c)
                total_chars += len(c)
                if total_chars > limit:
                    _kill_pty(proc)
                    return -1, "Taille de sortie PTY maximale dépassée."
            returncode = proc.wait()
        finally:
            for fd in (slave_fd, master_fd):
                with contextlib.suppress(OSError):
                    if fd >= 0:
                        os.close(fd)
            if proc is not None:
                _kill_pty(proc)
        return returncode, "".join(chunks)


def _read_pty(fd: int) -> str:
    with contextlib.suppress(OSError):
        return os.read(fd, 4096).decode("utf-8", errors="replace")
    return ""


def _kill_pty(proc: subprocess.Popen[Any]) -> None:
    with contextlib.suppress(Exception):
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=0.5)
