"""Couche d'Accessibilité Programmatique (AT-SPI / D-Bus).

Ce module assure la médiation sémantique avec l'arbre d'accessibilité Linux (AT-SPI2 / D-Bus)
en déléguant au moteur natif en Rust pour garantir des lectures rapides (< 50 ms),
l'inspection d'arbres hiérarchiques et des actions directes en mémoire RAM sans cécité visuelle.
"""

from __future__ import annotations

import collections
import contextlib
import json
import logging
import os
import platform
import shutil
import struct
import subprocess
import sys
import threading
import time
from typing import Any
import uuid

logger = logging.getLogger("gui_agent.layers.accessibility")

# Mock d'état pour les tests unitaires et environnements headless sans bus graphique
_mock_state: dict[str, Any] | None = None
_mock_action_handler: Any | None = None
_mock_value_handler: Any | None = None

# Cache en mémoire des correspondances element_index -> object_ref synchronisé par verrou
_snapshots: dict[str, dict[str, Any]] = {}
_last_node_cache: dict[str, str] = {}
_last_snapshot_id: str | None = None
_cache_lock = threading.Lock()


def _clear_accessibility_cache() -> None:
    """Réinitialise l'ensemble des caches de snapshots et de nœuds."""
    global _last_snapshot_id
    with _cache_lock:
        _snapshots.clear()
        _last_node_cache.clear()
        _last_snapshot_id = None


def set_mock_state(state: dict[str, Any] | None) -> None:
    """Configure un état mocké d'accessibilité pour les tests."""
    global _mock_state
    _mock_state = state


def set_mock_action_handler(handler: Any | None) -> None:
    """Configure un gestionnaire mocké pour perform_action."""
    global _mock_action_handler
    _mock_action_handler = handler


def set_mock_value_handler(handler: Any | None) -> None:
    """Configure un gestionnaire mocké pour set_value."""
    global _mock_value_handler
    _mock_value_handler = handler


def _is_elf_binary(path: str) -> bool:
    """Vérifie si le fichier cible est un exécutable binaire natif ELF compatible avec l'hôte."""
    try:
        with open(path, "rb") as f:
            header = f.read(20)
            if len(header) < 20 or header[:4] != b"\x7fELF":
                return False

            ei_data = header[5]  # 1 = little-endian, 2 = big-endian
            endian = "<" if ei_data == 1 else ">"
            e_machine = struct.unpack(endian + "H", header[18:20])[0]

            host = platform.machine().lower()
            expected_machines: dict[str, set[int]] = {
                "x86_64": {0x3E},
                "amd64": {0x3E},
                "aarch64": {0xB7},
                "arm64": {0xB7},
                "i386": {0x03},
                "i686": {0x03},
                "x86": {0x03},
                "arm": {0x28},
                "armv7l": {0x28},
                "riscv64": {0xF3},
            }
            allowed = expected_machines.get(host)
            return allowed is None or e_machine in allowed
    except (OSError, struct.error):
        return False


def find_atspi_mediator_binary(exclude_scripts: bool = False) -> str | None:
    """Détecte l'exécutable du moteur AT-SPI disponible."""
    # 1. Variable d'environnement prioritaire
    custom_bin = os.environ.get("GUI_AGENT_ATSPI_BIN")
    if (
        custom_bin
        and os.path.isfile(custom_bin)
        and os.access(custom_bin, os.X_OK)
        and (not exclude_scripts or _is_elf_binary(custom_bin))
    ):
        return custom_bin

    # 2. Binaire local compilé dans workspace root ou crates/atspi_mediator (release puis debug)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for profile in ("release", "debug"):
        workspace_bin = os.path.join(project_root, "target", profile, "gui-agent-atspi")
        if (
            os.path.isfile(workspace_bin)
            and os.access(workspace_bin, os.X_OK)
            and (not exclude_scripts or _is_elf_binary(workspace_bin))
        ):
            return workspace_bin
        for candidate_crate in (
            os.path.join(project_root, "linux", "crates", "atspi_mediator", "target", profile, "gui-agent-atspi"),
            os.path.join(project_root, "crates", "atspi_mediator", "target", profile, "gui-agent-atspi"),
        ):
            if (
                os.path.isfile(candidate_crate)
                and os.access(candidate_crate, os.X_OK)
                and (not exclude_scripts or _is_elf_binary(candidate_crate))
            ):
                return candidate_crate

    # 2b. Binaire natif packagé directement dans le package Python (gui_agent/bin/gui-agent-atspi)
    package_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "gui-agent-atspi")
    if (
        os.path.isfile(package_bin)
        and os.access(package_bin, os.X_OK)
        and (not exclude_scripts or _is_elf_binary(package_bin))
    ):
        return package_bin

    # 3. Exécutable système standard dans ~/.local/bin ou préfixe d'environnement Python
    standard_paths = [
        os.path.expanduser("~/.local/bin/gui-agent-atspi"),
        os.path.join(sys.prefix, "bin", "gui-agent-atspi"),
    ]
    for candidate in standard_paths:
        if (
            os.path.isfile(candidate)
            and os.access(candidate, os.X_OK)
            and (not exclude_scripts or _is_elf_binary(candidate))
        ):
            return candidate

    # 4. Exécutable système 'gui-agent-atspi' dans le PATH
    which_agent = shutil.which("gui-agent-atspi")
    if which_agent and (not exclude_scripts or _is_elf_binary(which_agent)):
        return which_agent

    # 5. Exécutable système computer-use-linux (Rust upstream)
    which_bin = shutil.which("computer-use-linux")
    if which_bin and (not exclude_scripts or _is_elf_binary(which_bin)):
        return which_bin

    # 6. Chemins NVM éventuels dans le répertoire utilisateur
    user_home = os.path.expanduser("~")
    nvm_dir = os.path.join(user_home, ".nvm", "versions", "node")
    if os.path.isdir(nvm_dir):
        try:
            for node_ver in sorted(os.listdir(nvm_dir), reverse=True):
                candidate = os.path.join(nvm_dir, node_ver, "bin", "computer-use-linux")
                if (
                    os.path.isfile(candidate)
                    and os.access(candidate, os.X_OK)
                    and (not exclude_scripts or _is_elf_binary(candidate))
                ):
                    return candidate
        except OSError as nvm_err:
            logger.debug("Erreur lors du scan du répertoire NVM: %s", nvm_err)

    return None


def _get_atspi_bus_address() -> str | None:
    """Résout l'adresse du bus d'accessibilité AT-SPI / D-Bus."""
    env_addr = os.environ.get("DBUS_SESSION_BUS_ADDRESS")
    if env_addr:
        return env_addr
    user_bus = f"/run/user/{os.getuid()}/bus"
    if os.path.exists(user_bus):
        return f"unix:path={user_bus}"
    return None


def _dbus_get_actions(
    busctl_bin: str, addr_args: list[str], dest: str, obj_path: str, timeout: float = 5.0
) -> list[str]:
    """Récupère la liste des noms d'actions exposées par org.a11y.atspi.Action."""
    if not dest or dest.startswith("-") or not obj_path.startswith("/"):
        return []
    cmd_count = [
        busctl_bin,
        *addr_args,
        "call",
        dest,
        obj_path,
        "org.a11y.atspi.Action",
        "GetNActions",
    ]
    try:
        res = subprocess.run(cmd_count, capture_output=True, timeout=timeout, text=True, check=False)
        if res.returncode != 0:
            return []
        count_str = res.stdout.strip().split()[-1]
        count = max(0, min(int(count_str), 32))
    except Exception:
        return []

    names: list[str] = []
    for idx in range(count):
        cmd_name = [
            busctl_bin,
            *addr_args,
            "call",
            dest,
            obj_path,
            "org.a11y.atspi.Action",
            "GetName",
            "i",
            str(idx),
        ]
        try:
            res_name = subprocess.run(cmd_name, capture_output=True, timeout=timeout, text=True, check=False)
            if res_name.returncode == 0 and 's "' in res_name.stdout:
                name = res_name.stdout.split('s "', 1)[1].split('"', 1)[0]
                names.append(name)
            else:
                names.append("")
        except Exception:
            names.append("")
    return names


def _dbus_call_action_or_value(tool_name: str, arguments: dict[str, Any], timeout: float = 10.0) -> bool:
    """Exécute l'action ou l'écriture de valeur via busctl directement sur le bus AT-SPI."""
    element_id = str(arguments.get("element_identifier") or arguments.get("element_index") or "")
    if not element_id or "/" not in element_id:
        return False

    parts = element_id.split("/", 1)
    dest = parts[0].rstrip(":")
    obj_path = "/" + parts[1]
    if not dest or dest.startswith("-") or not obj_path.startswith("/"):
        return False

    busctl_bin = shutil.which("busctl")
    if not busctl_bin:
        return False

    bus_addr = _get_atspi_bus_address()
    addr_args = ["--address=" + bus_addr] if bus_addr else ["--user"]

    if tool_name == "perform_action":
        action_name = str(arguments.get("action", "")).strip()
        actions = _dbus_get_actions(busctl_bin, addr_args, dest, obj_path, timeout=timeout)

        action_idx: int | None = None
        if action_name.isdigit():
            idx = int(action_name)
            if actions and not (0 <= idx < len(actions)):
                return False
            action_idx = idx
        elif not actions:
            return False
        elif not action_name:
            action_idx = 0
        else:
            req_lower = action_name.lower()
            exact_matches = [i for i, name in enumerate(actions) if name.lower() == req_lower]
            if len(exact_matches) == 1:
                action_idx = exact_matches[0]
            elif len(exact_matches) > 1:
                return False
            else:
                sub_matches = [i for i, name in enumerate(actions) if req_lower in name.lower()]
                if len(sub_matches) == 1:
                    action_idx = sub_matches[0]
                elif req_lower in ("activate", "click", "press", "primary", "default"):
                    primary = [
                        i
                        for i, name in enumerate(actions)
                        if name.lower() in ("activate", "click", "press", "primary", "default", "toggle", "open")
                    ]
                    if len(primary) == 1:
                        action_idx = primary[0]

        if action_idx is None:
            return False

        cmd = [
            busctl_bin,
            *addr_args,
            "call",
            dest,
            obj_path,
            "org.a11y.atspi.Action",
            "DoAction",
            "i",
            str(action_idx),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=timeout, text=True, check=False)
            return res.returncode == 0 and "b true" in res.stdout
        except Exception as exc:
            logger.debug("Échec du fallback busctl perform_action: %s", exc)
            return False

    if tool_name == "set_value":
        val_str = str(arguments.get("value", ""))
        # 1. Tentative SetTextContents sur EditableText
        cmd_text = [
            busctl_bin,
            *addr_args,
            "call",
            dest,
            obj_path,
            "org.a11y.atspi.EditableText",
            "SetTextContents",
            "s",
            val_str,
        ]
        try:
            res = subprocess.run(cmd_text, capture_output=True, timeout=timeout, text=True, check=False)
            if res.returncode == 0 and "b true" in res.stdout:
                return True
        except Exception as exc:
            logger.debug("Échec du fallback busctl SetTextContents: %s", exc)

        # 2. Tentative CurrentValue sur Value (si valeur numérique)
        try:
            num_val = float(val_str)
            cmd_val = [
                busctl_bin,
                *addr_args,
                "set-property",
                dest,
                obj_path,
                "org.a11y.atspi.Value",
                "CurrentValue",
                "d",
                str(num_val),
            ]
            res = subprocess.run(cmd_val, capture_output=True, timeout=timeout, text=True, check=False)
            return res.returncode == 0
        except ValueError:
            pass
        except Exception as exc:
            logger.debug("Échec du fallback busctl set-property Value: %s", exc)

    return False


def _dbus_read_children(
    busctl_bin: str, addr_args: list[str], dest: str, obj_path: str, timeout: float = 1.5
) -> list[tuple[str, str]]:
    """Lit les enfants d'un nœud Accessible via l'interface D-Bus."""
    if not dest or dest.startswith("-") or not obj_path.startswith("/"):
        return []
    cmd = [
        busctl_bin,
        *addr_args,
        "call",
        dest,
        obj_path,
        "org.a11y.atspi.Accessible",
        "GetChildren",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=timeout, text=True, check=False)
        if res.returncode != 0:
            return []
        tokens = res.stdout.strip().split()
        items = [tok.strip('"') for tok in tokens if tok.startswith(('":', '"/'))]
        children: list[tuple[str, str]] = []
        for i in range(0, len(items) - 1, 2):
            c_dest, c_path = items[i], items[i + 1]
            if c_dest and not c_dest.startswith("-") and c_path.startswith("/"):
                children.append((c_dest, c_path))
        return children
    except Exception:
        return []


def _dbus_get_app_state(
    app_name: str | None = None,
    max_nodes: int = 50,
    max_depth: int = 4,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    """Extrait l'arbre d'accessibilité applicatif directement via D-Bus / busctl en explorant les contrôles descendants."""
    busctl_bin = shutil.which("busctl")
    if not busctl_bin:
        return []

    if timeout <= 0:
        return []

    deadline = time.monotonic() + timeout

    def _remaining(cap: float = 1.0) -> float:
        rem = deadline - time.monotonic()
        return min(cap, max(0.001, rem))

    bus_addr = _get_atspi_bus_address()
    addr_args = ["--address=" + bus_addr] if bus_addr else ["--user"]

    roots = _dbus_read_children(
        busctl_bin, addr_args, "org.a11y.atspi.Registry", "/org/a11y/atspi/accessible/root", timeout=_remaining(timeout)
    )
    if not roots:
        return []

    target_needle = app_name.strip().lower() if app_name else ""
    queue: collections.deque[tuple[str, str, int]] = collections.deque()

    # Découverte et filtrage des applications racines
    for bus_dest, root_path in roots:
        if time.monotonic() >= deadline:
            break
        cmd_name = [
            busctl_bin,
            *addr_args,
            "get-property",
            bus_dest,
            root_path,
            "org.a11y.atspi.Accessible",
            "Name",
        ]
        try:
            name_res = subprocess.run(cmd_name, capture_output=True, timeout=_remaining(1.0), text=True, check=False)
            app_root_name = ""
            if name_res.returncode == 0 and 's "' in name_res.stdout:
                app_root_name = name_res.stdout.split('s "', 1)[1].split('"', 1)[0]
        except Exception as exc:
            logger.debug("Échec de lecture du nom d'application racine D-Bus: %s", exc)
            continue

        if target_needle and target_needle not in app_root_name.lower():
            continue

        queue.append((bus_dest, root_path, 0))

    nodes: list[dict[str, Any]] = []
    curr_index = 0

    while queue and len(nodes) < max_nodes:
        if time.monotonic() >= deadline:
            break
        dest, obj_path, depth = queue.popleft()

        # Lecture du nom
        name = ""
        if time.monotonic() < deadline:
            try:
                cmd_n = [busctl_bin, *addr_args, "get-property", dest, obj_path, "org.a11y.atspi.Accessible", "Name"]
                res_n = subprocess.run(cmd_n, capture_output=True, timeout=_remaining(1.0), text=True, check=False)
                if res_n.returncode == 0 and 's "' in res_n.stdout:
                    name = res_n.stdout.split('s "', 1)[1].split('"', 1)[0]
            except Exception as exc:
                logger.debug("Échec de lecture du nom Accessible: %s", exc)

        # Lecture du rôle
        role = "application" if depth == 0 else "unknown"
        if time.monotonic() < deadline:
            try:
                cmd_r = [busctl_bin, *addr_args, "call", dest, obj_path, "org.a11y.atspi.Accessible", "GetRoleName"]
                res_r = subprocess.run(cmd_r, capture_output=True, timeout=_remaining(1.0), text=True, check=False)
                if res_r.returncode == 0 and 's "' in res_r.stdout:
                    role = res_r.stdout.split('s "', 1)[1].split('"', 1)[0]
            except Exception as exc:
                logger.debug("Échec de lecture du rôle Accessible: %s", exc)

        # Actions disponibles sur le composant (collectées uniquement pour les contrôles interactifs descendants)
        actions: list[str] = []
        if depth > 0 and time.monotonic() < deadline:
            actions = _dbus_get_actions(busctl_bin, addr_args, dest, obj_path, timeout=_remaining(0.2))

        # Exploration des enfants descendants si la profondeur maximale n'est pas atteinte
        child_count = 0
        if depth < max_depth and (len(nodes) + len(queue)) < max_nodes and time.monotonic() < deadline:
            children = _dbus_read_children(busctl_bin, addr_args, dest, obj_path, timeout=_remaining(1.0))
            child_count = len(children)
            for child_dest, child_path in children:
                if (len(nodes) + len(queue)) >= max_nodes:
                    break
                queue.append((child_dest, child_path, depth + 1))

        nodes.append(
            {
                "index": curr_index,
                "object_ref": f"{dest}{obj_path}",
                "name": name or ("application" if depth == 0 else ""),
                "role": role,
                "depth": depth,
                "children_count": child_count,
                "states": ["visible", "showing"],
                "actions": actions,
            }
        )
        curr_index += 1

    return nodes


def _run_python_atspi_cli(args: list[str]) -> None:
    """Fallback d'exécution du médiateur AT-SPI en pur Python."""
    if not args or args[0] in ("-h", "--help", "help"):
        print(
            "gui-agent-atspi: interface de médiation AT-SPI / D-Bus (commandes: doctor, apps, state, action, value, mcp)"
        )
        return

    cmd = args[0]
    if cmd == "doctor":
        bus_addr = os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")
        status = "ok" if bus_addr or os.path.exists(f"/run/user/{os.getuid()}/bus") else "no_bus"
        print(json.dumps({"status": status, "engine": "python-fallback", "bus": bus_addr}))
    elif cmd == "apps":
        apps_tree = _dbus_get_app_state(max_depth=0)
        app_names = [n["name"] for n in apps_tree if n.get("name")]
        print(json.dumps(app_names))
    elif cmd == "state":
        app_filt = args[1] if len(args) > 1 else None
        state_tree = _dbus_get_app_state(app_name=app_filt)
        if not state_tree:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "layer": "accessibility",
                        "error": "Moteur natif gui-agent-atspi introuvable et aucun contrôle accessible D-Bus détecté",
                        "count": 0,
                        "tree": [],
                    }
                )
            )
        else:
            print(
                json.dumps(
                    {
                        "status": "success",
                        "layer": "accessibility",
                        "count": len(state_tree),
                        "tree": state_tree,
                        "degraded": True,
                    }
                )
            )
    elif cmd == "action":
        target = args[1] if len(args) > 1 else ""
        act_name = args[2] if len(args) > 2 else "0"
        ok = _dbus_call_action_or_value("perform_action", {"element_identifier": target, "action": act_name})
        print(json.dumps({"ok": ok}))
    elif cmd == "value":
        target = args[1] if len(args) > 1 else ""
        val = args[2] if len(args) > 2 else ""
        ok = _dbus_call_action_or_value("set_value", {"element_identifier": target, "value": val})
        print(json.dumps({"ok": ok}))
    elif cmd == "mcp":
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                req = json.loads(line_str)
            except Exception:
                sys.stdout.write(
                    json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
                    + "\n"
                )
                sys.stdout.flush()
                continue

            if not isinstance(req, dict):
                sys.stdout.write(
                    json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}})
                    + "\n"
                )
                sys.stdout.flush()
                continue

            req_id = req.get("id")
            method = req.get("method")

            # Ignorer les notifications sans id (ex: notifications/initialized)
            if req_id is None:
                continue

            try:
                if method == "initialize":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "gui-agent-atspi-py", "version": "0.1.0"},
                        },
                    }
                elif method == "tools/list":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "get_app_state",
                                    "description": "Extrait l'arbre d'accessibilité d'une application ou du bureau",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "app_name": {"type": "string", "description": "Nom de l'application cible"},
                                            "include_screenshot": {"type": "boolean", "default": False},
                                        },
                                    },
                                },
                                {
                                    "name": "perform_action",
                                    "description": "Déclenche une action AT-SPI sur un composant accessible",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "element_identifier": {"type": "string"},
                                            "action": {"type": "string", "default": "activate"},
                                            "snapshot_id": {"type": "string"},
                                        },
                                        "required": ["element_identifier"],
                                    },
                                },
                                {
                                    "name": "set_value",
                                    "description": "Modifie la valeur textuelle d'un composant accessible",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "element_identifier": {"type": "string"},
                                            "value": {"type": "string"},
                                            "snapshot_id": {"type": "string"},
                                        },
                                        "required": ["element_identifier", "value"],
                                    },
                                },
                            ]
                        },
                    }
                elif method == "tools/call":
                    params = req.get("params", {})
                    t_name = str(params.get("name", ""))
                    t_args = params.get("arguments", {})
                    if not isinstance(t_args, dict):
                        t_args = {}
                    ok = _dbus_call_action_or_value(t_name, t_args)
                    res = {"jsonrpc": "2.0", "id": req_id, "result": {"structuredContent": {"ok": ok}}}
                else:
                    res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
            except Exception as loop_exc:
                sys.stdout.write(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {"code": -32603, "message": f"Internal error: {loop_exc}"},
                        }
                    )
                    + "\n"
                )
                sys.stdout.flush()
                continue
    else:
        print(f"Commande inconnue: {cmd}", file=sys.stderr)
        sys.exit(1)


def main_cli() -> None:
    """CLI unifié gui-agent-atspi déployé nativement avec le paquet Python.

    Délègue directement au binaire compilé Rust natif à haute performance (<50ms)
    si présent, compile à la volée si Cargo est disponible, ou exécute le fallback
    programmé.
    """
    args = sys.argv[1:]
    # 1. Recherche prioritaire du binaire Rust natif (ELF)
    native_bin = find_atspi_mediator_binary(exclude_scripts=True)
    if native_bin and os.path.isfile(native_bin) and os.access(native_bin, os.X_OK):
        with contextlib.suppress(OSError):
            res = subprocess.run([native_bin, *args], check=False)
            sys.exit(res.returncode)

    # 2. Si le binaire compilé n'est pas encore disponible, tentative de compilation locale via Cargo
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cargo_manifest = os.path.join(project_root, "Cargo.toml")
    if os.path.isfile(cargo_manifest) and shutil.which("cargo"):
        try:
            logger.info("Compilation initiale du médiateur Rust gui-agent-atspi via Cargo...")
            subprocess.run(
                ["cargo", "build", "--release", "--manifest-path", cargo_manifest, "--bin", "gui-agent-atspi"],
                cwd=project_root,
                capture_output=True,
                check=True,
            )
            built_bin = os.path.join(project_root, "target", "release", "gui-agent-atspi")
            if os.path.isfile(built_bin) and os.access(built_bin, os.X_OK):
                built_res = subprocess.run([built_bin, *args], check=False)
                sys.exit(built_res.returncode)
        except Exception as exc:
            logger.debug("Échec de compilation à la volée: %s", exc)

    # 3. Fallback d'exécution Python pour les commandes de base
    _run_python_atspi_cli(args)


def _call_mcp_action_or_value(tool_name: str, arguments: dict[str, Any], timeout: float = 15.0) -> bool:
    """Invoque l'outil MCP perform_action ou set_value via le serveur stdio Rust ou le fallback D-Bus."""
    try:
        binary = find_atspi_mediator_binary(exclude_scripts=True)
    except TypeError:
        binary = find_atspi_mediator_binary()
    if not binary:
        logger.info("Binaire AT-SPI Rust absent, repli sur l'invocation D-Bus directe pour %s", tool_name)
        return _dbus_call_action_or_value(tool_name, arguments, timeout=timeout)

    try:
        proc = subprocess.Popen(
            [binary, "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as exc:
        logger.error("Impossible de lancer le processus MCP %s: %s", binary, exc)
        return False

    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "gui-agent", "version": "0.1.0"},
        },
    }
    call_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    payload = (
        json.dumps(init_req)
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
        + "\n"
        + json.dumps(call_req)
        + "\n"
    )

    try:
        stdout_data, _ = proc.communicate(input=payload, timeout=timeout)
        for line in stdout_data.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception as parse_exc:
                logger.debug("Ligne non JSON ignorée dans la sortie MCP: %s (%s)", line, parse_exc)
                continue
            if data.get("id") == 2:
                result = data.get("result", {})
                structured = result.get("structuredContent")
                if isinstance(structured, dict) and "ok" in structured:
                    return bool(structured["ok"])

                content = result.get("content", [])
                if content and isinstance(content[0], dict):
                    raw_text = content[0].get("text", "")
                    try:
                        content_json = json.loads(raw_text)
                        if isinstance(content_json, dict) and "ok" in content_json:
                            return bool(content_json["ok"])
                    except Exception as json_exc:
                        logger.debug("Échec du parsing JSON du champ content: %s", json_exc)

                return False
        return False
    except subprocess.TimeoutExpired:
        logger.error("Timeout dépassé (%.1fs) lors de l'appel MCP %s", timeout, tool_name)
        try:
            proc.kill()
            proc.wait(timeout=1.0)
        except Exception as kill_exc:
            logger.debug("Échec du kill après timeout: %s", kill_exc)
        return False
    except Exception as exc:
        logger.error("Erreur lors de l'appel MCP %s: %s", tool_name, exc)
        return False
    finally:
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=1.0)
            except Exception as term_exc:
                logger.debug("Échec de la terminaison du processus MCP: %s", term_exc)
                try:
                    proc.kill()
                except Exception as kill_exc:
                    logger.debug("Échec du kill du processus MCP: %s", kill_exc)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            if stream and hasattr(stream, "closed") and not stream.closed:
                try:
                    stream.close()
                except Exception as close_exc:
                    logger.debug("Échec de la fermeture de flux MCP: %s", close_exc)


def _format_snapshot_result(
    tree: list[dict[str, Any]],
    app_name: str | None,
    include_screenshot: bool,
    snapshot_id: str | None = None,
) -> dict[str, Any]:
    """Enregistre l'arbre dans le cache de snapshots et formate le dictionnaire de retour."""
    global _last_snapshot_id

    new_cache: dict[str, str] = {}
    for node in tree:
        if isinstance(node, dict):
            idx = node.get("index")
            obj_ref = node.get("object_ref")
            if idx is not None and obj_ref:
                new_cache[str(idx)] = str(obj_ref)

    sid = snapshot_id or uuid.uuid4().hex[:12]
    with _cache_lock:
        if len(_snapshots) >= 20:
            oldest_id = next(iter(_snapshots))
            del _snapshots[oldest_id]
        _snapshots[sid] = {
            "nodes": new_cache,
            "app_name": app_name,
        }
        _last_node_cache.clear()
        _last_node_cache.update(new_cache)
        _last_snapshot_id = sid

    result: dict[str, Any] = {
        "status": "success",
        "layer": "accessibility",
        "snapshot_id": sid,
        "count": len(tree),
        "tree": tree,
        "include_screenshot": include_screenshot,
    }
    if include_screenshot:
        with contextlib.suppress(Exception):
            from gui_agent.layers.input_emulation import screen_capture

            cap = screen_capture()
            if cap.get("status") == "success":
                result["screenshot"] = cap.get("image")

    return result


def get_app_state(include_screenshot: bool = False, app_name: str | None = None) -> dict[str, Any]:
    """Extrait l'arbre d'accessibilité applicatif en JSON texte pur via AT-SPI.

    Args:
        include_screenshot: Si True, capture et inclut également l'image de l'écran.
        app_name: Nom optionnel de l'application ou filtre textuel de fenêtre.

    Returns:
        dict contenant status, layer, count, tree et include_screenshot.
    """
    # 1. Vérification du mock
    if _mock_state is not None:
        mock_res = dict(_mock_state)
        mock_res["layer"] = "accessibility"
        mock_res["include_screenshot"] = include_screenshot
        tree_mock = mock_res.get("tree", [])
        if isinstance(tree_mock, list):
            formatted = _format_snapshot_result(
                tree_mock, app_name, include_screenshot, snapshot_id=mock_res.get("snapshot_id")
            )
            formatted.update(mock_res)
            return formatted
        return mock_res

    # 2. Résolution de l'exécutable Rust
    binary = find_atspi_mediator_binary()
    if not binary:
        _clear_accessibility_cache()
        return {
            "status": "error",
            "layer": "accessibility",
            "error": "Moteur Rust AT-SPI introuvable (computer-use-linux ou gui-agent-atspi manquant)",
            "include_screenshot": include_screenshot,
            "tree": [],
            "count": 0,
        }

    # 3. Commande CLI d'extraction de l'arbre
    cmd = [binary, "state"]
    if app_name:
        cmd.append(app_name)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10.0,
            check=False,
        )
        if proc.returncode != 0:
            _clear_accessibility_cache()
            err_msg = proc.stderr.strip() or f"Code sortie {proc.returncode}"
            logger.warning("Échec de l'extraction de l'arbre AT-SPI : %s", err_msg)
            return {
                "status": "error",
                "layer": "accessibility",
                "error": err_msg,
                "include_screenshot": include_screenshot,
                "tree": [],
                "count": 0,
            }

        tree_data = json.loads(proc.stdout)
        # Validation stricte du format de sortie de l'arbre
        if isinstance(tree_data, list):
            tree = tree_data
        elif isinstance(tree_data, dict) and isinstance(tree_data.get("tree"), list):
            if tree_data.get("status") == "error":
                _clear_accessibility_cache()
                return {
                    "status": "error",
                    "layer": "accessibility",
                    "error": str(tree_data.get("error") or "Échec de l'extraction AT-SPI"),
                    "include_screenshot": include_screenshot,
                    "tree": [],
                    "count": 0,
                }
            tree = tree_data["tree"]
        else:
            _clear_accessibility_cache()
            return {
                "status": "error",
                "layer": "accessibility",
                "error": "Format de sortie AT-SPI non pris en charge (liste ou dict avec 'tree' attendu)",
                "include_screenshot": include_screenshot,
                "tree": [],
                "count": 0,
            }

        return _format_snapshot_result(tree, app_name, include_screenshot)

    except subprocess.TimeoutExpired:
        _clear_accessibility_cache()
        logger.error("Timeout dépassé (10s) lors de la lecture de l'arbre AT-SPI")
        return {
            "status": "error",
            "layer": "accessibility",
            "error": "Timeout de lecture AT-SPI dépassé (10s)",
            "include_screenshot": include_screenshot,
            "tree": [],
            "count": 0,
        }
    except Exception as exc:
        _clear_accessibility_cache()
        logger.error("Erreur inattendue lors de l'extraction AT-SPI: %s", exc)
        return {
            "status": "error",
            "layer": "accessibility",
            "error": str(exc),
            "include_screenshot": include_screenshot,
            "tree": [],
            "count": 0,
        }


def perform_action(
    element_id: str | int,
    action: str = "activate",
    snapshot_id: str | None = None,
    timeout: float = 15.0,
) -> bool:
    """Déclenche l'action du composant accessible directement en mémoire par le bus AT-SPI.

    Args:
        element_id: Index numérique de l'élément (ex: "42") ou référence AT-SPI (ex: ":1.14/path").
        action: Nom de l'action à exécuter (ex: "activate", "press", "click", "toggle").
        snapshot_id: Identifiant du snapshot pour s'assurer que l'index correspond à la vue actuelle (obligatoire si element_id est numérique).
        timeout: Délai maximal en secondes alloué à l'opération (défaut: 15.0s).

    Returns:
        bool indiquant si l'action a été déclenchée avec succès.
    """
    if _mock_action_handler is not None:
        if callable(_mock_action_handler):
            return bool(_mock_action_handler(element_id, action))
        return bool(_mock_action_handler)

    element_id = str(element_id)

    with _cache_lock:
        if snapshot_id is not None and snapshot_id != _last_snapshot_id:
            logger.error(
                "Snapshot ID '%s' périmé (dernier snapshot valide: '%s'). Action rejetée.",
                snapshot_id,
                _last_snapshot_id,
            )
            return False

    if element_id.isdigit():
        if not snapshot_id:
            logger.error(
                "L'index numérique %s requiert obligatoirement un 'snapshot_id' valide issu de get_app_state() pour garantir la cohérence sémantique et éviter d'agir sur un état applicatif obsolète ou différent. Action rejetée.",
                element_id,
            )
            return False

        with _cache_lock:
            if snapshot_id != _last_snapshot_id:
                logger.error(
                    "Snapshot ID '%s' périmé pour l'index %s (dernier snapshot: '%s'). Action rejetée.",
                    snapshot_id,
                    element_id,
                    _last_snapshot_id,
                )
                return False
            snapshot_entry = _snapshots.get(snapshot_id)
            if snapshot_entry is None:
                logger.error(
                    "Snapshot ID '%s' inconnu ou expiré pour l'index %s. Action rejetée.",
                    snapshot_id,
                    element_id,
                )
                return False
            resolved_ref = snapshot_entry["nodes"].get(element_id)

        if not resolved_ref:
            logger.error(
                "Index d'élément %s introuvable dans le snapshot '%s' (app: %s). Action rejetée.",
                element_id,
                snapshot_id,
                snapshot_entry.get("app_name"),
            )
            return False

        args: dict[str, Any] = {
            "action": action,
            "element_identifier": resolved_ref,
            "element_index": int(element_id),
        }
    else:
        args = {
            "action": action,
            "element_identifier": element_id,
        }

    return _call_mcp_action_or_value("perform_action", args, timeout=timeout)


def set_value(
    element_id: str | int,
    text: str,
    snapshot_id: str | None = None,
    timeout: float = 15.0,
) -> bool:
    """Écrit directement la valeur textuelle dans la mémoire du composant via AT-SPI.

    Args:
        element_id: Index numérique de l'élément (ex: "42") ou référence AT-SPI (ex: ":1.14/path").
        text: Valeur textuelle ou numérique à assigner au composant.
        snapshot_id: Identifiant du snapshot pour garantir que l'index correspond à la vue actuelle (obligatoire si element_id est numérique).
        timeout: Délai maximal en secondes alloué à l'opération (défaut: 15.0s).

    Returns:
        bool indiquant si l'assignation a été acceptée par le composant.
    """
    if _mock_value_handler is not None:
        if callable(_mock_value_handler):
            return bool(_mock_value_handler(element_id, text))
        return bool(_mock_value_handler)

    element_id = str(element_id)

    with _cache_lock:
        if snapshot_id is not None and snapshot_id != _last_snapshot_id:
            logger.error(
                "Snapshot ID '%s' périmé (dernier snapshot valide: '%s'). Écriture de valeur rejetée.",
                snapshot_id,
                _last_snapshot_id,
            )
            return False

    if element_id.isdigit():
        if not snapshot_id:
            logger.error(
                "L'index numérique %s requiert obligatoirement un 'snapshot_id' valide issu de get_app_state() pour garantir la cohérence sémantique et éviter d'agir sur un état applicatif obsolète ou différent. Écriture de valeur rejetée.",
                element_id,
            )
            return False

        with _cache_lock:
            if snapshot_id != _last_snapshot_id:
                logger.error(
                    "Snapshot ID '%s' périmé pour l'index %s (dernier snapshot: '%s'). Écriture de valeur rejetée.",
                    snapshot_id,
                    element_id,
                    _last_snapshot_id,
                )
                return False
            snapshot_entry = _snapshots.get(snapshot_id)
            if snapshot_entry is None:
                logger.error(
                    "Snapshot ID '%s' inconnu ou expiré pour l'index %s. Écriture de valeur rejetée.",
                    snapshot_id,
                    element_id,
                )
                return False
            resolved_ref = snapshot_entry["nodes"].get(element_id)

        if not resolved_ref:
            logger.error(
                "Index d'élément %s introuvable dans le snapshot '%s' (app: %s). Écriture de valeur rejetée.",
                element_id,
                snapshot_id,
                snapshot_entry.get("app_name"),
            )
            return False

        args: dict[str, Any] = {
            "element_identifier": resolved_ref,
            "element_index": int(element_id),
            "value": text,
        }
    else:
        args = {
            "element_identifier": element_id,
            "value": text,
        }

    return _call_mcp_action_or_value("set_value", args, timeout=timeout)
