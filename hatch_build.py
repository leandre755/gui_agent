"""Hatchling custom build hook pour gui-agent.

Compile automatiquement le médiateur Rust natif gui-agent-atspi lors de la
construction de la wheel (pip install ., uv tool install git+..., python -m build)
afin d'embarquer le binaire natif dans le paquet distribuable.
"""

from __future__ import annotations

import contextlib
import logging
import os
import platform
import shutil
import stat
import subprocess
import sys
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logger = logging.getLogger(__name__)


class CustomBuildHook(BuildHookInterface):
    """Hook de construction personnalisée pour compiler le médiateur AT-SPI Rust."""

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Initialise la compilation Rust et copie le binaire dans linux/bin/."""
        project_root = self.root
        cargo_bin = shutil.which("cargo")
        cargo_manifest = os.path.join(project_root, "Cargo.toml")

        dest_dir = os.path.join(project_root, "linux", "bin")
        os.makedirs(dest_dir, exist_ok=True)
        dest_bin = os.path.join(dest_dir, "gui-agent-atspi")

        if sys.platform.startswith("linux") and cargo_bin and os.path.isfile(cargo_manifest):
            # Nettoyer l'artefact de destination préalable uniquement avant recompilation
            if os.path.exists(dest_bin):
                with contextlib.suppress(OSError):
                    os.remove(dest_bin)

            target_dir = os.environ.get("CARGO_TARGET_DIR") or os.path.join(project_root, "target")
            try:
                subprocess.run(
                    [
                        cargo_bin,
                        "build",
                        "--release",
                        "--manifest-path",
                        cargo_manifest,
                        "--bin",
                        "gui-agent-atspi",
                        "--target-dir",
                        target_dir,
                    ],
                    cwd=project_root,
                    capture_output=True,
                    check=True,
                )
            except Exception as exc:
                raise RuntimeError(f"Échec de la compilation préalable du médiateur Rust via Cargo: {exc}") from exc

            built_bin = os.path.join(target_dir, "release", "gui-agent-atspi")
            if not os.path.isfile(built_bin):
                raise RuntimeError(f"L'artefact compilé attendu est introuvable après cargo build: {built_bin}")

            shutil.copy2(built_bin, dest_bin)
            mode = os.stat(dest_bin).st_mode
            os.chmod(dest_bin, mode | stat.S_IXUSR)

            # Le binaire natif ELF est embarqué : marquer la wheel avec le tag de plateforme exact de l'hôte
            # sans revendiquer abusivement la conformité manylinux/musllinux non auditée
            build_data["pure_python"] = False
            plat = f"linux_{platform.machine().lower()}"
            build_data["tag"] = f"py3-none-{plat}"
        else:
            # Aucun binaire natif embarqué : garantir une wheel pure Python cohérente
            if os.path.exists(dest_bin):
                with contextlib.suppress(OSError):
                    os.remove(dest_bin)
