"""Résolution dynamique des chemins système sous Linux (spécifications XDG Base Directory).

Garantit l'agnosticisme complet de l'emplacement de gui_agent : aucun chemin utilisateur en dur,
stockage conforme sous XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME et découverte dynamique
des binaires exécutables natifs (ex. gui-agent-atspi).
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys
import tempfile


def _validate_xdg_env_path(var_name: str) -> Path | None:
    """Valide une variable d'environnement XDG selon la spécification XDG Base Directory.

    Une variable XDG doit contenir un chemin absolu. Si elle est vide, non définie
    ou relative, elle doit être ignorée et le repli par défaut utilisé.
    """
    raw = os.environ.get(var_name)
    if not raw or not raw.strip():
        return None
    raw_path = Path(raw.strip()).expanduser()
    if not raw_path.is_absolute():
        return None
    return raw_path.resolve()


def _is_secure_runtime_directory(p: Path, uid: int | None) -> bool:
    """Vérifie qu'un répertoire d'exécution est un dossier réel, non-symlink, appartenant à l'UID avec mode 0700."""
    try:
        if not p.is_dir() or p.is_symlink():
            return False
        st = p.stat()
        if uid is not None and st.st_uid != uid:
            return False
        return (st.st_mode & 0o077) == 0
    except OSError:
        return False


class LinuxPaths:
    """Gestionnaire de chemins système pour Linux conforme aux standards XDG."""

    @property
    def platform_name(self) -> str:
        return "linux"

    def get_xdg_data_home(self) -> Path:
        """XDG_DATA_HOME (défaut : $HOME/.local/share)."""
        valid = _validate_xdg_env_path("XDG_DATA_HOME")
        if valid is not None:
            return valid
        return Path(os.environ.get("HOME", "~")).expanduser().resolve() / ".local" / "share"

    def get_xdg_config_home(self) -> Path:
        """XDG_CONFIG_HOME (défaut : $HOME/.config)."""
        valid = _validate_xdg_env_path("XDG_CONFIG_HOME")
        if valid is not None:
            return valid
        return Path(os.environ.get("HOME", "~")).expanduser().resolve() / ".config"

    def get_xdg_cache_home(self) -> Path:
        """XDG_CACHE_HOME (défaut : $HOME/.cache)."""
        valid = _validate_xdg_env_path("XDG_CACHE_HOME")
        if valid is not None:
            return valid
        return Path(os.environ.get("HOME", "~")).expanduser().resolve() / ".cache"

    def get_xdg_runtime_dir(self) -> Path:
        """XDG_RUNTIME_DIR (défaut : /run/user/$UID ou /tmp/gui-agent-$UID sécurisé)."""
        uid = os.getuid() if hasattr(os, "getuid") else None
        valid_xdg = _validate_xdg_env_path("XDG_RUNTIME_DIR")
        if valid_xdg is not None and _is_secure_runtime_directory(valid_xdg, uid):
            return valid_xdg

        if uid is not None:
            user_run = Path(f"/run/user/{uid}")
            if _is_secure_runtime_directory(user_run, uid):
                return user_run

        temp_dir = Path(tempfile.gettempdir())
        fallback_dir = temp_dir / (f"gui-agent-{uid}" if uid is not None else "gui-agent")
        try:
            if fallback_dir.is_symlink():
                try:
                    fallback_dir.unlink()
                except OSError:
                    return Path(tempfile.mkdtemp(prefix=f"gui-agent-{uid or 'safe'}-"))
            if fallback_dir.exists():
                st = fallback_dir.stat()
                if uid is not None and st.st_uid != uid:
                    return Path(tempfile.mkdtemp(prefix=f"gui-agent-{uid}-"))
                if (st.st_mode & 0o077) != 0:
                    fallback_dir.chmod(0o700)
            else:
                fallback_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                fallback_dir.chmod(0o700)
        except OSError:
            return Path(tempfile.mkdtemp(prefix=f"gui-agent-{uid or 'safe'}-"))
        return fallback_dir

    def get_data_dir(self) -> Path:
        """Répertoire persistant de données pour gui-agent."""
        return self.get_xdg_data_home() / "gui-agent"

    def get_config_dir(self) -> Path:
        """Répertoire de configuration pour gui-agent."""
        return self.get_xdg_config_home() / "gui-agent"

    def get_cache_dir(self) -> Path:
        """Répertoire de cache général pour gui-agent."""
        return self.get_xdg_cache_home() / "gui-agent"

    def get_screenshots_dir(self) -> Path:
        """Répertoire dynamique des captures d'écran."""
        env_val = os.environ.get("GUI_AGENT_SCREENSHOTS_DIR")
        if env_val and env_val.strip():
            return Path(env_val).expanduser().resolve()
        return self.get_cache_dir() / "screenshots"

    def get_videos_dir(self) -> Path:
        """Répertoire dynamique des enregistrements vidéo."""
        env_val = os.environ.get("GUI_AGENT_VIDEOS_DIR")
        if env_val and env_val.strip():
            return Path(env_val).expanduser().resolve()
        return self.get_cache_dir() / "videos"

    def get_binary_install_dir(self) -> Path:
        """Répertoire d'installation standard pour les binaires exécutables."""
        if sys.prefix != sys.base_prefix:
            return Path(sys.prefix) / "bin"
        return Path(os.environ.get("HOME", "~")).expanduser().resolve() / ".local" / "bin"

    def get_binary_candidates(self, binary_name: str) -> list[Path]:
        """Retourne la liste ordonnée des chemins candidats de découverte du binaire."""
        candidates: list[Path] = []

        # 1. Variables d'environnement prioritaires
        clean_name = binary_name.replace("-", "_").replace(".", "_").upper()
        short_name = clean_name[len("GUI_AGENT_") :] if clean_name.startswith("GUI_AGENT_") else clean_name
        for env_var in (
            f"GUI_AGENT_{short_name}_BIN",
            f"GUI_AGENT_{clean_name}_BIN",
            "GUI_AGENT_LINUX_BIN",
            "GUI_AGENT_BIN",
        ):
            val = os.environ.get(env_var)
            if val and val.strip():
                candidates.append(Path(val).expanduser().resolve())

        # 2. Cibles de compilation Cargo locale (release puis debug)
        base_dir = Path(__file__).resolve().parent.parent
        for profile in ("release", "debug"):
            candidates.append(base_dir / "target" / profile / binary_name)
            candidates.append(base_dir / "crates" / "atspi_mediator" / "target" / profile / binary_name)
            candidates.append(base_dir / "linux" / "crates" / "atspi_mediator" / "target" / profile / binary_name)

        # 3. Binaire packagé directement dans le package Python (gui_agent/bin/...)
        package_bin_dir = Path(__file__).resolve().parent / "bin"
        candidates.append(package_bin_dir / binary_name)

        # 4. Environnement virtuel actif (sys.prefix/bin)
        candidates.append(Path(sys.prefix) / "bin" / binary_name)

        # 5. Répertoire utilisateur ~/.local/bin
        candidates.append(Path(os.environ.get("HOME", "~")).expanduser().resolve() / ".local" / "bin" / binary_name)

        # 6. Recherche PATH système via shutil.which
        which_path = shutil.which(binary_name)
        if which_path:
            candidates.append(Path(which_path).resolve())

        # 7. Répertoires système standards
        for sys_dir in ("/usr/local/bin", "/usr/bin", "/bin"):
            candidates.append(Path(sys_dir) / binary_name)

        # Déduplication avec préservation de l'ordre
        seen: set[str] = set()
        deduped: list[Path] = []
        for p in candidates:
            str_p = str(p)
            if str_p not in seen:
                seen.add(str_p)
                deduped.append(p)

        return deduped

    def find_binary(self, binary_name: str) -> Path | None:
        """Trouve le premier binaire exécutable valide parmi les candidats."""
        for candidate in self.get_binary_candidates(binary_name):
            try:
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    return candidate
            except (OSError, PermissionError):
                continue
        return None

    def ensure_dirs(self) -> None:
        """Crée tous les répertoires nécessaires avec gestion des permissions."""
        for d in (
            self.get_data_dir(),
            self.get_config_dir(),
            self.get_cache_dir(),
            self.get_screenshots_dir(),
            self.get_videos_dir(),
        ):
            d.mkdir(parents=True, exist_ok=True)


# Instance globale Linux
_paths = LinuxPaths()


def get_paths() -> LinuxPaths:
    """Retourne l'instance des chemins Linux."""
    return _paths


def get_screenshots_dir() -> str:
    """Retourne le chemin absolu du répertoire de captures d'écran."""
    p = _paths.get_screenshots_dir()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def get_videos_dir() -> str:
    """Retourne le chemin absolu du répertoire des enregistrements vidéo."""
    p = _paths.get_videos_dir()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def get_cache_dir() -> str:
    """Retourne le chemin absolu du cache."""
    p = _paths.get_cache_dir()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def get_data_dir() -> str:
    """Retourne le chemin absolu des données."""
    p = _paths.get_data_dir()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def get_config_dir() -> str:
    """Retourne le chemin absolu de configuration."""
    p = _paths.get_config_dir()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def get_binary_install_dir() -> str:
    """Retourne le répertoire d'installation des binaires."""
    p = _paths.get_binary_install_dir()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def find_platform_binary(binary_name: str) -> str | None:
    """Recherche un binaire exécutable natif."""
    found = _paths.find_binary(binary_name)
    return str(found) if found else None


__all__ = [
    "LinuxPaths",
    "find_platform_binary",
    "get_binary_install_dir",
    "get_cache_dir",
    "get_config_dir",
    "get_data_dir",
    "get_paths",
    "get_screenshots_dir",
    "get_videos_dir",
]
