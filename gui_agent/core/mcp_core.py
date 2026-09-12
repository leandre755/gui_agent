"""SDK Python unifié mcp_core injecté dans l'espace REPL."""

from __future__ import annotations

from gui_agent import layers


class MCPCoreSDK:
    """Interface unifiée exposant l'ensemble des primitives système."""

    activate_window = staticmethod(layers.activate_window)
    find_text = staticmethod(layers.find_text)
    get_app_state = staticmethod(layers.get_app_state)
    key_tap = staticmethod(layers.key_tap)
    mouse_click_at = staticmethod(layers.mouse_click_at)
    mouse_drag_smooth = staticmethod(layers.mouse_drag_smooth)
    mouse_scroll = staticmethod(layers.mouse_scroll)
    perform_action = staticmethod(layers.perform_action)
    process_list = staticmethod(layers.process_list)
    process_run = staticmethod(layers.process_run)
    screen_capture = staticmethod(layers.screen_capture)
    set_value = staticmethod(layers.set_value)

    @property
    def mcp_core(self) -> MCPCoreSDK:
        return self


mcp_core = MCPCoreSDK()
__all__ = ["MCPCoreSDK", "mcp_core"]
