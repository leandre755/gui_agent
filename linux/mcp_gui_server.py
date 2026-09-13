import importlib.util
import os
import sys

# Si 'gui_agent' n'est pas encore enregistré dans l'environnement (ex: exécution directe depuis source),
# initialiser le package dynamique pour mapper 'gui_agent' vers le répertoire source courant (linux/)
if "gui_agent" not in sys.modules:
    _pkg_dir = os.path.dirname(os.path.abspath(__file__))
    _pkg_init = os.path.join(_pkg_dir, "__init__.py")
    if os.path.isfile(_pkg_init):
        _spec = importlib.util.spec_from_file_location("gui_agent", _pkg_init, submodule_search_locations=[_pkg_dir])
        if _spec and _spec.loader:
            _pkg = importlib.util.module_from_spec(_spec)
            sys.modules["gui_agent"] = _pkg
            _spec.loader.exec_module(_pkg)

from gui_agent.server import (
    FastMCP,
    SCREENSHOTS_DIR,
    capture_screen_pil,
    check_display_env,
    get_monitor_geometry,
    gui_app_launch,
    gui_click_text,
    gui_clipboard_get,
    gui_clipboard_set,
    gui_find_template,
    gui_find_text,
    gui_get_screen_info,
    gui_keyboard_press,
    gui_keyboard_type,
    gui_mouse_click,
    gui_mouse_drag,
    gui_mouse_move,
    gui_mouse_scroll,
    gui_start_video_recording,
    gui_stop_video_recording,
    gui_take_screenshot,
    gui_web_action,
    gui_window_close,
    gui_window_focus,
    gui_window_list,
    gui_window_resize_move,
    logger,
    main,
    mcp,
    normalize_coordinates,
    press_shortcut_human,
    run_xdotool,
    sleep_human,
    translate_key,
    type_char_human,
)

__all__ = [
    "SCREENSHOTS_DIR",
    "FastMCP",
    "capture_screen_pil",
    "check_display_env",
    "get_monitor_geometry",
    "gui_app_launch",
    "gui_click_text",
    "gui_clipboard_get",
    "gui_clipboard_set",
    "gui_find_template",
    "gui_find_text",
    "gui_get_screen_info",
    "gui_keyboard_press",
    "gui_keyboard_type",
    "gui_mouse_click",
    "gui_mouse_drag",
    "gui_mouse_move",
    "gui_mouse_scroll",
    "gui_start_video_recording",
    "gui_stop_video_recording",
    "gui_take_screenshot",
    "gui_web_action",
    "gui_window_close",
    "gui_window_focus",
    "gui_window_list",
    "gui_window_resize_move",
    "logger",
    "main",
    "mcp",
    "normalize_coordinates",
    "press_shortcut_human",
    "run_xdotool",
    "sleep_human",
    "translate_key",
    "type_char_human",
]

if __name__ == "__main__":
    main()
