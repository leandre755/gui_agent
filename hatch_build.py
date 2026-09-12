"""Hatchling custom build hook pour gui-agent.

Compile automatiquement le médiateur Rust natif gui-agent-atspi lors de la
construction de la wheel (pip install ., uv tool install git+..., python -m build)
afin d'embarquer le binaire natif dans le paquet distribuable.
"""

from __future__ import annotations

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
        """Initialise la compilation Rust et copie le binaire dans gui_agent/bin/."""
        project_root = self.root
        cargo_bin = shutil.which("cargo")
        cargo_manifest = os.path.join(project_root, "Cargo.toml")

        if cargo_bin and os.path.isfile(cargo_manifest):
            try:
                subprocess.run(
                    [cargo_bin, "build", "--release", "--manifest-path", cargo_manifest, "--bin", "gui-agent-atspi"],
                    cwd=project_root,
                    capture_output=True,
                    check=True,
                )
                built_bin = os.path.join(project_root, "target", "release", "gui-agent-atspi")
                dest_dir = os.path.join(project_root, "gui_agent", "bin")
                os.makedirs(dest_dir, exist_ok=True)
                dest_bin = os.path.join(dest_dir, "gui-agent-atspi")
                if os.path.isfile(built_bin):
                    shutil.copy2(built_bin, dest_bin)
                    mode = os.stat(dest_bin).st_mode
                    os.chmod(dest_bin, mode | stat.S_IXUSR)

                    # Le binaire natif ELF est embarqué : marquer la wheel comme spécifique à la plateforme/architecture
                    build_data["pure_python"] = False
                    try:
                        from packaging.tags import sys_tags

                        plat = next(
                            iter(
                                t.platform
                                for t in sys_tags()
                                if "manylinux" not in t.platform and "musllinux" not in t.platform
                            )
                        )
                    except Exception:
                        plat = f"{sys.platform}_{platform.machine().lower()}"
                    build_data["tag"] = f"py3-none-{plat}"
            except Exception as exc:
                logger.debug("Échec de la compilation préalable du médiateur Rust via Hatchling: %s", exc)
