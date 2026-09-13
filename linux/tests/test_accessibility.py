"""Tests unitaires et d'intégration pour la couche d'accessibilité (AT-SPI / D-Bus)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any
from unittest.mock import MagicMock

import pytest

from gui_agent.core.mcp_core import mcp_core
import gui_agent.layers.accessibility as accessibility
from gui_agent.layers.accessibility import (
    find_atspi_mediator_binary,
    get_app_state,
    perform_action,
    set_mock_action_handler,
    set_mock_state,
    set_mock_value_handler,
    set_value,
)


@pytest.fixture(autouse=True)
def cleanup_mocks() -> Any:
    """Réinitialise les gestionnaires mocks avant et après chaque test."""
    set_mock_state(None)
    set_mock_action_handler(None)
    set_mock_value_handler(None)
    accessibility._snapshots.clear()
    accessibility._last_node_cache.clear()
    accessibility._last_snapshot_id = None
    yield
    set_mock_state(None)
    set_mock_action_handler(None)
    set_mock_value_handler(None)
    accessibility._snapshots.clear()
    accessibility._last_node_cache.clear()
    accessibility._last_snapshot_id = None


def test_find_atspi_mediator_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la détection de l'exécutable Rust et la priorité des variables d'environnement."""
    # Test avec override d'environnement valide
    monkeypatch.setenv("GUI_AGENT_ATSPI_BIN", "/bin/sh")
    assert find_atspi_mediator_binary() == "/bin/sh"

    # Test avec override inexistant
    monkeypatch.setenv("GUI_AGENT_ATSPI_BIN", "/nonexistent/binary")
    detected = find_atspi_mediator_binary()
    assert detected != "/nonexistent/binary"


def test_get_app_state_nominal_or_error() -> None:
    """Vérifie le contrat de retour de get_app_state en conditions réelles."""
    res = get_app_state(include_screenshot=False)
    assert isinstance(res, dict)
    assert res["layer"] == "accessibility"
    assert res["status"] in ("success", "error")
    assert "count" in res
    assert "tree" in res
    assert res["include_screenshot"] is False


def test_get_app_state_with_screenshot() -> None:
    """Vérifie la transmission du paramètre include_screenshot."""
    res = get_app_state(include_screenshot=True)
    assert res["include_screenshot"] is True
    assert res["layer"] == "accessibility"


def test_get_app_state_mock() -> None:
    """Vérifie le comportement de get_app_state sous mock."""
    mock_payload = {
        "status": "success",
        "count": 2,
        "tree": [
            {"index": 0, "role": "application", "name": "test_app"},
            {"index": 1, "role": "push button", "name": "Valider"},
        ],
    }
    set_mock_state(mock_payload)
    res = get_app_state(include_screenshot=False)
    assert res["status"] == "success"
    assert res["count"] == 2
    assert len(res["tree"]) == 2
    assert res["tree"][1]["name"] == "Valider"
    assert res["layer"] == "accessibility"


def test_get_app_state_binary_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la gestion gracieuse en cas d'absence de moteur Rust."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: None)
    monkeypatch.setattr(accessibility, "_dbus_get_app_state", lambda app_name=None: [])
    res = get_app_state()
    assert res["status"] == "error"
    assert "introuvable" in res["error"]
    assert res["count"] == 0
    assert res["tree"] == []


def test_get_app_state_subprocess_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la gestion d'un échec d'exécution du binaire Rust."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stderr = "Bus D-Bus inaccessible"
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_proc)

    res = get_app_state()
    assert res["status"] == "error"
    assert "Bus D-Bus inaccessible" in res["error"]


def test_get_app_state_subprocess_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la levée et la capture propre d'un timeout sur le binaire."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    def raise_timeout(*args: Any, **kwargs: Any) -> Any:
        raise subprocess.TimeoutExpired(cmd=["test"], timeout=10.0)

    monkeypatch.setattr(subprocess, "run", raise_timeout)

    res = get_app_state()
    assert res["status"] == "error"
    assert "Timeout" in res["error"]


def test_perform_action_mock() -> None:
    """Vérifie le fonctionnement de perform_action avec mock."""
    set_mock_action_handler(lambda el, act: el == "10" and act == "activate")
    assert perform_action("10", "activate") is True
    assert perform_action("10", "press") is False
    assert perform_action("99", "activate") is False

    set_mock_action_handler(True)
    assert perform_action("anything") is True


def test_perform_action_binary_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie le retour False immédiat si aucun binaire Rust n'est présent et fallback D-Bus indisponible."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: None)
    monkeypatch.setattr(accessibility, "_get_atspi_bus_address", lambda: None)
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    assert perform_action("0") is False
    assert perform_action(":1.1/org/a11y/atspi/accessible/root", "activate") is False


def test_perform_action_mcp_mock_protocol(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie l'interaction JSON-RPC avec le protocole MCP stdio pour perform_action."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    written_lines: list[str] = []

    class MockStdin:
        def write(self, text: str) -> None:
            written_lines.append(text)

        def flush(self) -> None:
            pass

    class MockStdout:
        def __init__(self) -> None:
            self.lines = [
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"structuredContent": {"ok": True}}}) + "\n",
            ]

        def readline(self) -> str:
            if self.lines:
                return self.lines.pop(0)
            return ""

    class MockProcess:
        def __init__(self) -> None:
            self.stdin = MockStdin()
            self.stdout = MockStdout()
            self.stderr = MagicMock()

        def communicate(self, input: str | None = None, timeout: float | None = None) -> tuple[str, str]:
            if input:
                for line in input.splitlines(keepends=True):
                    self.stdin.write(line)
            out = "".join(self.stdout.lines)
            return out, ""

        def poll(self) -> int | None:
            return 0

        def terminate(self) -> None:
            pass

        def wait(self, timeout: float = 1.0) -> None:
            pass

        def kill(self) -> None:
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProcess())

    # Appel numérique (avec index résolu dans le cache du snapshot)
    accessibility._snapshots["snap_mcp"] = {"nodes": {"42": ":1.42/node/42"}, "app_name": "test_app"}
    accessibility._last_snapshot_id = "snap_mcp"
    accessibility._last_node_cache["42"] = ":1.42/node/42"
    res_num = perform_action("42", "press", snapshot_id="snap_mcp")
    assert res_num is True
    assert any('"element_index": 42' in line for line in written_lines)
    assert any('"element_identifier": ":1.42/node/42"' in line for line in written_lines)

    # Appel sélecteur textuel direct (element_identifier)
    written_lines.clear()
    res_str = perform_action(":1.14/root", "click")
    assert res_str is True
    assert any('"element_identifier": ":1.14/root"' in line for line in written_lines)


def test_set_value_mock() -> None:
    """Vérifie le fonctionnement de set_value avec mock."""
    set_mock_value_handler(lambda el, val: el == "15" and val == "valid_text")
    assert set_value("15", "valid_text") is True
    assert set_value("15", "wrong") is False
    assert set_value("99", "valid_text") is False

    set_mock_value_handler(True)
    assert set_value("any", "val") is True


def test_set_value_binary_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie le retour False immédiat si aucun binaire Rust n'est présent et fallback D-Bus indisponible."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: None)
    monkeypatch.setattr(accessibility, "_get_atspi_bus_address", lambda: None)
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    assert set_value("0", "text") is False
    assert set_value(":1.1/org/a11y/atspi/accessible/root", "text") is False


def test_set_value_mcp_mock_protocol(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie l'interaction JSON-RPC avec le protocole MCP stdio pour set_value."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    written_lines: list[str] = []

    class MockStdin:
        def write(self, text: str) -> None:
            written_lines.append(text)

        def flush(self) -> None:
            pass

    class MockStdout:
        def __init__(self) -> None:
            self.lines = [
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"structuredContent": {"ok": True}}}) + "\n",
            ]

        def readline(self) -> str:
            if self.lines:
                return self.lines.pop(0)
            return ""

    class MockProcess:
        def __init__(self) -> None:
            self.stdin = MockStdin()
            self.stdout = MockStdout()
            self.stderr = MagicMock()

        def communicate(self, input: str | None = None, timeout: float | None = None) -> tuple[str, str]:
            if input:
                for line in input.splitlines(keepends=True):
                    self.stdin.write(line)
            out = "".join(self.stdout.lines)
            return out, ""

        def poll(self) -> int | None:
            return 0

        def terminate(self) -> None:
            pass

        def wait(self, timeout: float = 1.0) -> None:
            pass

        def kill(self) -> None:
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProcess())

    accessibility._snapshots["snap_val"] = {"nodes": {"100": ":1.100/input/100"}, "app_name": "test_app"}
    accessibility._last_snapshot_id = "snap_val"
    accessibility._last_node_cache["100"] = ":1.100/input/100"
    res = set_value("100", "nouveau_texte", snapshot_id="snap_val")
    assert res is True
    assert any('"value": "nouveau_texte"' in line for line in written_lines)
    assert any('"element_index": 100' in line for line in written_lines)
    assert any('"element_identifier": ":1.100/input/100"' in line for line in written_lines)


def test_perform_action_and_set_value_with_node_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que element_identifier est résolu à partir de _last_node_cache."""
    written_lines: list[str] = []

    class MockStdin:
        def write(self, text: str) -> None:
            written_lines.append(text)

        def flush(self) -> None:
            pass

    class MockStdout:
        def __init__(self) -> None:
            self.lines = [
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"structuredContent": {"ok": True}}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"structuredContent": {"ok": True}}}) + "\n",
            ]

        def readline(self) -> str:
            if self.lines:
                return self.lines.pop(0)
            return ""

    class MockProcess:
        def __init__(self) -> None:
            self.stdin = MockStdin()
            self.stdout = MockStdout()
            self.stderr = MagicMock()

        def communicate(self, input: str | None = None, timeout: float | None = None) -> tuple[str, str]:
            if input:
                for line in input.splitlines(keepends=True):
                    self.stdin.write(line)
            out = "".join(self.stdout.lines)
            return out, ""

        def poll(self) -> int | None:
            return 0

        def terminate(self) -> None:
            pass

        def wait(self, timeout: float = 1.0) -> None:
            pass

        def kill(self) -> None:
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProcess())
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    # Peupler le cache avec un snapshot explicite
    accessibility._snapshots["snap_7"] = {
        "nodes": {"7": ":1.42/org/a11y/atspi/accessible/7"},
        "app_name": "test_app",
    }
    accessibility._last_snapshot_id = "snap_7"
    accessibility._last_node_cache["7"] = ":1.42/org/a11y/atspi/accessible/7"

    # Vérifier perform_action avec résolution
    ok_act = perform_action("7", "press", snapshot_id="snap_7")
    assert ok_act is True
    assert any('"element_index": 7' in line for line in written_lines)
    assert any('"element_identifier": ":1.42/org/a11y/atspi/accessible/7"' in line for line in written_lines)

    # Vérifier set_value avec résolution
    written_lines.clear()
    ok_val = set_value("7", "valeur_test", snapshot_id="snap_7")
    assert ok_val is True
    assert any('"element_index": 7' in line for line in written_lines)
    assert any('"element_identifier": ":1.42/org/a11y/atspi/accessible/7"' in line for line in written_lines)


def test_mcp_core_sdk_facade_integration() -> None:
    """Vérifie l'exposition et l'appel des outils d'accessibilité depuis mcp_core."""
    set_mock_state({"status": "success", "count": 1, "tree": [{"role": "window"}]})
    set_mock_action_handler(True)
    set_mock_value_handler(True)

    state = mcp_core.get_app_state()
    assert state["status"] == "success"
    assert state["count"] == 1

    act_ok = mcp_core.perform_action("1", "activate")
    assert act_ok is True

    val_ok = mcp_core.set_value("1", "texte_saisi")
    assert val_ok is True


def test_get_app_state_invalid_tree_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie le rejet d'un payload AT-SPI mal formé et le nettoyage du cache."""
    accessibility._last_node_cache["1"] = ":1.1/old"
    accessibility._last_snapshot_id = "old_snap"
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps({"tree": "not_a_list"})
    mock_proc.stderr = ""
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_proc)

    res = get_app_state()
    assert res["status"] == "error"
    assert "non pris en charge" in res["error"]
    assert len(accessibility._last_node_cache) == 0
    assert accessibility._last_snapshot_id is None


def test_perform_action_and_set_value_with_snapshot_id_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie qu'un snapshot_id obsolète entraîne un rejet fail-closed immédiat."""
    written_lines: list[str] = []

    class MockStdin:
        def write(self, text: str) -> None:
            written_lines.append(text)

        def flush(self) -> None:
            pass

    class MockStdout:
        def __init__(self) -> None:
            self.lines = [
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"structuredContent": {"ok": True}}}) + "\n",
            ]

        def readline(self) -> str:
            if self.lines:
                return self.lines.pop(0)
            return ""

    class MockProcess:
        def __init__(self) -> None:
            self.stdin = MockStdin()
            self.stdout = MockStdout()
            self.stderr = MagicMock()

        def communicate(self, input: str | None = None, timeout: float | None = None) -> tuple[str, str]:
            if input:
                for line in input.splitlines(keepends=True):
                    self.stdin.write(line)
            out = "".join(self.stdout.lines)
            return out, ""

        def poll(self) -> int | None:
            return 0

        def terminate(self) -> None:
            pass

        def wait(self, timeout: float = 1.0) -> None:
            pass

        def kill(self) -> None:
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProcess())
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    accessibility._snapshots["current_snap"] = {"nodes": {"5": ":1.99/stale/ref"}, "app_name": "app"}
    accessibility._last_node_cache["5"] = ":1.99/stale/ref"
    accessibility._last_snapshot_id = "current_snap"

    # Avec snapshot_id obsolète, l'action et l'écriture doivent être immédiatement rejetées
    act_ok = perform_action("5", "activate", snapshot_id="stale_snap")
    assert act_ok is False
    assert len(written_lines) == 0

    val_ok = set_value("5", "texte", snapshot_id="stale_snap")
    assert val_ok is False
    assert len(written_lines) == 0


def test_perform_action_and_set_value_with_missing_cache_index(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie qu'un index numérique absent du cache est rejeté sans appel externe."""
    mock_popen = MagicMock()
    monkeypatch.setattr(subprocess, "Popen", mock_popen)
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")
    accessibility._snapshots["snap_1"] = {"nodes": {}, "app_name": "app"}
    accessibility._last_node_cache.clear()
    accessibility._last_snapshot_id = "snap_1"

    assert perform_action("999", "activate", snapshot_id="snap_1") is False
    assert set_value("999", "valeur", snapshot_id="snap_1") is False
    assert mock_popen.call_count == 0


def test_numeric_index_without_snapshot_id_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie qu'un index numérique sans snapshot_id est systématiquement rejeté (fail-closed)."""
    mock_popen = MagicMock()
    monkeypatch.setattr(subprocess, "Popen", mock_popen)
    accessibility._snapshots["valid_snap"] = {"nodes": {"1": ":1.1/valid"}, "app_name": "app"}
    accessibility._last_snapshot_id = "valid_snap"
    accessibility._last_node_cache["1"] = ":1.1/valid"

    # Tout appel numérique sans snapshot_id doit échouer immédiatement sans appeler Popen
    assert perform_action("1", "activate") is False
    assert set_value("1", "texte") is False
    assert mock_popen.call_count == 0


def test_dbus_fallback_action_and_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie le fonctionnement du fallback direct busctl/D-Bus lorsque le binaire Rust est absent."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: None)

    executed_cmds: list[list[str]] = []

    def mock_run(cmd: list[str], *args: Any, **kwargs: Any) -> Any:
        executed_cmds.append(cmd)
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "b true"
        mock_res.stderr = ""
        return mock_res

    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr(accessibility, "_get_atspi_bus_address", lambda: "unix:path=/test/bus")
    monkeypatch.setattr("shutil.which", lambda name: f"/bin/{name}" if name == "busctl" else None)

    res_act = perform_action(":1.42/org/a11y/atspi/accessible/42", "0")
    assert res_act is True
    assert any("DoAction" in cmd for cmd in executed_cmds)

    res_val = set_value(":1.42/org/a11y/atspi/accessible/42", "hello")
    assert res_val is True
    assert any("SetTextContents" in cmd for cmd in executed_cmds)


def test_is_elf_binary_architecture_validation(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que _is_elf_binary rejette les architectures incompatibles et accepte l'hôte."""
    import struct

    # 1. Fichier non-ELF
    txt_file = tmp_path / "script.sh"
    txt_file.write_text("#!/bin/sh\necho hello\n")
    assert accessibility._is_elf_binary(str(txt_file)) is False

    # 2. ELF valide pour x86_64 (machine 0x3E)
    x86_file = tmp_path / "bin_x86"
    hdr_x86 = bytearray(b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 10)
    hdr_x86 += struct.pack("<H", 0x3E)  # EM_X86_64
    hdr_x86 += b"\x00" * 32
    x86_file.write_bytes(bytes(hdr_x86))

    # 3. ELF pour ARM64 (machine 0xB7)
    arm_file = tmp_path / "bin_arm"
    hdr_arm = bytearray(b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 10)
    hdr_arm += struct.pack("<H", 0xB7)  # EM_AARCH64
    hdr_arm += b"\x00" * 32
    arm_file.write_bytes(bytes(hdr_arm))

    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    assert accessibility._is_elf_binary(str(x86_file)) is True
    assert accessibility._is_elf_binary(str(arm_file)) is False

    monkeypatch.setattr("platform.machine", lambda: "aarch64")
    assert accessibility._is_elf_binary(str(x86_file)) is False
    assert accessibility._is_elf_binary(str(arm_file)) is True


def test_dbus_get_app_state_descendant_controls_traversal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que _dbus_get_app_state explore bien les contrôles descendants avec rôles et actions."""
    monkeypatch.setattr("shutil.which", lambda name: f"/bin/{name}" if name == "busctl" else None)
    monkeypatch.setattr(accessibility, "_get_atspi_bus_address", lambda: "unix:path=/test/bus")

    def mock_run(cmd: list[str], *args: Any, **kwargs: Any) -> Any:
        mock_res = MagicMock()
        mock_res.returncode = 0
        if "GetChildren" in cmd:
            if "/org/a11y/atspi/accessible/root" in cmd:
                mock_res.stdout = 'a(so) 1 ":1.100" "/org/a11y/atspi/accessible/100"'
            else:
                mock_res.stdout = 'a(so) 1 ":1.100" "/org/a11y/atspi/accessible/101"'
        elif "GetRoleName" in cmd:
            mock_res.stdout = 's "push button"'
        elif "GetNActions" in cmd:
            mock_res.stdout = "i 1"
        elif "GetName" in cmd:
            mock_res.stdout = 's "click"'
        elif "Name" in cmd:
            if "/org/a11y/atspi/accessible/100" in cmd:
                mock_res.stdout = 's "mon_app"'
            else:
                mock_res.stdout = 's "Bouton Valider"'
        else:
            mock_res.stdout = ""
        mock_res.stderr = ""
        return mock_res

    monkeypatch.setattr(subprocess, "run", mock_run)

    tree = accessibility._dbus_get_app_state(app_name="mon_app", max_depth=2, max_nodes=10)
    assert len(tree) >= 2
    assert tree[0]["name"] == "mon_app"
    assert tree[0]["depth"] == 0
    assert tree[1]["name"] == "Bouton Valider"
    assert tree[1]["role"] == "push button"
    assert tree[1]["depth"] == 1
    assert "click" in tree[1]["actions"]


def test_perform_action_and_set_value_numeric_int_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que passer element_id sous forme d'entier (ex: 42) est normalisé sans erreur."""
    written_lines: list[str] = []

    class MockStdin:
        def write(self, text: str) -> None:
            written_lines.append(text)

        def flush(self) -> None:
            pass

    class MockStdout:
        def __init__(self) -> None:
            self.lines = [
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"structuredContent": {"ok": True}}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}) + "\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "result": {"structuredContent": {"ok": True}}}) + "\n",
            ]

        def readline(self) -> str:
            if self.lines:
                return self.lines.pop(0)
            return ""

    class MockProcess:
        def __init__(self) -> None:
            self.stdin = MockStdin()
            self.stdout = MockStdout()
            self.stderr = MagicMock()

        def communicate(self, input: str | None = None, timeout: float | None = None) -> tuple[str, str]:
            if input:
                for line in input.splitlines(keepends=True):
                    self.stdin.write(line)
            out = "".join(self.stdout.lines)
            return out, ""

        def poll(self) -> int | None:
            return 0

        def terminate(self) -> None:
            pass

        def wait(self, timeout: float = 1.0) -> None:
            pass

        def kill(self) -> None:
            pass

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: MockProcess())
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *args, **kwargs: "/bin/sh")

    accessibility._snapshots["snap_int"] = {"nodes": {"42": ":1.42/btn/42"}, "app_name": "app"}
    accessibility._last_snapshot_id = "snap_int"
    accessibility._last_node_cache["42"] = ":1.42/btn/42"

    # Passer l'entier 42 au lieu de la chaîne "42"
    act_ok = perform_action(42, "activate", snapshot_id="snap_int")
    assert act_ok is True
    assert any('"element_index": 42' in line for line in written_lines)

    written_lines.clear()
    val_ok = set_value(42, "nouveau", snapshot_id="snap_int")
    assert val_ok is True
    assert any('"element_index": 42' in line for line in written_lines)


def test_dbus_call_action_or_value_dest_and_path_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie le rejet strict d'identifiants D-Bus avec injection d'arguments ou chemin invalide."""
    monkeypatch.setattr("shutil.which", lambda name: f"/bin/{name}")
    # Rejet d'une destination débutant par '-'
    assert accessibility._dbus_call_action_or_value("perform_action", {"element_identifier": "--user/path"}) is False
    assert accessibility._dbus_call_action_or_value("perform_action", {"element_identifier": "-help/path"}) is False
    # Rejet d'un chemin d'objet ne débutant pas par '/'
    assert accessibility._dbus_call_action_or_value("perform_action", {"element_identifier": ":1.14"}) is False


def test_dbus_set_value_b_false_rejection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que SetTextContents renvoie False lorsque D-Bus répond 'b false'."""
    monkeypatch.setattr("shutil.which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(accessibility, "_get_atspi_bus_address", lambda: "unix:path=/test/bus")

    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "b false\n"
    mock_res.stderr = ""
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_res)

    ok = accessibility._dbus_call_action_or_value("set_value", {"element_identifier": ":1.42/node/1", "value": "test"})
    assert ok is False


def test_python_mcp_loop_resilience_and_tools_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la résilience de la boucle MCP Python face aux JSON malformés et l'appel tools/list."""
    import io
    import sys

    input_stream = io.StringIO(
        "MALFORMED JSON LINE\n"
        + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 10, "method": "tools/list"})
        + "\n"
    )
    output_stream = io.StringIO()
    monkeypatch.setattr(sys, "stdin", input_stream)
    monkeypatch.setattr(sys, "stdout", output_stream)

    accessibility._run_python_atspi_cli(["mcp"])

    output_lines = [json.loads(line) for line in output_stream.getvalue().strip().splitlines() if line.strip()]
    assert len(output_lines) == 2
    # 1. Réponse d'erreur Parse error sur la première ligne invalide
    assert output_lines[0].get("error", {}).get("code") == -32700
    # 2. Réponse valide à tools/list contenant les 3 outils
    tools_res = output_lines[1]
    assert tools_res.get("id") == 10
    tool_names = [t["name"] for t in tools_res.get("result", {}).get("tools", [])]
    assert "get_app_state" in tool_names
    assert "perform_action" in tool_names
    assert "set_value" in tool_names


def test_dbus_get_app_state_deadline_interruption(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que la traversée D-Bus s'interrompt dès que le deadline est dépassé."""
    monkeypatch.setattr("shutil.which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(accessibility, "_get_atspi_bus_address", lambda: "unix:path=/tmp/test")
    monkeypatch.setattr(
        accessibility,
        "_dbus_read_children",
        lambda *args, **kwargs: [(":1.1", "/root/1"), (":1.2", "/root/2")],
    )

    # 1. Timeout immédiat / déjà expiré
    nodes = accessibility._dbus_get_app_state(timeout=-1.0)
    assert nodes == []

    # 2. Expiration en cours de boucle
    curr_time = 100.0

    def mock_time() -> float:
        nonlocal curr_time
        curr_time += 5.0
        return curr_time

    monkeypatch.setattr("time.monotonic", mock_time)
    nodes_mid = accessibility._dbus_get_app_state(timeout=2.0)
    assert isinstance(nodes_mid, list)


def test_multi_snapshot_concurrent_validity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie que la capture d'un second snapshot n'invalide pas les requêtes sur le premier snapshot."""
    called_refs: list[str] = []

    def mock_mcp_call(tool_name: str, args: dict[str, Any], timeout: float = 15.0) -> bool:
        called_refs.append(args.get("element_identifier", ""))
        return True

    monkeypatch.setattr(accessibility, "_call_mcp_action_or_value", mock_mcp_call)

    # Créer deux snapshots distincts (simulant deux applications ou requêtes concurrentes)
    accessibility._snapshots["snap_app_a"] = {
        "nodes": {"1": ":1.10/node/button_a"},
        "app_name": "AppA",
    }
    accessibility._snapshots["snap_app_b"] = {
        "nodes": {"1": ":1.20/node/button_b"},
        "app_name": "AppB",
    }

    # Agir sur snap_app_a après la création de snap_app_b
    ok_a = perform_action("1", "click", snapshot_id="snap_app_a")
    assert ok_a is True
    assert called_refs[-1] == ":1.10/node/button_a"

    # Agir sur snap_app_b
    ok_b = perform_action("1", "press", snapshot_id="snap_app_b")
    assert ok_b is True
    assert called_refs[-1] == ":1.20/node/button_b"

    # set_value sur les deux snapshots
    val_a = set_value("1", "texte_a", snapshot_id="snap_app_a")
    assert val_a is True
    val_b = set_value("1", "texte_b", snapshot_id="snap_app_b")
    assert val_b is True


def test_get_app_state_dbus_fallback_when_binary_missing_or_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie le repli sur D-Bus pur quand le binaire Rust est manquant ou échoue."""
    fake_tree = [{"name": "FallbackBtn", "role": "push button", "object_ref": ":1.99/node"}]
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *a, **kw: None)
    monkeypatch.setattr(accessibility, "_dbus_get_app_state", lambda app_name=None: fake_tree)

    res = get_app_state(include_screenshot=False, app_name="test_app")
    assert res["status"] == "success"
    assert res.get("degraded") is True
    assert res["count"] == 1
    assert res["tree"][0]["name"] == "FallbackBtn"


def test_call_mcp_action_or_value_fallback_on_popen_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie le repli direct sur _dbus_call_action_or_value en cas d'erreur de lancement Popen."""
    monkeypatch.setattr(accessibility, "find_atspi_mediator_binary", lambda *a, **kw: "/bin/false")

    def mock_popen_fail(*args: Any, **kwargs: Any) -> Any:
        raise OSError("Processus non exécutable")

    monkeypatch.setattr(subprocess, "Popen", mock_popen_fail)
    dbus_called = False

    def mock_dbus_call(tool_name: str, args: dict[str, Any], timeout: float = 10.0) -> bool:
        nonlocal dbus_called
        dbus_called = True
        return True

    monkeypatch.setattr(accessibility, "_dbus_call_action_or_value", mock_dbus_call)

    res = accessibility._call_mcp_action_or_value(
        "perform_action", {"element_identifier": ":1.1/node", "action": "click"}
    )
    assert res is True
    assert dbus_called is True


def test_get_atspi_bus_address_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    """Vérifie la résolution de l'adresse AT-SPI via variable d'environnement puis busctl."""
    # 1. Via variable d'environnement explicite
    monkeypatch.setenv("AT_SPI_BUS_ADDRESS", "unix:path=/custom/atspi")
    assert accessibility._get_atspi_bus_address() == "unix:path=/custom/atspi"

    # 2. Sans variable, via busctl
    monkeypatch.delenv("AT_SPI_BUS_ADDRESS", raising=False)
    mock_run = MagicMock()
    mock_run.returncode = 0
    mock_run.stdout = 's "unix:path=/run/user/1000/at-spi/bus_0"\n'
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_run)
    assert accessibility._get_atspi_bus_address() == "unix:path=/run/user/1000/at-spi/bus_0"


def test_mcp_stale_index_rejection_with_token() -> None:
    """Vérifie que le serveur MCP Rust rejette un index numérique avec un snapshot_token périmé ou absent."""
    bin_path = str(Path(__file__).resolve().parent.parent / "bin" / "gui-agent-atspi")
    if not os.path.isfile(bin_path) or not os.access(bin_path, os.X_OK):
        pytest.skip("gui-agent-atspi binaire non présent")

    proc = subprocess.Popen(
        [bin_path, "mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    action_no_snap = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "perform_action", "arguments": {"element_index": 7}},
    }
    action_stale_token = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "perform_action", "arguments": {"element_index": 7, "snapshot_token": "stale-snap-999"}},
    }
    payload = "\n".join([json.dumps(init_req), json.dumps(action_no_snap), json.dumps(action_stale_token)]) + "\n"
    out, _ = proc.communicate(input=payload, timeout=5.0)
    lines = [json.loads(line_str) for line_str in out.strip().splitlines() if line_str.strip()]

    resp_2 = next((line_item for line_item in lines if line_item.get("id") == 2), None)
    assert resp_2 is not None
    assert resp_2["result"]["isError"] is True

    resp_3 = next((line_item for line_item in lines if line_item.get("id") == 3), None)
    assert resp_3 is not None
    assert resp_3["result"]["isError"] is True
