<p align="center">
  <img src="https://files.catbox.moe/udf9j4.jpeg" alt="gui-agent Hero Banner" width="100%" style="border-radius: 8px;" />
</p>

<h1 align="center"><img src="https://files.catbox.moe/xei715.png" alt="gui-agent Logo" width="114" style="vertical-align: middle; margin-right: 12px;" /> gui-agent</h1>

<p align="center"><b>Monolithic FastMCP Server for Linux & Windows Desktop Computer Use</b></p>

<p align="center">🌐 <b><a href="README.md">English</a></b> | <b><a href="README.fr.md">Français</a></b></p>

<p align="center">
  <a href="#-core-capabilities"><img src="https://img.shields.io/badge/Capabilities-→-10B981?style=flat-square" alt="Capabilities" /></a>
  <a href="#-how-it-works"><img src="https://img.shields.io/badge/Architecture-→-10B981?style=flat-square" alt="Architecture" /></a>
  <a href="#-installation"><img src="https://img.shields.io/badge/Installation-→-10B981?style=flat-square" alt="Installation" /></a>
  <a href="#-mcp-client-configuration"><img src="https://img.shields.io/badge/MCP_Clients-→-10B981?style=flat-square" alt="MCP Clients" /></a>
  <a href="#-toolset--cli-reference"><img src="https://img.shields.io/badge/Toolset-→-10B981?style=flat-square" alt="Toolset" /></a>
  <a href="#-clean-uninstallation"><img src="https://img.shields.io/badge/Uninstall-→-10B981?style=flat-square" alt="Uninstall" /></a>
  <a href="#-development--zero-slop-quality"><img src="https://img.shields.io/badge/Development-→-10B981?style=flat-square" alt="Development" /></a>
</p>

<p align="center">
  <a href="https://github.com/leandre755/gui_agent/releases/tag/v0.1.0"><img src="https://img.shields.io/badge/version-0.1.0-3FB950?style=flat-square" alt="Version 0.1.0" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-34D399?style=flat-square" alt="Python 3.10+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-F0883E?style=flat-square" alt="License MIT" /></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows-10B981?style=flat-square" alt="Platform Linux | Windows" /></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP_Protocol-1.2.0+-10B981?style=flat-square" alt="MCP Protocol 1.2.0+" /></a>
</p>

### Why gui-agent?

Desktop automation for AI agents usually requires running multiple disjointed utilities for screen capture, input simulation, window management, and OCR. Spawning separate processes increases latency, consumes hundreds of megabytes of RAM, and fails when windows or display servers change state.

**gui-agent** packs these capabilities into a single FastMCP server communicating over stdio. It provides 21 tools for Linux (X11/XWayland) and Windows in a single process that uses under 50 MB RAM, requiring no heavy browser runtimes for core desktop operations (unless `gui_web_action` is explicitly called) or cloud vision APIs.

The server captures frames directly from the display server, renders a Cartesian pixel grid over screenshots to prevent spatial errors in vision models, and dispatches native input events through OS system calls and utilities (`xdotool`, Win32 API). It includes OpenCV template matching and local OCR fallbacks for reliable element targeting.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Bullseye.png" alt="Bullseye" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Core Capabilities

The server exposes 21 FastMCP tools for OS-level Computer Use. All tools communicate over a single JSON-RPC 2.0 stdio channel.

| Tool Name | Domain | Description | Status |
| :--- | :--- | :--- | :--- |
| `gui_get_screen_info` | <img src="https://img.shields.io/badge/Screen-10B981?style=flat-square" alt="Screen" /> | Returns display resolution, connected monitors, screen coordinates, and failsafe state. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_take_screenshot` | <img src="https://img.shields.io/badge/Screen-10B981?style=flat-square" alt="Screen" /> | Captures full or cropped desktop displays with optional Cartesian coordinate grid overlays. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_move` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Moves the mouse cursor to absolute `(x, y)` or normalized `[0, 1000]` coordinates. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_click` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Sends single, double, or triple mouse clicks (`left`, `right`, `middle`) at target coordinates. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_drag` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Drags the cursor from `(x1, y1)` to `(x2, y2)` with configurable duration. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_scroll` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Scrolls the mouse wheel along horizontal or vertical axes (`up`, `down`, `left`, `right`). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_keyboard_type` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Types text strings with configurable inter-key delays. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_keyboard_press` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Sends key combinations and special keys (`ctrl+c`, `super`, `alt+tab`, `Return`). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_clipboard_get` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Reads clipboard text with multi-backend fallback (`pyperclip`, `xclip`, `xsel`). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_clipboard_set` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Writes text to the system clipboard across available backends. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_list` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Lists open desktop windows with window IDs, process PIDs, titles, and WM classes. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_focus` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Raises and focuses a target window by ID. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_resize_move` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Moves and resizes a target window to specified coordinates and dimensions. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_close` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Closes a target window via standard window manager protocols. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_app_launch` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Launches a process asynchronously in the background or synchronously. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_find_template` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Locates template sub-images on screen using OpenCV template matching. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_find_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Finds text coordinates on screen via OCR (Tesseract / RapidOCR). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_click_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Finds matching text on screen via OCR and clicks its center coordinate. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_web_action` | <img src="https://img.shields.io/badge/Web-34D399?style=flat-square" alt="Web" /> | Runs Playwright browser actions (`aria_tree`, `click`, `type`, `screenshot`). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_start_video_recording` | <img src="https://img.shields.io/badge/Media-F0883E?style=flat-square" alt="Media" /> | Records desktop screen video in the background via FFmpeg (`x11grab` / H.264). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_stop_video_recording` | <img src="https://img.shields.io/badge/Media-F0883E?style=flat-square" alt="Media" /> | Stops the active FFmpeg recording and finalizes the MP4 file container. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="Gear" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> How It Works

**gui-agent** bridges MCP clients (Claude Code, Antigravity CLI, Cursor) and the operating system desktop. It executes input events, captures display buffers, and inspects application windows through local system interfaces.

<p align="center">
  <img src="https://gist.githubusercontent.com/lender926-lab/050b95747c45950573c28906fcb1fae6/raw/exc-how-it-works-en.svg" alt="gui-agent Architecture Workflow" width="100%" style="border-radius: 10px;" />
</p>

### Technical Execution Pipeline

1. **Screen Capture & Coordinate Grid**: When an agent calls `gui_take_screenshot`, the server grabs the framebuffer via MSS, falling back to Spectacle or Scrot if XWayland returns an empty buffer. It draws a configurable pixel grid (default 100px) with high-contrast coordinate labels so vision models can read exact pixel locations.
2. **FastMCP stdio Interface**: The server communicates over stdio using JSON-RPC 2.0. Tool signatures are validated through Pydantic models at runtime without exposing network ports or running background daemons.
3. **Coordinate Normalization**: Tools accept either absolute pixel coordinates `(x, y)` or normalized `[0, 1000]` ranges. The normalization helper maps these values across multi-monitor layouts, applying screen bounds clamping and DPI offsets.
4. **Native Input & Window Dispatch**: Mouse and keyboard events are sent directly to the display server (`xdotool`/`Xlib` on Linux, Win32 `SendInput` on Windows) with configurable inter-key delays. Window inspection queries the window manager via `wmctrl` and `xprop`.
5. **Local Vision, OCR & Playwright**: OpenCV template matching locates UI icons by image reference. Text recognition uses Tesseract with RapidOCR ONNX fallback. For web targets, Playwright provides direct DOM tree inspection and interaction.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="Package" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Installation

> For operating system guides, troubleshooting, and offline setups, see [**INSTALL.md**](INSTALL.md).

### 1. Automated Installation (Recommended)

#### Linux (Bash)
Run the install script to verify dependencies, install `uv`, create an isolated environment, and register the MCP server:

```bash
# Single-line curl installer
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/install.sh | bash

# Or locally from a cloned repository
./install.sh
```

#### Microsoft Windows (PowerShell)
Run the PowerShell installer (standard user or administrator):

```powershell
# Single-line PowerShell installer
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/install.ps1 | iex"

# Or locally from a cloned repository
.\install.ps1 -Local
```

### 2. Isolated Deployment via uv tool

Install `gui-agent` in an isolated virtual environment with global CLI entrypoints:

```bash
# Install from PyPI
uv tool install gui-agent

# Or install from GitHub repository
uv tool install "git+https://github.com/leandre755/gui_agent.git"

# Upgrade to latest release
uv tool upgrade gui-agent
```

### 3. Linux System Prerequisites

Install system packages for window control, screen capture, OCR, and clipboard operations:

```bash
# Debian / Ubuntu / Linux Mint
sudo apt-get update && sudo apt-get install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract-ocr libgl1

# Fedora / RHEL
sudo dnf install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract libglvnd-glx

# Arch Linux / Manjaro
sudo pacman -S --needed \
  xdotool wmctrl spectacle ffmpeg xclip tesseract
```

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Electric%20Plug.png" alt="Plug" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> MCP Client Configuration

### 1. Claude Code CLI

Register the server with Claude Code CLI in a single command:

```bash
# If installed via uv tool
claude mcp add gui-agent -- gui-agent

# Direct on-the-fly execution via uvx (zero pre-installation)
claude mcp add gui-agent -- uvx --from gui-agent gui-agent
```

### 2. Antigravity CLI

Add the server definition to your Antigravity global MCP configuration:

- **Linux / macOS**: `~/.gemini/config/mcp_config.json`
- **Windows**: `%USERPROFILE%\.gemini\config\mcp_config.json`

```json
{
  "mcpServers": {
    "gui-agent": {
      "command": "gui-agent",
      "args": [],
      "env": {
        "DISPLAY": ":0"
      }
    }
  }
}
```

*(Note: The alias binary `mcp-gui-server` can also be used as the `command` target).*

### 3. Cursor & VSCode

Add the following entry to your Cursor `mcp.json` (`~/.cursor/mcp.json` or `.vscode/mcp.json`):

```json
{
  "mcpServers": {
    "gui-agent": {
      "command": "uvx",
      "args": ["--from", "gui-agent", "gui-agent"]
    }
  }
}
```

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Hammer%20and%20Wrench.png" alt="Tools" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Toolset & CLI Reference

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Computer%20Mouse.png" alt="Mouse" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Display & Cursor Tools (10 tools)</b></summary>

#### `gui_get_screen_info`
Returns screen dimensions, connected monitors, display coordinates, and failsafe state.
- **Parameters**: None.
- **Returns**: `dict` containing `resolution`, `width`, `height`, `monitors` list, `display_env`, and `failsafe_enabled`.

#### `gui_take_screenshot`
Captures full-screen or cropped screenshots with an optional Cartesian coordinate grid overlay.
- **Parameters**:
  - `monitor_index` (`int`, default `1`): Target monitor index (`0` for virtual canvas).
  - `crop_box` (`list[int] | None`, default `None`): Sub-region `[x, y, width, height]`.
  - `apply_grid` (`bool`, default `True`): Overlays the Cartesian coordinate grid.
  - `grid_interval` (`int`, default `100`): Interval in pixels between grid lines (minimum 20).
  - `format` (`str`, default `"png"`): Output image format (`"png"` or `"jpeg"`).
  - `quality` (`int`, default `80`): Compression quality (1-100) for JPEG output.
  - `output_path` (`str | None`, default `None`): Destination file path. Relative paths are resolved to absolute paths and missing parent directories are created. Empty paths and existing directories are rejected. If the path lacks an extension, the extension corresponding to `format` is automatically appended. Incompatible extensions are rejected. If the target file already exists, atomic reservation with incremental suffixes such as `(1)` and `(2)` protects existing files from overwrite. `screenshot_path` returns the actual resolved absolute path used. If omitted, defaults to a timestamped image in the screenshots directory.
  - `include_base64` (`bool`, default `False`): Returns Base64-encoded string representation.
- **Returns**: `dict` containing `screenshot_path` (resolved absolute path), `raw_screenshot_path`, `resolution`, `grid_applied`, and `renamed_due_to_conflict`.

#### `gui_mouse_move`
Moves the mouse cursor to target coordinates.
- **Parameters**:
  - `x` (`float`): Target X position.
  - `y` (`float`): Target Y position.
  - `duration` (`float`, default `0.2`): Movement interpolation duration in seconds.
  - `normalized` (`bool`, default `False`): Set to `True` when using `[0, 1000]` coordinates.
  - `monitor_index` (`int`, default `1`): Reference monitor for coordinate calculations.

#### `gui_mouse_click`
Performs mouse clicks at target coordinates.
- **Parameters**:
  - `x` (`float`): Target X position.
  - `y` (`float`): Target Y position.
  - `button` (`str`, default `"left"`): Mouse button (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, default `1`): Number of clicks to perform.
  - `normalized` (`bool`, default `False`): Set to `True` for `[0, 1000]` coordinates.
  - `monitor_index` (`int`, default `1`): Reference monitor.

#### `gui_mouse_drag`
Performs a drag-and-drop mouse operation between two points.
- **Parameters**:
  - `x1` (`float`): Starting X position.
  - `y1` (`float`): Starting Y position.
  - `x2` (`float`): Ending X position.
  - `y2` (`float`): Ending Y position.
  - `duration` (`float`, default `0.5`): Drag animation duration in seconds.
  - `normalized` (`bool`, default `False`): Set to `True` for `[0, 1000]` coordinates.
  - `monitor_index` (`int`, default `1`): Reference monitor.

#### `gui_mouse_scroll`
Scrolls the mouse wheel along horizontal or vertical axes.
- **Parameters**:
  - `clicks` (`int`): Number of scroll ticks (positive integer).
  - `direction` (`str`, default `"down"`): Direction (`"up"`, `"down"`, `"left"`, `"right"`).

#### `gui_keyboard_type`
Types text sequentially with configurable delays between keystrokes.
- **Parameters**:
  - `text` (`str`): String content to type.
  - `delay` (`float`, default `0.06`): Base delay between keystrokes in seconds.

#### `gui_keyboard_press`
Sends individual key presses or hotkey combinations.
- **Parameters**:
  - `key` (`str`): Key identifier or chord (e.g., `"Return"`, `"Escape"`, `"ctrl+c"`, `"alt+tab"`, `"super"`).

#### `gui_clipboard_get`
Reads text content from the system clipboard.
- **Parameters**: None.
- **Returns**: `dict` containing clipboard `text`, character `length`, and retrieval `method`.

#### `gui_clipboard_set`
Writes text content into the system clipboard.
- **Parameters**:
  - `text` (`str`): Text content to store in the clipboard.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Window.png" alt="Window" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Window & Process Control (5 tools)</b></summary>

#### `gui_window_list`
Lists open desktop windows with window ID, title, PID, and window class.
- **Parameters**: None.
- **Returns**: `dict` with `windows` array containing window `id`, `title`, `pid`, and `wm_class`.

#### `gui_window_focus`
Brings a target window to the foreground by ID.
- **Parameters**:
  - `window_id` (`int`): Numeric window ID obtained from `gui_window_list`.

#### `gui_window_resize_move`
Moves and resizes a target window to specified coordinates and dimensions.
- **Parameters**:
  - `window_id` (`int`): Target numeric window ID.
  - `x` (`int`): New top-left X coordinate.
  - `y` (`int`): New top-left Y coordinate.
  - `width` (`int`): New window width in pixels.
  - `height` (`int`): New window height in pixels.

#### `gui_window_close`
Closes a target application window via standard window manager protocols.
- **Parameters**:
  - `window_id` (`int`): Target numeric window ID.

#### `gui_app_launch`
Launches an operating system command or executable.
- **Parameters**:
  - `command` (`str`): Shell command line or binary path to launch.
  - `background` (`bool`, default `True`): Run asynchronously detached (`True`) or wait synchronously (`False`).

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magnifying%20Glass%20Tilted%20Left.png" alt="Search" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Vision & OCR Automation (3 tools)</b></summary>

#### `gui_find_template`
Locates an image template on screen using OpenCV template matching.
- **Parameters**:
  - `template_path` (`str`): File path to the reference template image.
  - `threshold` (`float`, default `0.8`): Confidence threshold (between 0.01 and 1.0).
  - `monitor_index` (`int`, default `1`): Monitor index to inspect.
- **Returns**: `dict` containing match center coordinates `(x, y)` and matching `confidence`.

#### `gui_find_text`
Locates text on screen via OCR (Tesseract / RapidOCR) and returns bounding box coordinates.
- **Parameters**:
  - `text` (`str`): Target string to discover.
  - `confidence` (`float`, default `0.6`): Minimum OCR confidence score (0.0 to 1.0).
  - `monitor_index` (`int`, default `1`): Monitor index to search.
- **Returns**: `dict` containing `text_found`, centroid `(x, y)`, `confidence`, and bounding box `[x, y, w, h]`.

#### `gui_click_text`
Searches for text on screen via OCR and clicks the center of the matching region.
- **Parameters**:
  - `text` (`str`): Target text string to locate and click.
  - `button` (`str`, default `"left"`): Mouse button to click (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, default `1`): Number of clicks to perform.
  - `monitor_index` (`int`, default `1`): Target monitor.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Movie%20Camera.png" alt="Camera" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Web & Multimedia Recording (3 tools)</b></summary>

#### `gui_web_action`
Automates web pages in headless Chromium via Playwright.
- **Parameters**:
  - `url` (`str`): Web address or local file URL to navigate to.
  - `action` (`str`, default `"aria_tree"`): Action to perform (`"aria_tree"`, `"click"`, `"type"`, `"screenshot"`).
  - `selector` (`str | None`, default `None`): CSS or XPath selector for `click` and `type` actions.
  - `text` (`str | None`, default `None`): Text payload to input when `action="type"`.
  - `viewport_width` (`int`, default `1280`): Browser viewport width.
  - `viewport_height` (`int`, default `720`): Browser viewport height.
  - `timeout_ms` (`int`, default `30000`): Navigation and locator timeout in milliseconds.

#### `gui_start_video_recording`
Starts background screen recording via FFmpeg (`x11grab` / H.264).
- **Parameters**:
  - `output_path` (`str | None`, default `None`): Destination file path (defaults to timestamped MP4 in screenshots dir).
  - `fps` (`int`, default `5`): Video capture frame rate (1 to 30 FPS).
  - `monitor_index` (`int`, default `1`): Target monitor index.
  - `duration` (`int | None`, default `None`): Optional automatic duration limit in seconds.

#### `gui_stop_video_recording`
Stops the active FFmpeg recording and checks the output MP4 file.
- **Parameters**: None.
- **Returns**: `dict` containing `output_path`, `file_exists`, and `file_size_bytes`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Control%20Knobs.png" alt="Config" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Environment Variables (Configuration)</b></summary>

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `DISPLAY` | Target X11 display server identifier. | `:0` |
| `GUI_AGENT_SCREENSHOTS_DIR` | Directory where screenshots, crops, and screen recordings are saved. | `~/.local/share/gui-agent/screenshots` |

</details>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Wastebasket.png" alt="Trash" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Clean Uninstallation

To remove `gui-agent`, delete isolated environments, and clean registered MCP configurations:

### 1. Linux & macOS (Bash)

```bash
# Automated remote uninstaller
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/uninstall.sh | bash

# Local uninstall with full data and screenshot purge
./uninstall.sh --purge-data --yes
```

### 2. Microsoft Windows (PowerShell)

```powershell
# Automated remote uninstaller
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/uninstall.ps1 | iex"

# Local uninstall with full data and screenshot purge
.\uninstall.ps1 -PurgeData -Yes
```

#### What the uninstaller cleans:
- Removes `gui-agent` and `mcp-gui-server` binaries from `~/.local/bin` (or `%USERPROFILE%\.local\bin`).
- Unregisters the MCP server from Claude Code CLI configuration.
- Cleans JSON entries from Antigravity `mcp_config.json`.
- Purges temporary directories and optionally deletes the screenshot repository (`--purge-data` / `-PurgeData`).

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Shield.png" alt="Shield" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Development & Zero-Slop Quality

Development is gated by an 8-layer pre-commit hook pipeline and test coverage.

### 1. Local Environment Setup

```bash
# Clone the repository
git clone https://github.com/leandre755/gui_agent.git
cd gui_agent

# Initialize virtual environment with Astral UV
uv venv
source .venv/bin/activate

# Install editable package with development dependencies
uv pip install -e ".[dev]"
```

### 2. Running Test Suites

```bash
# Run unit and integration tests
pytest -v tests/
```

### 3. Zero-Slop 8-Layer Pre-Commit Verification

Every commit passes through 8 static validation layers before merge:

```bash
# Run the 8-layer Zero-Slop validation hook locally
ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit
```

| Layer | Validator | Scope & Quality Invariants Enforced |
| :--- | :--- | :--- |
| 1 | `anti-leak` | Blocks secret tokens, private keys, and `.env` variables from staged files. |
| 2 | `pip-audit` | Audits installed dependencies against CVE vulnerability databases. |
| 3 | `ruff check` | Enforces lint rules, PEP 8 standards, and Python 3.10+ syntax. |
| 4 | `ruff format` | Checks uniform code formatting across all Python sources. |
| 5 | `mypy` | Runs static type checking across the entire codebase. |
| 6 | `sonar/smells` | Checks cognitive complexity (McCabe C90 <= 25), bugs, and code smells. |
| 7 | `bandit` | Analyzes AST for security issues (unsafe subprocess calls, shell patterns). |
| 8 | `semgrep` | SAST scanner detecting security vulnerabilities and dangerous patterns. |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Scroll.png" alt="Scroll" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> License

This project is licensed under the terms of the [MIT License](LICENSE).

Copyright (c) 2026 Leandre. All rights reserved.
