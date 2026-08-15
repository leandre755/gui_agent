"""Tests unitaires pour le package gui-agent."""

import gui_agent
import mcp_gui_server
from gui_agent.server import normalize_coordinates, translate_key


def test_package_metadata():
    assert gui_agent.__version__ == "0.1.0"
    assert len(gui_agent.__all__) > 20


def test_fastmcp_tools_registration():
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
    assert hasattr(mcp_gui_server, "gui_get_screen_info")
    assert hasattr(mcp_gui_server, "gui_take_screenshot")
    assert hasattr(mcp_gui_server, "normalize_coordinates")
    assert mcp_gui_server.mcp is gui_agent.mcp


def test_normalize_coordinates():
    # Coordonnées réelles (normalized=False)
    x, y = normalize_coordinates(500, 300, normalized=False)
    assert x == 500
    assert y == 300


def test_translate_key():
    assert translate_key("ctrl") == "control"
    assert translate_key("alt") == "alt"
    assert translate_key("super") == "Super_L"
    assert translate_key("enter") == "Return"
    assert translate_key("escape") == "Escape"


def test_installation_and_uninstallation_scripts_presence():
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
    import inspect
    import os
    from PIL import Image

    sig = inspect.signature(gui_agent.gui_take_screenshot)
    assert "save_to_artifacts" not in sig.parameters, "save_to_artifacts ne doit plus exister dans la signature"
    assert "output_path" in sig.parameters, "output_path doit être présent dans la signature"

    # 1. Cas nominal : capture PNG avec output_path valide
    target_file = str(tmp_path / "nested" / "custom_screenshot.png")
    res = gui_agent.gui_take_screenshot(apply_grid=True, format="png", output_path=target_file)
    assert res.get("status") == "success"
    assert res.get("screenshot_path") == target_file
    assert os.path.isfile(target_file)
    assert os.path.isfile(res["raw_screenshot_path"])
    with Image.open(target_file) as img:
        assert img.format == "PNG"

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
