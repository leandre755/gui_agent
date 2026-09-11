"""Couches d'interaction et de médiation système pour gui_agent.

Architecture modulaire :
- accessibility : Médiation d'accessibilité programmatique (AT-SPI / D-Bus)
- visual_perception : Perception visuelle et reconnaissance optique de caractères (OCR)
- input_emulation : Émulation d'entrées bas-niveau et injection d'événements noyau (uinput / evdev)
- window_management : Gestion de fenêtrage et contrôle de processus
"""

from gui_agent.layers.accessibility import get_app_state, perform_action, set_value
from gui_agent.layers.input_emulation import (
    key_tap,
    mouse_click_at,
    mouse_drag_smooth,
    mouse_scroll,
    screen_capture,
)
from gui_agent.layers.visual_perception import find_text
from gui_agent.layers.window_management import activate_window, process_list, process_run

__all__ = [
    "activate_window",
    "find_text",
    "get_app_state",
    "key_tap",
    "mouse_click_at",
    "mouse_drag_smooth",
    "mouse_scroll",
    "perform_action",
    "process_list",
    "process_run",
    "screen_capture",
    "set_value",
]
