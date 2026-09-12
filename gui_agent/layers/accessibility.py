"""Couche d'Accessibilité Programmatique (AT-SPI / D-Bus).

Ce module assure la médiation sémantique avec l'arbre d'accessibilité Linux (AT-SPI2 / D-Bus)
en déléguant au moteur natif en Rust pour garantir des lectures rapides (< 50 ms),
l'inspection d'arbres hiérarchiques et des actions directes en mémoire RAM sans cécité visuelle.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import threading
from typing import Any
import uuid

logger = logging.getLogger("gui_agent.layers.accessibility")

# Mock d'état pour les tests unitaires et environnements headless sans bus graphique
_mock_state: dict[str, Any] | None = None
_mock_action_handler: Any | None = None
_mock_value_handler: Any | None = None

# Cache en mémoire des correspondances element_index -> object_ref synchronisé par verrou
_last_node_cache: dict[str, str] = {}
_last_snapshot_id: str | None = None
_cache_lock = threading.Lock()


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


def find_atspi_mediator_binary() -> str | None:
    """Détecte l'exécutable du moteur Rust AT-SPI disponible."""
    # 1. Variable d'environnement prioritaire
    custom_bin = os.environ.get("GUI_AGENT_ATSPI_BIN")
    if custom_bin and os.path.isfile(custom_bin) and os.access(custom_bin, os.X_OK):
        return custom_bin

    # 2. Binaire local compilé dans crates/atspi_mediator (release puis debug)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for profile in ("release", "debug"):
        local_bin = os.path.join(project_root, "crates", "atspi_mediator", "target", profile, "gui-agent-atspi")
        if os.path.isfile(local_bin) and os.access(local_bin, os.X_OK):
            return local_bin

    # 3. Exécutable système computer-use-linux (Rust upstream)
    which_bin = shutil.which("computer-use-linux")
    if which_bin:
        return which_bin

    # 4. Chemins NVM éventuels dans le répertoire utilisateur
    user_home = os.path.expanduser("~")
    nvm_dir = os.path.join(user_home, ".nvm", "versions", "node")
    if os.path.isdir(nvm_dir):
        try:
            for node_ver in sorted(os.listdir(nvm_dir), reverse=True):
                candidate = os.path.join(nvm_dir, node_ver, "bin", "computer-use-linux")
                if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                    return candidate
        except OSError as nvm_err:
            logger.debug("Erreur lors du scan du répertoire NVM: %s", nvm_err)

    return None


def _call_mcp_action_or_value(tool_name: str, arguments: dict[str, Any], timeout: float = 5.0) -> bool:
    """Invoque l'outil MCP perform_action ou set_value via le serveur stdio Rust."""
    binary = find_atspi_mediator_binary()
    if not binary:
        logger.warning("Binaire AT-SPI Rust introuvable pour %s", tool_name)
        return False

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


def get_app_state(include_screenshot: bool = False, app_name: str | None = None) -> dict[str, Any]:
    """Extrait l'arbre d'accessibilité applicatif en JSON texte pur via AT-SPI.

    Args:
        include_screenshot: Si True, capture et inclut également l'image de l'écran.
        app_name: Nom optionnel de l'application ou filtre textuel de fenêtre.

    Returns:
        dict contenant status, layer, count, tree et include_screenshot.
    """
    global _last_snapshot_id

    # 1. Vérification du mock
    if _mock_state is not None:
        mock_res = dict(_mock_state)
        mock_res["layer"] = "accessibility"
        mock_res["include_screenshot"] = include_screenshot
        tree_mock = mock_res.get("tree", [])
        if isinstance(tree_mock, list):
            new_cache = {}
            for node in tree_mock:
                if isinstance(node, dict):
                    idx = node.get("index")
                    obj_ref = node.get("object_ref")
                    if idx is not None and obj_ref:
                        new_cache[str(idx)] = str(obj_ref)
            snap_id = mock_res.get("snapshot_id") or uuid.uuid4().hex[:12]
            mock_res["snapshot_id"] = snap_id
            with _cache_lock:
                _last_node_cache.clear()
                _last_node_cache.update(new_cache)
                _last_snapshot_id = snap_id
        return mock_res

    # 2. Résolution de l'exécutable Rust
    binary = find_atspi_mediator_binary()
    if not binary:
        with _cache_lock:
            _last_node_cache.clear()
            _last_snapshot_id = None
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
            with _cache_lock:
                _last_node_cache.clear()
                _last_snapshot_id = None
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
            tree = tree_data["tree"]
        else:
            with _cache_lock:
                _last_node_cache.clear()
                _last_snapshot_id = None
            return {
                "status": "error",
                "layer": "accessibility",
                "error": "Format de sortie AT-SPI non pris en charge (liste ou dict avec 'tree' attendu)",
                "include_screenshot": include_screenshot,
                "tree": [],
                "count": 0,
            }

        # Mise à jour synchronisée du cache des index vers object_ref avec identité de snapshot
        new_cache = {}
        for node in tree:
            if isinstance(node, dict):
                idx = node.get("index")
                obj_ref = node.get("object_ref")
                if idx is not None and obj_ref:
                    new_cache[str(idx)] = str(obj_ref)

        snapshot_id = uuid.uuid4().hex[:12]
        with _cache_lock:
            _last_node_cache.clear()
            _last_node_cache.update(new_cache)
            _last_snapshot_id = snapshot_id

        result: dict[str, Any] = {
            "status": "success",
            "layer": "accessibility",
            "snapshot_id": snapshot_id,
            "count": len(tree),
            "tree": tree,
            "include_screenshot": include_screenshot,
        }

        if include_screenshot:
            try:
                from gui_agent.layers.input_emulation import screen_capture

                cap = screen_capture()
                if cap.get("status") == "success":
                    result["screenshot"] = cap.get("image")
            except Exception as cap_exc:
                logger.warning("Impossible d'agréger la capture d'écran: %s", cap_exc)

        return result

    except subprocess.TimeoutExpired:
        with _cache_lock:
            _last_node_cache.clear()
            _last_snapshot_id = None
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
        with _cache_lock:
            _last_node_cache.clear()
            _last_snapshot_id = None
        logger.error("Erreur inattendue lors de l'extraction AT-SPI: %s", exc)
        return {
            "status": "error",
            "layer": "accessibility",
            "error": str(exc),
            "include_screenshot": include_screenshot,
            "tree": [],
            "count": 0,
        }


def perform_action(element_id: str, action: str = "activate", snapshot_id: str | None = None) -> bool:
    """Déclenche l'action du composant accessible directement en mémoire par le bus AT-SPI.

    Args:
        element_id: Index numérique de l'élément (ex: "42") ou référence AT-SPI (ex: ":1.14/path").
        action: Nom de l'action à exécuter (ex: "activate", "press", "click", "toggle").
        snapshot_id: Identifiant optionnel du snapshot pour s'assurer que l'index correspond à la vue actuelle.

    Returns:
        bool indiquant si l'action a été déclenchée avec succès.
    """
    if _mock_action_handler is not None:
        if callable(_mock_action_handler):
            return bool(_mock_action_handler(element_id, action))
        return bool(_mock_action_handler)

    args: dict[str, Any] = {"action": action}
    if element_id.isdigit():
        args["element_index"] = int(element_id)
        with _cache_lock:
            if snapshot_id is not None and snapshot_id != _last_snapshot_id:
                logger.warning(
                    "Snapshot ID obsolète pour l'index %s (demandé: %s, actuel: %s)",
                    element_id,
                    snapshot_id,
                    _last_snapshot_id,
                )
                resolved_ref = None
            else:
                resolved_ref = _last_node_cache.get(element_id)
        if resolved_ref:
            args["element_identifier"] = resolved_ref
    else:
        args["element_identifier"] = element_id

    return _call_mcp_action_or_value("perform_action", args)


def set_value(element_id: str, text: str, snapshot_id: str | None = None) -> bool:
    """Écrit directement la valeur textuelle dans la mémoire du composant via AT-SPI.

    Args:
        element_id: Index numérique de l'élément (ex: "42") ou référence AT-SPI (ex: ":1.14/path").
        text: Valeur textuelle ou numérique à assigner au composant.
        snapshot_id: Identifiant optionnel du snapshot pour s'assurer que l'index correspond à la vue actuelle.

    Returns:
        bool indiquant si l'assignation a été acceptée par le composant.
    """
    if _mock_value_handler is not None:
        if callable(_mock_value_handler):
            return bool(_mock_value_handler(element_id, text))
        return bool(_mock_value_handler)

    args: dict[str, Any] = {"value": text}
    if element_id.isdigit():
        args["element_index"] = int(element_id)
        with _cache_lock:
            if snapshot_id is not None and snapshot_id != _last_snapshot_id:
                logger.warning(
                    "Snapshot ID obsolète pour l'index %s (demandé: %s, actuel: %s)",
                    element_id,
                    snapshot_id,
                    _last_snapshot_id,
                )
                resolved_ref = None
            else:
                resolved_ref = _last_node_cache.get(element_id)
        if resolved_ref:
            args["element_identifier"] = resolved_ref
    else:
        args["element_identifier"] = element_id

    return _call_mcp_action_or_value("set_value", args)
