"""Tests pour l'architecture racine Linux et la résolution dynamique des chemins."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from gui_agent.paths import (
    LinuxPaths,
    find_platform_binary,
    get_binary_install_dir,
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_screenshots_dir,
    get_videos_dir,
)


def test_root_directories_structure() -> None:
    """Valide l'arborescence à la racine : linux contenant le code, windows et macos vides."""
    root = Path(__file__).resolve().parent.parent.parent

    # 1. Répertoire linux contenant directement le code, les tests et les exemples
    linux_dir = root / "linux"
    assert linux_dir.is_dir(), "Répertoire linux/ manquant à la racine"
    assert not (linux_dir / "gui_agent").exists(), "linux/gui_agent ne doit pas exister (pas de nesting redondant)"
    assert (linux_dir / "core").is_dir(), "linux/core manquant"
    assert (linux_dir / "layers").is_dir(), "linux/layers manquant"
    assert (linux_dir / "utils").is_dir(), "linux/utils manquant"
    assert (linux_dir / "tests").is_dir(), "linux/tests manquant"
    assert (linux_dir / "examples").is_dir(), "linux/examples manquant"
    assert (linux_dir / "server.py").is_file(), "linux/server.py manquant"
    assert (linux_dir / "mcp_gui_server.py").is_file(), "linux/mcp_gui_server.py manquant"
    assert (linux_dir / "install.sh").is_file(), "linux/install.sh manquant"
    assert (linux_dir / "uninstall.sh").is_file(), "linux/uninstall.sh manquant"
    assert (linux_dir / "paths.py").is_file(), "linux/paths.py manquant"
    assert (linux_dir / "accessibility.py").is_file(), "linux/accessibility.py manquant"
    assert (linux_dir / "input.py").is_file(), "linux/input.py manquant"
    assert (linux_dir / "window.py").is_file(), "linux/window.py manquant"

    # 2. Répertoires windows et macos
    windows_dir = root / "windows"
    assert windows_dir.is_dir(), "Répertoire windows/ manquant à la racine"
    win_files = {f.name for f in windows_dir.iterdir() if f.name != "__pycache__"}
    assert win_files.issubset({".gitkeep", "install.ps1", "uninstall.ps1"}), (
        f"windows/ ne doit contenir que .gitkeep et scripts d'installation : {win_files}"
    )

    macos_dir = root / "macos"
    assert macos_dir.is_dir(), "Répertoire macos/ manquant à la racine"
    mac_files = [f.name for f in macos_dir.iterdir() if f.name != "__pycache__"]
    assert mac_files in ([], [".gitkeep"]), f"macos/ doit être vide pour le moment : {mac_files}"

    # 3. Absence de répertoires de code/tests, doublon win/ ou caches à la racine
    assert not (root / "win").exists(), "Le doublon win/ ne doit pas exister (seul windows/ est retenu)"
    assert not (root / "gui_agent").exists(), "Le répertoire gui_agent ne doit plus exister à la racine"
    assert not (root / "tests").exists(), (
        "Le répertoire tests/ ne doit plus exister à la racine (déplacé dans linux/tests)"
    )
    assert not (root / "examples").exists(), (
        "Le répertoire examples/ ne doit plus exister à la racine (déplacé dans linux/examples)"
    )
    assert not (root / "screenshots").exists(), "Le répertoire de cache screenshots/ ne doit plus exister à la racine"


def test_linux_paths_default_xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Valide la résolution des chemins Linux par défaut selon les spécifications XDG."""
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    monkeypatch.delenv("GUI_AGENT_SCREENSHOTS_DIR", raising=False)
    monkeypatch.delenv("GUI_AGENT_VIDEOS_DIR", raising=False)

    paths = LinuxPaths()
    assert paths.platform_name == "linux"
    assert paths.get_data_dir() == fake_home / ".local" / "share" / "gui-agent"
    assert paths.get_config_dir() == fake_home / ".config" / "gui-agent"
    assert paths.get_cache_dir() == fake_home / ".cache" / "gui-agent"
    assert paths.get_screenshots_dir() == fake_home / ".cache" / "gui-agent" / "screenshots"
    assert paths.get_videos_dir() == fake_home / ".cache" / "gui-agent" / "videos"


def test_linux_paths_custom_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Valide la prise en compte prioritaire des variables d'environnement XDG sous Linux."""
    c_data = tmp_path / "custom_data"
    c_conf = tmp_path / "custom_conf"
    c_cache = tmp_path / "custom_cache"
    c_shots = tmp_path / "custom_shots"
    c_vids = tmp_path / "custom_vids"

    monkeypatch.setenv("XDG_DATA_HOME", str(c_data))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(c_conf))
    monkeypatch.setenv("XDG_CACHE_HOME", str(c_cache))
    monkeypatch.setenv("GUI_AGENT_SCREENSHOTS_DIR", str(c_shots))
    monkeypatch.setenv("GUI_AGENT_VIDEOS_DIR", str(c_vids))

    paths = LinuxPaths()
    assert paths.get_data_dir() == c_data / "gui-agent"
    assert paths.get_config_dir() == c_conf / "gui-agent"
    assert paths.get_cache_dir() == c_cache / "gui-agent"
    assert paths.get_screenshots_dir() == c_shots
    assert paths.get_videos_dir() == c_vids


def test_high_level_helpers_and_directories_created(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Valide les fonctions utilitaires et la création automatique des répertoires de cache."""
    test_shots = tmp_path / "shots"
    test_vids = tmp_path / "vids"
    monkeypatch.setenv("GUI_AGENT_SCREENSHOTS_DIR", str(test_shots))
    monkeypatch.setenv("GUI_AGENT_VIDEOS_DIR", str(test_vids))

    shots = get_screenshots_dir()
    vids = get_videos_dir()
    cache = get_cache_dir()
    data = get_data_dir()
    config = get_config_dir()
    bin_dir = get_binary_install_dir()

    assert os.path.isabs(shots)
    assert os.path.isabs(vids)
    assert os.path.isabs(cache)
    assert os.path.isabs(data)
    assert os.path.isabs(config)
    assert os.path.isabs(bin_dir)
    assert os.path.isdir(shots)
    assert os.path.isdir(vids)


def test_binary_candidates_and_discovery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la découverte dynamique des binaires exécutables natifs sous Linux."""
    fake_bin = tmp_path / "custom_atspi_bin"
    fake_bin.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    fake_bin.chmod(0o755)

    monkeypatch.setenv("GUI_AGENT_ATSPI_BIN", str(fake_bin))
    found = find_platform_binary("gui-agent-atspi")
    assert found == str(fake_bin)


def test_video_recording_tool_preserved_and_configured() -> None:
    """Valide formellement que l'outil de capture vidéo est conservé et configuré."""
    import gui_agent
    import gui_agent.server as s

    assert hasattr(gui_agent, "gui_start_video_recording")
    assert hasattr(gui_agent, "gui_stop_video_recording")
    assert "gui_start_video_recording" in gui_agent.__all__
    assert "gui_stop_video_recording" in gui_agent.__all__

    assert hasattr(s, "VIDEOS_DIR")
    assert os.path.isabs(s.VIDEOS_DIR)
    assert os.path.isdir(s.VIDEOS_DIR)


def test_linux_paths_rejects_relative_xdg_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que les variables XDG relatives sont ignorées et remplacées par les chemins par défaut."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("XDG_DATA_HOME", "relative/data")
    monkeypatch.setenv("XDG_CONFIG_HOME", "relative/config")
    monkeypatch.setenv("XDG_CACHE_HOME", "relative/cache")

    paths = LinuxPaths()
    assert paths.get_data_dir() == fake_home / ".local" / "share" / "gui-agent"
    assert paths.get_config_dir() == fake_home / ".config" / "gui-agent"
    assert paths.get_cache_dir() == fake_home / ".cache" / "gui-agent"


def test_linux_paths_runtime_dir_security(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la validation de sécurité (mode 0700 et UID) pour XDG_RUNTIME_DIR."""
    insecure_dir = tmp_path / "insecure_run"
    insecure_dir.mkdir()

    fake_stat = insecure_dir.stat()
    insecure_stat = os.stat_result(
        (
            fake_stat.st_mode | 0o077,
            fake_stat.st_ino,
            fake_stat.st_dev,
            fake_stat.st_nlink,
            fake_stat.st_uid,
            fake_stat.st_gid,
            fake_stat.st_size,
            int(fake_stat.st_atime),
            int(fake_stat.st_mtime),
            int(fake_stat.st_ctime),
        )
    )

    orig_stat = Path.stat

    def mocked_stat(self: Path, *, follow_symlinks: bool = True) -> os.stat_result:
        if self == insecure_dir:
            return insecure_stat
        return orig_stat(self, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(Path, "stat", mocked_stat)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(insecure_dir))
    paths = LinuxPaths()
    runtime_dir = paths.get_xdg_runtime_dir()
    assert runtime_dir != insecure_dir
    assert os.path.isdir(runtime_dir)
