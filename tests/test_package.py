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
    assert os.path.isfile("ci.sh"), "ci.sh manquant"
    assert os.access("ci.sh", os.X_OK), "ci.sh non exécutable"
    assert os.path.getsize("install.sh") > 100
    assert os.path.getsize("install.ps1") > 100
    assert os.path.getsize("uninstall.sh") > 100
    assert os.path.getsize("uninstall.ps1") > 100
    assert os.path.getsize("ci.sh") > 100


def test_gui_take_screenshot_output_path(tmp_path):
    import inspect

    sig = inspect.signature(gui_agent.gui_take_screenshot)
    assert "save_to_artifacts" not in sig.parameters, "save_to_artifacts ne doit plus exister dans la signature"
    assert "output_path" in sig.parameters, "output_path doit être présent dans la signature"

    target_file = str(tmp_path / "custom_screenshot.png")
    res = gui_agent.gui_take_screenshot(apply_grid=False, output_path=target_file)
    assert res.get("status") == "success"
    assert res.get("screenshot_path") == target_file
    import os

    assert os.path.exists(target_file)
