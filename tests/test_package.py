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


def test_gui_take_screenshot_output_path_nominal_png(tmp_path):
    """Teste le cas nominal d'enregistrement PNG avec output_path absolu."""
    import inspect
    import os
    from PIL import Image

    sig = inspect.signature(gui_agent.gui_take_screenshot)
    assert "save_to_artifacts" not in sig.parameters, "save_to_artifacts ne doit plus exister dans la signature"
    assert "output_path" in sig.parameters, "output_path doit être présent dans la signature"

    target_file = str(tmp_path / "nested" / "custom_screenshot.png")
    res = gui_agent.gui_take_screenshot(apply_grid=True, format="png", output_path=target_file)
    assert res.get("status") == "success"
    assert res.get("screenshot_path") == target_file
    assert os.path.isfile(target_file)
    assert os.path.isfile(res["raw_screenshot_path"])
    with Image.open(target_file) as img:
        assert img.format == "PNG"


def test_gui_take_screenshot_output_path_relative(tmp_path, monkeypatch):
    """Teste la résolution absolue d'un output_path relatif dans un répertoire contrôlé."""
    import os

    work_dir = tmp_path / "relative_workdir"
    work_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(work_dir)
    rel_output = os.path.join("nested_rel", "rel_screenshot.png")
    res_rel = gui_agent.gui_take_screenshot(apply_grid=False, format="png", output_path=rel_output)
    assert res_rel.get("status") == "success"
    expected_abs = str((work_dir / "nested_rel" / "rel_screenshot.png").resolve())
    assert res_rel.get("screenshot_path") == expected_abs
    assert os.path.isfile(expected_abs)


def test_gui_take_screenshot_output_path_jpeg(tmp_path):
    """Teste le cas nominal d'enregistrement JPEG avec output_path valide."""
    import os
    from PIL import Image

    target_jpg = str(tmp_path / "nested" / "custom_screenshot.jpg")
    res_jpg = gui_agent.gui_take_screenshot(apply_grid=False, format="jpeg", output_path=target_jpg)
    assert res_jpg.get("status") == "success"
    assert res_jpg.get("screenshot_path") == target_jpg
    assert os.path.isfile(target_jpg)
    with Image.open(target_jpg) as img_jpg:
        assert img_jpg.format == "JPEG"


def test_gui_take_screenshot_output_path_extension_conflict(tmp_path):
    """Teste le rejet strict lors d'un conflit entre l'extension de fichier et le format demandé."""
    import os

    conflict_file = str(tmp_path / "conflicting.png")
    res_err = gui_agent.gui_take_screenshot(apply_grid=False, format="jpeg", output_path=conflict_file)
    assert res_err.get("status") == "error"
    assert "Incohérence d'extension" in res_err.get("message", "")
    assert not os.path.exists(conflict_file)


def test_gui_take_screenshot_output_path_directory_rejected(tmp_path):
    """Teste le rejet strict si output_path correspond à un répertoire existant."""
    import os

    existing_dir = str(tmp_path / "existing_dir")
    os.makedirs(existing_dir, exist_ok=True)
    res_dir_err = gui_agent.gui_take_screenshot(apply_grid=False, output_path=existing_dir)
    assert res_dir_err.get("status") == "error"
    assert "est un dossier existant" in res_dir_err.get("message", "")


def test_gui_take_screenshot_output_path_collision_suffixes(tmp_path):
    """Teste la protection anti-écrasement par incrémentation atomique des suffixes (1), (2)..."""
    import os

    existing_file = str(tmp_path / "protected_screenshot.png")
    with open(existing_file, "w", encoding="utf-8") as f:
        f.write("contenu_original_intact")

    res_collision = gui_agent.gui_take_screenshot(apply_grid=False, output_path=existing_file)
    assert res_collision.get("status") == "success"
    assert res_collision.get("renamed_due_to_conflict") is True
    expected_renamed = str(tmp_path / "protected_screenshot (1).png")
    assert res_collision.get("screenshot_path") == expected_renamed
    assert os.path.isfile(expected_renamed)

    with open(existing_file, encoding="utf-8") as f:
        assert f.read() == "contenu_original_intact"

    res_collision_2 = gui_agent.gui_take_screenshot(apply_grid=False, output_path=existing_file)
    assert res_collision_2.get("status") == "success"
    assert res_collision_2.get("renamed_due_to_conflict") is True
    expected_renamed_2 = str(tmp_path / "protected_screenshot (2).png")
    assert res_collision_2.get("screenshot_path") == expected_renamed_2
    assert os.path.isfile(expected_renamed_2)


def test_gui_take_screenshot_relative_screenshots_dir(tmp_path, monkeypatch):
    """Teste la normalisation absolue lorsque GUI_AGENT_SCREENSHOTS_DIR est configuré avec un chemin relatif."""
    import os

    custom_workdir = tmp_path / "custom_workdir"
    custom_workdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(custom_workdir)
    monkeypatch.setattr(gui_agent.server, "SCREENSHOTS_DIR", "relative_screenshots_dir")
    os.makedirs("relative_screenshots_dir", exist_ok=True)

    res_default = gui_agent.gui_take_screenshot(apply_grid=False, output_path=None)
    assert res_default.get("status") == "success"
    scr_path = res_default.get("screenshot_path")
    raw_scr_path = res_default.get("raw_screenshot_path")
    assert os.path.isabs(scr_path), f"screenshot_path doit être absolu : {scr_path}"
    assert os.path.isabs(raw_scr_path), f"raw_screenshot_path doit être absolu : {raw_scr_path}"
    assert os.path.isfile(scr_path)
    assert os.path.isfile(raw_scr_path)


def test_gui_take_screenshot_failure_cleanup(tmp_path):
    """Teste le nettoyage strict des réservations lors d'un échec de sauvegarde."""
    import os
    from PIL import Image
    from unittest.mock import patch

    failure_target = str(tmp_path / "failure_cleanup" / "capture.png")

    def fail_save(self, *args, **kwargs):
        raise OSError("Simulation d'erreur disque lors de l'enregistrement")

    with patch.object(Image.Image, "save", fail_save):
        res_fail = gui_agent.gui_take_screenshot(apply_grid=False, output_path=failure_target)
        assert res_fail.get("status") == "error"

    assert not os.path.exists(failure_target), "Le fichier réservé n'a pas été nettoyé après l'échec"

    res_retry = gui_agent.gui_take_screenshot(apply_grid=False, output_path=failure_target)
    assert res_retry.get("status") == "success"
    assert res_retry.get("screenshot_path") == failure_target
    assert res_retry.get("renamed_due_to_conflict") is False
    assert os.path.isfile(failure_target)


def test_gui_take_screenshot_raw_reservation_failure_cleanup(tmp_path):
    """Teste le rollback de final_path si la réservation de raw_path échoue."""
    import os
    from unittest.mock import patch

    target_file = str(tmp_path / "raw_fail" / "capture.png")
    orig_reserve = gui_agent.server._reserve_unique_file_path
    call_count = 0

    def mock_reserve(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:  # Échec sur la réservation du fichier brut
            raise OSError("Erreur simulée sur la réservation brute")
        return orig_reserve(*args, **kwargs)

    with patch.object(gui_agent.server, "_reserve_unique_file_path", side_effect=mock_reserve):
        res = gui_agent.gui_take_screenshot(apply_grid=False, output_path=target_file)
        assert res.get("status") == "error"

    assert not os.path.exists(target_file), "Le fichier final_path n'a pas été libéré après échec de raw_path"


def test_gui_take_screenshot_foreign_file_substitution_protection(tmp_path):
    """Teste la protection anti-race-condition contre la substitution malveillante de fichier."""
    import os

    subst_target = str(tmp_path / "subst_test" / "capture.png")
    os.makedirs(os.path.dirname(subst_target), exist_ok=True)
    with open(subst_target, "w", encoding="utf-8") as f_foreign:
        f_foreign.write("FOREIGN_FILE_MUST_NOT_BE_TOUCHED")

    foreign_stat = os.stat(subst_target)
    foreign_identity = (foreign_stat.st_dev, foreign_stat.st_ino)

    dummy_fake_identity = (foreign_identity[0], foreign_identity[1] + 999999)
    gui_agent.server._cleanup_reserved_file_safely(subst_target, dummy_fake_identity)
    assert os.path.isfile(subst_target), "Le fichier étranger ne doit pas être supprimé si son inode ne correspond pas"
    with open(subst_target, encoding="utf-8") as f_check:
        assert f_check.read() == "FOREIGN_FILE_MUST_NOT_BE_TOUCHED"


def test_gui_take_screenshot_cleanup_mismatch_no_overwrite_new_target(tmp_path):
    """Teste que la restauration lors d'un mismatch d'inode n'écrase jamais un nouveau fichier créé."""
    import os
    from unittest.mock import patch

    subst_target = str(tmp_path / "subst_overwrite_test" / "capture.png")
    os.makedirs(os.path.dirname(subst_target), exist_ok=True)
    with open(subst_target, "w", encoding="utf-8") as f1:
        f1.write("OLD_SUBSTITUTED_FILE")

    foreign_stat = os.stat(subst_target)
    foreign_identity = (foreign_stat.st_dev, foreign_stat.st_ino)
    dummy_fake_identity = (foreign_identity[0], foreign_identity[1] + 888888)

    orig_open = os.open

    def mock_open_inject_race(path, flags, *args, **kwargs):
        # Dès que le fichier trash est ouvert pour fstat, on simule un processus tiers qui recrée subst_target
        if isinstance(path, str) and ".cleanup_" in path:
            with open(subst_target, "w", encoding="utf-8") as f2:
                f2.write("NEW_CONCURRENT_FOREIGN_TARGET")
        return orig_open(path, flags, *args, **kwargs)

    with patch("os.open", side_effect=mock_open_inject_race):
        gui_agent.server._cleanup_reserved_file_safely(subst_target, dummy_fake_identity)

    # Le nouveau fichier créé ne doit absolument pas avoir été écrasé
    assert os.path.isfile(subst_target)
    with open(subst_target, encoding="utf-8") as f_res:
        assert f_res.read() == "NEW_CONCURRENT_FOREIGN_TARGET"


def test_gui_take_screenshot_include_base64_nominal_and_protection(tmp_path):
    """Teste le retour Base64 nominal et la protection contre la substitution de fichier à la réouverture."""
    import base64

    target_file = str(tmp_path / "base64_test" / "capture.png")
    res = gui_agent.gui_take_screenshot(apply_grid=False, output_path=target_file, include_base64=True)
    assert res.get("status") == "success"
    assert "base64_data" in res
    with open(target_file, "rb") as f:
        expected_b64 = base64.b64encode(f.read()).decode("utf-8")
    assert res["base64_data"] == expected_b64
