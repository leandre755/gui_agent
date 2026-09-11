"""SDK Python unifié mcp_core injecté dans le namespace d'exécution locale CodeAct (REPL)."""

from __future__ import annotations

from gui_agent.layers import (
    activate_window,
    find_text,
    get_app_state,
    key_tap,
    mouse_click_at,
    mouse_drag_smooth,
    mouse_scroll,
    perform_action,
    process_list,
    process_run,
    screen_capture,
    set_value,
)


class MCPCoreSDK:
    """Interface unifiée exposant l'ensemble des primitives système pour l'environnement REPL."""

    # Médiation d'accessibilité programmatique
    get_app_state = staticmethod(get_app_state)
    perform_action = staticmethod(perform_action)
    set_value = staticmethod(set_value)

    # Perception visuelle & OCR
    find_text = staticmethod(find_text)

    # Émulation d'entrées bas-niveau
    screen_capture = staticmethod(screen_capture)
    mouse_click_at = staticmethod(mouse_click_at)
    mouse_drag_smooth = staticmethod(mouse_drag_smooth)
    mouse_scroll = staticmethod(mouse_scroll)
    key_tap = staticmethod(key_tap)

    # Gestion de fenêtrage et processus
    process_run = staticmethod(process_run)
    process_list = staticmethod(process_list)
    activate_window = staticmethod(activate_window)


# Instance globale importable directement
mcp_core = MCPCoreSDK()

# Export de niveau module pour syntaxe directe : mcp_core.find_text(...)
__all__ = [
    "MCPCoreSDK",
    "activate_window",
    "find_text",
    "get_app_state",
    "key_tap",
    "mcp_core",
    "mouse_click_at",
    "mouse_drag_smooth",
    "mouse_scroll",
    "perform_action",
    "process_list",
    "process_run",
    "screen_capture",
    "set_value",
]
