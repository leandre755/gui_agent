# Execution Plan: Qualification & Testing of MCP GUI Agent Tools

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: All 21 MCP GUI tools exported by `mcp_gui_server.py` must execute gracefully, handle invalid inputs cleanly, return accurate structured data/feedback, and prevent process crashes.
- **Pre-requisites**: Active X11/XWayland session (`DISPLAY=:0`), running `gui-agent` MCP server connected to Claude Code CLI.

## 🛠️ Step-by-Step Sequence

### Step 1: Informational & Screen System Tools Validation
- [x] **Action**: Call `mcp__gui-agent__gui_get_screen_info` and `mcp__gui-agent__gui_take_screenshot`.
- [x] **Verify**: Confirm returned screen resolution, monitors list, and valid screenshot image/path without errors.
- **Verification Proof**:
```text
gui_get_screen_info: SUCCESS (resolution 1366x768)
gui_take_screenshot: SUCCESS (file saved, but base64 payload causes context token overflow DEF-01)
```

### Step 2: Window Management Tools Validation
- [x] **Action**: Call `mcp__gui-agent__gui_window_list`, `mcp__gui-agent__gui_window_focus`, `mcp__gui-agent__gui_window_resize_move`, `mcp__gui-agent__gui_window_close`.
- [x] **Verify**: Confirm window listing details, error handling for non-existent window IDs, and successful window control operations.
- **Verification Proof**:
```text
gui_window_list: SUCCESS (2 windows listed)
gui_window_focus: SUCCESS (focused 6291470; invalid ID handled properly)
gui_window_resize_move: SUCCESS (resized & moved to 100,100 800x500)
gui_window_close: PARTIAL (handles bad window IDs via X error, PID vs WID confusion)
```

### Step 3: Mouse & Cursor Simulation Tools Validation
- [x] **Action**: Call `mcp__gui-agent__gui_mouse_move`, `mcp__gui-agent__gui_mouse_click`, `mcp__gui-agent__gui_mouse_drag`, `mcp__gui-agent__gui_mouse_scroll`.
- [x] **Verify**: Confirm fluid mouse movement, click handling, drag operations, and scroll actions.
- **Verification Proof**:
```text
gui_mouse_move: DEFECT (pixel coords work, normalized [0.0, 1.0] maps to (1,0) DEF-02)
gui_mouse_click: SUCCESS (left click at 400,400)
gui_mouse_drag: SUCCESS (dragged from 200,200 to 500,500)
gui_mouse_scroll: SUCCESS (scrolled 3 steps down)
```

### Step 4: Keyboard Simulation & Clipboard Tools Validation
- [x] **Action**: Call `mcp__gui-agent__gui_keyboard_type`, `mcp__gui-agent__gui_keyboard_press`, `mcp__gui-agent__gui_clipboard_set`, `mcp__gui-agent__gui_clipboard_get`.
- [x] **Verify**: Confirm keystrokes typed cleanly, key combos executed, clipboard read/write accuracy.
- **Verification Proof**:
```text
gui_clipboard_set: SUCCESS (set text in clipboard)
gui_clipboard_get: SUCCESS (retrieved text 'Test MCP GUI Clipboard 123')
gui_keyboard_type: SUCCESS (typed 'test')
gui_keyboard_press: DEFECT (invalid key names report success DEF-03)
```

### Step 5: OCR, Computer Vision & Template Matching Tools Validation
- [x] **Action**: Call `mcp__gui-agent__gui_find_text`, `mcp__gui-agent__gui_click_text`, `mcp__gui-agent__gui_find_template`.
- [x] **Verify**: Confirm text detection, OCR click behavior, template matching fallback/error handling.
- **Verification Proof**:
```text
gui_find_text: SUCCESS (found 'Claude' at 489, 86 with confidence 0.95)
gui_click_text: SUCCESS (clicked on 'Claude' at center 489, 86)
gui_find_template: SUCCESS (handled missing template cleanly)
```

### Step 6: Application Launch, Video Recording & Playwright Web Action Validation
- [x] **Action**: Call `mcp__gui-agent__gui_app_launch`, `mcp__gui-agent__gui_start_video_recording`, `mcp__gui-agent__gui_stop_video_recording`, `mcp__gui-agent__gui_web_action`.
- [x] **Verify**: Confirm X11 app launch, video recording start/stop without file descriptor leaks, Playwright headless action execution.
- **Verification Proof**:
```text
gui_app_launch: SUCCESS (launched PID 642024)
gui_start_video_recording: SUCCESS (started ffmpeg PID 642892)
gui_stop_video_recording: SUCCESS (stopped ffmpeg, file size 119,772 bytes)
gui_web_action: DEFECT (Playwright sync API crashes in FastMCP asyncio loop DEF-04)
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Video recording or xdotool/spectacle commands failing due to missing system binaries or non-zero exit codes.
- **Mitigation**: Catch exceptions gracefully in tool logic and log detailed error messages in test report.
