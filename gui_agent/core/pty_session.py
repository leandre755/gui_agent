"""Gestionnaire de session PTY pour l'exécution interactive et sécurisée de sous-processus."""

from __future__ import annotations

import contextlib
import logging
import os
import pty
import select
import signal
import subprocess
import time
from typing import Any

logger = logging.getLogger("gui_agent.core.pty")


class PTYSession:
    """Session pseudo-terminal (PTY) gérant l'interaction avec stdin/stdout/stderr."""

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    def execute(self, cmd: list[str], stdin_payload: str | None = None) -> tuple[int, str]:
        """Exécute une commande dans un pseudo-terminal PTY isolé."""
        master_fd, slave_fd = pty.openpty()
        chunks: list[str] = []
        returncode = -1
        proc: subprocess.Popen[Any] | None = None
        start = time.monotonic()
        try:
            os.set_blocking(master_fd, False)
            proc = subprocess.Popen(
                cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, preexec_fn=os.setsid
            )
            with contextlib.suppress(OSError):
                os.close(slave_fd)
                slave_fd = -1

            payload = stdin_payload.encode("utf-8") if stdin_payload else b""
            written = 0
            while proc.poll() is None:
                if time.monotonic() - start > self.timeout:
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=0.2)
                    except subprocess.TimeoutExpired:
                        with contextlib.suppress(ProcessLookupError):
                            os.killpg(proc.pid, signal.SIGKILL)
                        with contextlib.suppress(Exception):
                            proc.wait(timeout=1.0)
                    return -1, "Timeout d'exécution PTY dépassé."

                wlist = [master_fd] if written < len(payload) else []
                r, w, _ = select.select([master_fd], wlist, [], 0.05)
                if w and written < len(payload):
                    with contextlib.suppress(OSError):
                        n = os.write(master_fd, payload[written:])
                        written += n
                if r:
                    with contextlib.suppress(OSError):
                        data = os.read(master_fd, 4096)
                        if data:
                            chunks.append(data.decode("utf-8", errors="replace"))

            while select.select([master_fd], [], [], 0.05)[0]:
                with contextlib.suppress(OSError):
                    data = os.read(master_fd, 4096)
                    if not data:
                        break
                    chunks.append(data.decode("utf-8", errors="replace"))
            returncode = proc.wait()
        finally:
            if slave_fd >= 0:
                with contextlib.suppress(OSError):
                    os.close(slave_fd)
            with contextlib.suppress(OSError):
                os.close(master_fd)
            if proc is not None and proc.poll() is None:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGKILL)
                with contextlib.suppress(Exception):
                    proc.wait(timeout=0.5)
        return returncode, "".join(chunks)
