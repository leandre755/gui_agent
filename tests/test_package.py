"""Tests unitaires pour le package gui-agent."""

import gui_agent
import mcp_gui_server
from gui_agent.server import normalize_coordinates, translate_key


def test_package_metadata():
    """Valide les métadonnées et la structure d'export du package."""
    assert gui_agent.__version__ == "0.1.0"
    assert len(gui_agent.__all__) > 20


def test_fastmcp_tools_registration():
    """Vérifie l'enregistrement exact des 21 outils FastMCP du serveur."""
    tools = gui_agent.mcp._tool_manager.list_tools()
    tool_names = {t.name for t in tools}
    assert len(tools) == 21
    assert "gui_get_screen_info" in tool_names
    assert "gui_take_screenshot" in tool_names
    assert "gui_mouse_click" in tool_names
    assert "gui_mouse_move" in tool_names
    assert "gui_mouse_drag" in tool_names
    assert "gui_mouse_scroll" in tool_names
    assert "gui_keyboard_type" in tool_names
    assert "gui_keyboard_press" in tool_names
    assert "gui_clipboard_get" in tool_names
    assert "gui_clipboard_set" in tool_names
    assert "gui_window_list" in tool_names
    assert "gui_window_focus" in tool_names
    assert "gui_window_resize_move" in tool_names
    assert "gui_window_close" in tool_names
    assert "gui_app_launch" in tool_names
    assert "gui_find_template" in tool_names
    assert "gui_find_text" in tool_names
    assert "gui_click_text" in tool_names
    assert "gui_web_action" in tool_names
    assert "gui_start_video_recording" in tool_names
    assert "gui_stop_video_recording" in tool_names


def test_backward_compatibility():
    """Assure la rétrocompatibilité d'import depuis mcp_gui_server."""
    assert hasattr(mcp_gui_server, "gui_get_screen_info")
    assert hasattr(mcp_gui_server, "gui_take_screenshot")
    assert hasattr(mcp_gui_server, "normalize_coordinates")
    assert mcp_gui_server.mcp is gui_agent.mcp


def test_normalize_coordinates():
    """Valide la transformation et normalisation des coordonnées d'écran."""
    # Coordonnées réelles (normalized=False)
    x, y = normalize_coordinates(500, 300, normalized=False)
    assert x == 500
    assert y == 300


def test_translate_key():
    """Valide la table de correspondance des touches clavier."""
    assert translate_key("ctrl") == "control"
    assert translate_key("alt") == "alt"
    assert translate_key("super") == "Super_L"
    assert translate_key("enter") == "Return"
    assert translate_key("escape") == "Escape"


def test_installation_and_uninstallation_scripts_presence():
    """Vérifie la présence et la taille minimale des scripts d'installation/désinstallation."""
    import os

    assert os.path.isfile("install.sh"), "install.sh manquant"
    assert os.path.isfile("install.ps1"), "install.ps1 manquant"
    assert os.path.isfile("uninstall.sh"), "uninstall.sh manquant"
    assert os.path.isfile("uninstall.ps1"), "uninstall.ps1 manquant"
    assert os.path.getsize("install.sh") > 100
    assert os.path.getsize("install.ps1") > 100
    assert os.path.getsize("uninstall.sh") > 100
    assert os.path.getsize("uninstall.ps1") > 100


def test_install_doc_structure():
    """Valide la conformité structurelle du guide d'installation INSTALL.md."""
    import os

    doc_path = "INSTALL.md"
    assert os.path.isfile(doc_path), "INSTALL.md manquant"
    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    assert "Guide d'Installation" in content
    assert "Microsoft Windows" in content
    assert "Linux & macOS" in content
    assert "Dépannage" in content
    assert "powershell" in content.lower()
    assert "uv tool install" in content
    assert "install.ps1" in content
    assert "uninstall.ps1" in content


def test_gui_take_screenshot_output_path(tmp_path):
    """Teste le comportement sécurisé et exhaustif de output_path dans gui_take_screenshot."""
    import inspect
    import os
    from PIL import Image

    sig = inspect.signature(gui_agent.gui_take_screenshot)
    assert "save_to_artifacts" not in sig.parameters, "save_to_artifacts ne doit plus exister dans la signature"
    assert "output_path" in sig.parameters, "output_path doit être présent dans la signature"

    # 1. Cas nominal : capture PNG avec output_path absolu valide
    target_file = str(tmp_path / "nested" / "custom_screenshot.png")
    res = gui_agent.gui_take_screenshot(apply_grid=True, format="png", output_path=target_file)
    assert res.get("status") == "success"
    assert res.get("screenshot_path") == target_file
    assert os.path.isfile(target_file)
    assert os.path.isfile(res["raw_screenshot_path"])
    with Image.open(target_file) as img:
        assert img.format == "PNG"

    # 1.b Cas nominal : capture PNG avec output_path relatif dans un répertoire de travail contrôlé
    orig_cwd = os.getcwd()
    try:
        work_dir = tmp_path / "relative_workdir"
        work_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(work_dir)
        rel_output = os.path.join("nested_rel", "rel_screenshot.png")
        res_rel = gui_agent.gui_take_screenshot(apply_grid=False, format="png", output_path=rel_output)
        assert res_rel.get("status") == "success"
        expected_abs = str((work_dir / "nested_rel" / "rel_screenshot.png").resolve())
        assert res_rel.get("screenshot_path") == expected_abs
        assert os.path.isfile(expected_abs)
    finally:
        os.chdir(orig_cwd)

    # 2. Cas nominal : capture JPEG avec output_path valide
    target_jpg = str(tmp_path / "nested" / "custom_screenshot.jpg")
    res_jpg = gui_agent.gui_take_screenshot(apply_grid=False, format="jpeg", output_path=target_jpg)
    assert res_jpg.get("status") == "success"
    assert res_jpg.get("screenshot_path") == target_jpg
    assert os.path.isfile(target_jpg)
    with Image.open(target_jpg) as img_jpg:
        assert img_jpg.format == "JPEG"

    # 3. Cas de sécurité : rejet strict si conflit entre extension et format demandé
    conflict_file = str(tmp_path / "conflicting.png")
    res_err = gui_agent.gui_take_screenshot(apply_grid=False, format="jpeg", output_path=conflict_file)
    assert res_err.get("status") == "error"
    assert "Incohérence d'extension" in res_err.get("message", "")
    assert not os.path.exists(conflict_file)

    # 4. Cas de sécurité : rejet si output_path est un répertoire existant
    existing_dir = str(tmp_path / "existing_dir")
    os.makedirs(existing_dir, exist_ok=True)
    res_dir_err = gui_agent.gui_take_screenshot(apply_grid=False, output_path=existing_dir)
    assert res_dir_err.get("status") == "error"
    assert "est un dossier existant" in res_dir_err.get("message", "")

    # 5. Cas de sécurité : protection contre l'écrasement de fichier existant (renommage (1), (2)...)
    existing_file = str(tmp_path / "protected_screenshot.png")
    with open(existing_file, "w", encoding="utf-8") as f:
        f.write("contenu_original_intact")

    res_collision = gui_agent.gui_take_screenshot(apply_grid=False, output_path=existing_file)
    assert res_collision.get("status") == "success"
    assert res_collision.get("renamed_due_to_conflict") is True
    expected_renamed = str(tmp_path / "protected_screenshot (1).png")
    assert res_collision.get("screenshot_path") == expected_renamed
    assert os.path.isfile(expected_renamed)

    # Vérification que le fichier initial n'a pas été altéré
    with open(existing_file, encoding="utf-8") as f:
        assert f.read() == "contenu_original_intact"

    # Deuxième collision -> progression du suffixe vers (2)
    res_collision_2 = gui_agent.gui_take_screenshot(apply_grid=False, output_path=existing_file)
    assert res_collision_2.get("status") == "success"
    assert res_collision_2.get("renamed_due_to_conflict") is True
    expected_renamed_2 = str(tmp_path / "protected_screenshot (2).png")
    assert res_collision_2.get("screenshot_path") == expected_renamed_2
    assert os.path.isfile(expected_renamed_2)

    # 6. Cas de configuration : vérification du chemin absolu avec GUI_AGENT_SCREENSHOTS_DIR relatif
    orig_screenshots_dir = gui_agent.server.SCREENSHOTS_DIR
    orig_cwd_dir = os.getcwd()
    try:
        custom_workdir = tmp_path / "custom_workdir"
        custom_workdir.mkdir(parents=True, exist_ok=True)
        os.chdir(custom_workdir)
        gui_agent.server.SCREENSHOTS_DIR = "relative_screenshots_dir"
        os.makedirs(gui_agent.server.SCREENSHOTS_DIR, exist_ok=True)

        res_default = gui_agent.gui_take_screenshot(apply_grid=False, output_path=None)
        assert res_default.get("status") == "success"
        scr_path = res_default.get("screenshot_path")
        raw_scr_path = res_default.get("raw_screenshot_path")
        assert os.path.isabs(scr_path), f"screenshot_path doit être absolu : {scr_path}"
        assert os.path.isabs(raw_scr_path), f"raw_screenshot_path doit être absolu : {raw_scr_path}"
        assert os.path.isfile(scr_path)
        assert os.path.isfile(raw_scr_path)
    finally:
        gui_agent.server.SCREENSHOTS_DIR = orig_screenshots_dir
        os.chdir(orig_cwd_dir)

    # 7. Cas de résilience : nettoyage strict des réservations de fichiers en cas d'erreur de sauvegarde
    failure_target = str(tmp_path / "failure_cleanup" / "capture.png")
    from unittest.mock import patch

    def fail_save(self, *args, **kwargs):
        raise OSError("Simulation d'erreur disque lors de l'enregistrement")

    with patch.object(Image.Image, "save", fail_save):
        res_fail = gui_agent.gui_take_screenshot(apply_grid=False, output_path=failure_target)
        assert res_fail.get("status") == "error"

    # Le fichier final réservé a été nettoyé
    assert not os.path.exists(failure_target), "Le fichier réservé n'a pas été nettoyé après l'échec"

    # La nouvelle tentative ultérieure ne subit aucune fausse collision et utilise le nom d'origine
    res_retry = gui_agent.gui_take_screenshot(apply_grid=False, output_path=failure_target)
    assert res_retry.get("status") == "success"
    assert res_retry.get("screenshot_path") == failure_target
    assert res_retry.get("renamed_due_to_conflict") is False
    assert os.path.isfile(failure_target)
