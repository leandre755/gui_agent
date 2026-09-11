"""Gestionnaire de session PTY pour l'exécution interactive et sécurisée de sous-processus."""

from __future__ import annotations

import contextlib
import logging
import os
import pty
import select
import subprocess
import time

logger = logging.getLogger("gui_agent.core.pty")


class PTYSession:
    """Session pseudo-terminal (PTY) gérant l'interaction avec stdin/stdout/stderr."""

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    def execute(self, cmd: list[str], stdin_payload: str | None = None) -> tuple[int, str]:
        """Exécute une commande dans un pseudo-terminal PTY isolé."""
        master_fd, slave_fd = pty.openpty()
        output_chunks: list[str] = []
        returncode = -1

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True,
                preexec_fn=os.setsid,
            )
            os.close(slave_fd)

            if stdin_payload:
                os.write(master_fd, stdin_payload.encode("utf-8"))

            start_time = time.monotonic()
            while proc.poll() is None:
                if time.monotonic() - start_time > self.timeout:
                    proc.kill()
                    return -1, "Timeout d'exécution PTY dépassé."

                r, _, _ = select.select([master_fd], [], [], 0.1)
                if master_fd in r:
                    try:
                        data = os.read(master_fd, 4096)
                        if data:
                            output_chunks.append(data.decode("utf-8", errors="replace"))
                    except OSError:
                        break

            # Lecture finale des reliquats
            while True:
                r, _, _ = select.select([master_fd], [], [], 0.05)
                if master_fd in r:
                    try:
                        data = os.read(master_fd, 4096)
                        if not data:
                            break
                        output_chunks.append(data.decode("utf-8", errors="replace"))
                    except OSError:
                        break
                else:
                    break

            returncode = proc.wait()
        finally:
            with contextlib.suppress(OSError):
                os.close(master_fd)

        return returncode, "".join(output_chunks)
