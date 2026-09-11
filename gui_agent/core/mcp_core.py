"""SDK Python unifié mcp_core injecté dans l'espace REPL."""

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
    """Interface unifiée exposant l'ensemble des primitives système."""

    get_app_state, perform_action, set_value = (
        staticmethod(get_app_state),
        staticmethod(perform_action),
        staticmethod(set_value),
    )
    find_text, screen_capture = staticmethod(find_text), staticmethod(screen_capture)
    mouse_click_at, mouse_drag_smooth = staticmethod(mouse_click_at), staticmethod(mouse_drag_smooth)
    mouse_scroll, key_tap = staticmethod(mouse_scroll), staticmethod(key_tap)
    process_run, process_list, activate_window = (
        staticmethod(process_run),
        staticmethod(process_list),
        staticmethod(activate_window),
    )


mcp_core = MCPCoreSDK()
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
