"""Configuration pytest et chargement direct du package gui_agent depuis linux/.

Permet d'importer `gui_agent` et ses sous-modules directement depuis le répertoire `linux/`
sans nécessiter de dossier physique `gui_agent/` ni de symlink à la racine du projet.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import sys

linux_dir = Path(__file__).resolve().parent.parent
project_root = linux_dir.parent

if str(linux_dir) not in sys.path:
    sys.path.insert(0, str(linux_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if "gui_agent" not in sys.modules:
    loader = importlib.machinery.SourceFileLoader("gui_agent", str(linux_dir / "__init__.py"))
    spec = importlib.util.spec_from_loader("gui_agent", loader, origin=str(linux_dir / "__init__.py"))
    if spec is not None:
        spec.submodule_search_locations = [str(linux_dir)]
        mod = importlib.util.module_from_spec(spec)
        sys.modules["gui_agent"] = mod
        loader.exec_module(mod)
