"""Couches d'interaction et de médiation système pour gui_agent."""

from . import accessibility, input_emulation, visual_perception, window_management
from .accessibility import get_app_state, perform_action, set_value
from .input_emulation import key_tap, mouse_click_at, mouse_drag_smooth, mouse_scroll, screen_capture
from .visual_perception import find_text
from .window_management import activate_window, process_list, process_run

__all__ = [
    "accessibility",
    "activate_window",
    "find_text",
    "get_app_state",
    "input_emulation",
    "key_tap",
    "mouse_click_at",
    "mouse_drag_smooth",
    "mouse_scroll",
    "perform_action",
    "process_list",
    "process_run",
    "screen_capture",
    "set_value",
    "visual_perception",
    "window_management",
]
