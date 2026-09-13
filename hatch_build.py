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
import tempfile
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logger = logging.getLogger(__name__)


def _detect_linux_platform_tag() -> str:
    """Détermine le tag de compatibilité manylinux ou musllinux audité de la plateforme hôte."""
    try:
        import packaging.tags as p_tags

        for t in p_tags.sys_tags():
            if t.platform.startswith(("manylinux", "musllinux")):
                return t.platform
    except Exception as exc:
        logger.debug("Échec de détection packaging.tags: %s", exc)

    libc_name, libc_version = platform.libc_ver()
    arch = platform.machine().lower()
    if libc_name == "glibc" and libc_version:
        parts = libc_version.split(".")
        if len(parts) >= 2:
            return f"manylinux_{parts[0]}_{parts[1]}_{arch}"
    elif "musl" in sys.version.lower() or os.path.exists("/lib/ld-musl-x86_64.so.1"):
        return f"musllinux_1_2_{arch}"

    raise RuntimeError(
        f"Impossible de déterminer un tag de compatibilité manylinux ou musllinux audité pour l'hôte "
        f"({libc_name} {libc_version} {arch})."
    )


class CustomBuildHook(BuildHookInterface):
    """Hook de construction personnalisée pour compiler le médiateur AT-SPI Rust."""

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Initialise la compilation Rust et copie le binaire dans linux/bin/."""
        project_root = self.root

        if version == "editable":
            self.build_config.target_config["dev-mode-dirs"] = ["linux"]
            shim_content = f'''"""Editable installation shim for gui_agent pointing to linux/."""
import os

_linux_dir = os.path.abspath({os.path.join(project_root, "linux")!r})
__path__ = [_linux_dir]
__file__ = os.path.join(_linux_dir, "__init__.py")

if os.path.isfile(__file__):
    with open(__file__, encoding="utf-8") as _f:
        exec(compile(_f.read(), __file__, "exec"))
'''
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".py", delete=False) as shim:
                shim.write(shim_content)
                shim.flush()
                self._shim_file = shim.name

            if "force_include_editable" not in build_data:
                build_data["force_include_editable"] = {}
            build_data["force_include_editable"][self._shim_file] = "gui_agent/__init__.py"
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

            # Le binaire natif ELF est embarqué : marquer la wheel avec un tag de compatibilité audité (manylinux / musllinux)
            build_data["pure_python"] = False
            plat = _detect_linux_platform_tag()
            build_data["tag"] = f"py3-none-{plat}"
        else:
            # Aucun binaire natif embarqué : garantir une wheel pure Python cohérente
            if os.path.exists(dest_bin):
                with contextlib.suppress(OSError):
                    os.remove(dest_bin)

    def finalize(self, version: str, build_data: dict[str, Any], artifact_path: str) -> None:
        """Nettoie les artefacts temporaires après la construction."""
        shim = getattr(self, "_shim_file", None)
        if shim and os.path.exists(shim):
            with contextlib.suppress(OSError):
                os.remove(shim)
            self._shim_file = None

    def clean(self, versions: list[str]) -> None:
        """Nettoie les fichiers temporaires du hook."""
        shim = getattr(self, "_shim_file", None)
        if shim and os.path.exists(shim):
            with contextlib.suppress(OSError):
                os.remove(shim)
            self._shim_file = None
