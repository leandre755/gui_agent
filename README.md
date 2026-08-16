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

### The Philosophy: Why gui-agent?

Autonomous AI agents interacting with modern graphical user interfaces are frequently burdened by fragmented architectures, fragile micro-servers, and exorbitant memory footprints. Traditional automation setups force models to juggle disparate processes for screen capture, input emulation, window management, and optical character recognition. This fragmentation introduces latency, high failure rates on dynamic desktop environments, and excessive resource consumption that quickly overwhelms memory-constrained workstations.

**gui-agent** resolves this architectural friction by providing a unified, monolithic FastMCP server engineered specifically for direct, low-latency Computer Use on Linux (X11/XWayland) and Windows desktop environments. Consolidating twenty-one high-performance tools into a single resilient stdio connection, **gui-agent** operates with a minimal memory footprint below 50 MB RAM, enabling seamless execution on dual-core CPUs and virtualized environments without requiring external browser runtimes for desktop tools (browser automation is strictly localized to `gui_web_action`) or external cloud vision dependencies.

Under the hood, **gui-agent** couples millisecond-level screen acquisition with an intelligent Cartesian coordinate grid overlay, allowing large language models to accurately locate visual targets without spatial hallucinations. By combining native OS input dispatchers, window hierarchy introspection, OpenCV template matching, and local OCR parsing with automated fallback pipelines, the system guarantees deterministic execution, zero-leak process lifecycle management, and pixel-precise control across complex desktop workflows.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Bullseye.png" alt="Bullseye" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Core Capabilities

The server exposes 21 monolithic FastMCP tools covering the complete lifecycle of operating system Computer Use. All tools operate through a single standard input/output (stdio) JSON-RPC 2.0 communication channel.

| Tool Name | Domain | Description | Status |
| :--- | :--- | :--- | :--- |
| `gui_get_screen_info` | <img src="https://img.shields.io/badge/Screen-10B981?style=flat-square" alt="Screen" /> | Retrieves screen resolution, detected monitors, display coordinates, and failsafe state. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_take_screenshot` | <img src="https://img.shields.io/badge/Screen-10B981?style=flat-square" alt="Screen" /> | Captures full or cropped desktop displays with dynamic Cartesian coordinate grid overlays. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_move` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Smoothly displaces the mouse cursor to absolute `(x, y)` or normalized `[0, 1000]` coordinates. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_click` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Dispatches single, double, or triple mouse clicks (`left`, `right`, `middle`) at target coordinates. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_drag` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Performs smooth mouse drag-and-drop operations from `(x1, y1)` to `(x2, y2)` with configurable duration. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_mouse_scroll` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Simulates directional scroll wheel actions (`up`, `down`, `left`, `right`) with adjustable step count. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_keyboard_type` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Types text strings character-by-character with realistic micro-jitter delays to prevent anti-bot blocks. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_keyboard_press` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Sends specialized keycodes and complex hotkey chords (`ctrl+c`, `super`, `alt+tab`, `Return`). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_clipboard_get` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Reads text from the OS clipboard with automated multi-backend fallback (`pyperclip`, `xclip`, `xsel`). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_clipboard_set` | <img src="https://img.shields.io/badge/Input-10B981?style=flat-square" alt="Input" /> | Writes arbitrary text into the system clipboard with multi-backend synchronization. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_list` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Inspects active window hierarchy, returning window IDs, process PIDs, titles, and WM classes. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_focus` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Activates and raises a target application window to the desktop foreground by ID. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_resize_move` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Relocates and resizes a target window with pixel-exact coordinate and dimension parameters. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_window_close` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Gracefully terminates an open application window via native window manager protocols. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_app_launch` | <img src="https://img.shields.io/badge/Window-10B981?style=flat-square" alt="Window" /> | Spawns system applications either as asynchronous background processes or synchronous commands. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_find_template` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Searches for visual sub-images across the screen using OpenCV normalized cross-correlation matching. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_find_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Identifies and locates on-screen text coordinates via OCR engines (Tesseract / RapidOCR). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_click_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Performs an end-to-end OCR search and immediately clicks the center of the matching text bounding box. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_web_action` | <img src="https://img.shields.io/badge/Web-34D399?style=flat-square" alt="Web" /> | Executes deterministic browser interactions (`aria_tree`, `click`, `type`, `screenshot`) via Playwright. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_start_video_recording` | <img src="https://img.shields.io/badge/Media-F0883E?style=flat-square" alt="Media" /> | Starts background low-overhead screen video recording via FFmpeg (`x11grab` / H.264 ultrafast). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_stop_video_recording` | <img src="https://img.shields.io/badge/Media-F0883E?style=flat-square" alt="Media" /> | Cleanly halts the active FFmpeg recording, flushes the MP4 container, and prevents descriptor leaks. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="Gear" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> How It Works

**gui-agent** operates as a closed-loop Computer Use bridge between frontier LLM reasoning engines and the host operating system. The execution pipeline ensures zero spatial hallucinations through deterministic coordinate normalization and hybrid fallback mechanisms.

<p align="center">
  <img src="https://gist.githubusercontent.com/lender926-lab/050b95747c45950573c28906fcb1fae6/raw/exc-how-it-works-en.svg" alt="gui-agent Architecture Workflow" width="100%" style="border-radius: 10px;" />
</p>

### Technical Execution Pipeline

1. **Sub-second Screen Ingestion & Cartesian Grid Overlay**: When an agent requests visual state via `gui_take_screenshot`, the server captures the raw framebuffer through MSS. If XWayland compositing renders a blank frame, it transparently falls back to KDE Spectacle or Scrot. The engine overlays a millimeter Cartesian coordinate grid with adaptive contrast-buffered labels at customizable intervals (e.g. 100px), enabling LLMs to infer target coordinates with mathematical certainty.
2. **Standardized JSON-RPC 2.0 stdio Interface**: Built on FastMCP, the server communicates over standard input/output streams without opening vulnerable network ports or spawning complex daemon topologies. All tool signatures are statically typed and validated through Pydantic schemas.
3. **Dual Coordinate Normalization Engine**: The server accepts coordinates in either absolute physical pixels `(x, y)` or normalized ratios `[0, 1000]` across any display geometry or multi-monitor setup. An automatic converter handles boundary clamping, DPI scaling, and coordinate translation.
4. **Native OS Input & Window Dispatcher**: Keystrokes, hotkeys, mouse clicks, and drag operations are routed through low-latency native drivers (`xdotool` and `python-xlib` under Linux, Win32 API under Windows). Humanized delays and micro-jitter emulate natural user interaction. Window management commands (`wmctrl` / `xprop`) inspect and manipulate window states without window manager locks.
5. **Local Vision, OCR & Playwright Automation**: Template matching (`cv2.matchTemplate`) enables robust icon detection even under theme variations. Text discovery combines Tesseract OCR with RapidOCR ONNX fallback. Web automation leverages Playwright to inspect ARIA trees and manipulate DOM nodes directly without visual ambiguity.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="Package" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Installation

> For detailed OS-specific instructions, troubleshooting matrices, and offline setups, see the [**Detailed Installation Guide (INSTALL.md)**](INSTALL.md).

### 1. Automated Installation (Recommended)

#### Linux (Bash)
Run the automated installer to check dependencies, install Astral `uv`, configure the isolated environment, and register the MCP server:

```bash
# Single-line curl installer
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/install.sh | bash

# Or locally from a cloned repository
./install.sh
```

#### Microsoft Windows (PowerShell)
Launch PowerShell (standard user or administrator) and execute:

```powershell
# Single-line PowerShell installer
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/install.ps1 | iex"

# Or locally from a cloned repository
.\install.ps1 -Local
```

### 2. Isolated Deployment via uv tool

Install `gui-agent` directly into an isolated environment with global CLI entrypoints:

```bash
# Install from PyPI
uv tool install gui-agent

# Or install from GitHub repository
uv tool install "git+https://github.com/leandre755/gui_agent.git"

# Upgrade to latest release
uv tool upgrade gui-agent
```

### 3. Linux System Prerequisites

Under Linux, install the native window management, OCR, and media libraries:

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
Retrieves display parameters, monitor topologies, active resolution, and session variables.
- **Parameters**: None.
- **Returns**: `dict` containing `resolution`, `width`, `height`, `monitors` list, `display_env`, and `failsafe_enabled`.

#### `gui_take_screenshot`
Captures full-screen or cropped images with an optional Cartesian coordinate grid overlay.
- **Parameters**:
  - `monitor_index` (`int`, default `1`): Target monitor index (`0` for virtual canvas).
  - `crop_box` (`list[int] | None`, default `None`): Sub-region `[x, y, width, height]`.
  - `apply_grid` (`bool`, default `True`): Overlays the Cartesian coordinate grid.
  - `grid_interval` (`int`, default `100`): Interval in pixels between grid lines (minimum 20).
  - `format` (`str`, default `"png"`): Output image format (`"png"` or `"jpeg"`).
  - `quality` (`int`, default `80`): Compression quality (1-100) for JPEG output.
  - `output_path` (`str | None`, default `None`): Destination file path. Relative paths are resolved to absolute paths and missing parent directories are created. Empty paths and existing directories are rejected. If the path lacks an extension, the extension corresponding to `format` is automatically appended. Incompatible extensions are rejected. If the target file already exists, atomic reservation with incremental suffixes such as `(1)` and `(2)` protects existing files from overwrite. `screenshot_path` returns the actual resolved absolute path used. If omitted, defaults to a timestamped image in the screenshots directory.
  - `include_base64` (`bool`, default `False`): Returns Base64-encoded string representation.
- **Returns**: `dict` containing `screenshot_path` (resolved absolute path), `raw_screenshot_path`, `format`, `resolution`, `cropped`, `grid_applied`, `grid_interval`, `renamed_due_to_conflict`, `message`, and `base64_data` (present when `include_base64` is enabled).

#### `gui_mouse_move`
Smoothly translates the mouse cursor to target coordinates.
- **Parameters**:
  - `x` (`float`): Target X position.
  - `y` (`float`): Target Y position.
  - `duration` (`float`, default `0.2`): Movement interpolation duration in seconds.
  - `normalized` (`bool`, default `False`): Set to `True` when using `[0, 1000]` coordinates.
  - `monitor_index` (`int`, default `1`): Reference monitor for coordinate calculations.

#### `gui_mouse_click`
Executes single, double, or multi-clicks at specific coordinates.
- **Parameters**:
  - `x` (`float`): Target X position.
  - `y` (`float`): Target Y position.
  - `button` (`str`, default `"left"`): Mouse button (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, default `1`): Number of clicks to perform.
  - `normalized` (`bool`, default `False`): Set to `True` for `[0, 1000]` coordinates.
  - `monitor_index` (`int`, default `1`): Reference monitor.

#### `gui_mouse_drag`
Performs a smooth click-and-drag gesture between two spatial locations.
- **Parameters**:
  - `x1` (`float`): Starting X position.
  - `y1` (`float`): Starting Y position.
  - `x2` (`float`): Ending X position.
  - `y2` (`float`): Ending Y position.
  - `duration` (`float`, default `0.5`): Drag animation duration in seconds.
  - `normalized` (`bool`, default `False`): Set to `True` for `[0, 1000]` coordinates.
  - `monitor_index` (`int`, default `1`): Reference monitor.

#### `gui_mouse_scroll`
Simulates mouse wheel scrolling along vertical or horizontal axes.
- **Parameters**:
  - `clicks` (`int`): Number of scroll ticks (positive integer).
  - `direction` (`str`, default `"down"`): Direction (`"up"`, `"down"`, `"left"`, `"right"`).

#### `gui_keyboard_type`
Types text sequentially with natural human-like timing variations.
- **Parameters**:
  - `text` (`str`): String content to type.
  - `delay` (`float`, default `0.06`): Base delay between keystrokes in seconds.

#### `gui_keyboard_press`
Simulates individual key presses or complex modifier combinations.
- **Parameters**:
  - `key` (`str`): Key identifier or chord (e.g., `"Return"`, `"Escape"`, `"ctrl+c"`, `"alt+tab"`, `"super"`).

#### `gui_clipboard_get`
Reads current textual content from the system clipboard.
- **Parameters**: None.
- **Returns**: `dict` containing clipboard `text`, character `length`, and retrieval `method`.

#### `gui_clipboard_set`
Writes string content into the OS clipboard.
- **Parameters**:
  - `text` (`str`): Text content to store in the clipboard.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Window.png" alt="Window" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Window & Process Control (5 tools)</b></summary>

#### `gui_window_list`
Enumerates all active desktop windows with metadata.
- **Parameters**: None.
- **Returns**: `dict` with `windows` array containing window `id`, `title`, `pid`, and `wm_class`.

#### `gui_window_focus`
Activates and brings a specified window to the front.
- **Parameters**:
  - `window_id` (`int`): Numeric window ID obtained from `gui_window_list`.

#### `gui_window_resize_move`
Reposition and resize an application window in a single atomic operation.
- **Parameters**:
  - `window_id` (`int`): Target numeric window ID.
  - `x` (`int`): New top-left X coordinate.
  - `y` (`int`): New top-left Y coordinate.
  - `width` (`int`): New window width in pixels.
  - `height` (`int`): New window height in pixels.

#### `gui_window_close`
Sends an orderly close request to a target window.
- **Parameters**:
  - `window_id` (`int`): Target numeric window ID.

#### `gui_app_launch`
Spawns an operating system process or binary.
- **Parameters**:
  - `command` (`str`): Shell command line or binary path to launch.
  - `background` (`bool`, default `True`): Run asynchronously detached (`True`) or wait synchronously (`False`).

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magnifying%20Glass%20Tilted%20Left.png" alt="Search" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Vision & OCR Automation (3 tools)</b></summary>

#### `gui_find_template`
Performs normalized template matching via OpenCV to locate graphical elements.
- **Parameters**:
  - `template_path` (`str`): File path to the reference template image.
  - `threshold` (`float`, default `0.8`): Confidence threshold (between 0.01 and 1.0).
  - `monitor_index` (`int`, default `1`): Monitor index to inspect.
- **Returns**: `dict` containing match center coordinates `(x, y)` and matching `confidence`.

#### `gui_find_text`
Extracts text bounding boxes via OCR (Tesseract / RapidOCR) and calculates centroid coordinates.
- **Parameters**:
  - `text` (`str`): Target string to discover.
  - `confidence` (`float`, default `0.6`): Minimum OCR confidence score (0.0 to 1.0).
  - `monitor_index` (`int`, default `1`): Monitor index to search.
- **Returns**: `dict` containing `text_found`, centroid `(x, y)`, `confidence`, and bounding box `[x, y, w, h]`.

#### `gui_click_text`
Executes an OCR search and dispatches a mouse click directly to the centroid of the discovered text.
- **Parameters**:
  - `text` (`str`): Target text string to locate and click.
  - `button` (`str`, default `"left"`): Mouse button to click (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, default `1`): Number of clicks to perform.
  - `monitor_index` (`int`, default `1`): Target monitor.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Movie%20Camera.png" alt="Camera" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Web & Multimedia Recording (3 tools)</b></summary>

#### `gui_web_action`
Interacts directly with web pages via headless Chromium powered by Playwright.
- **Parameters**:
  - `url` (`str`): Web address or local file URL to navigate to.
  - `action` (`str`, default `"aria_tree"`): Action to perform (`"aria_tree"`, `"click"`, `"type"`, `"screenshot"`).
  - `selector` (`str | None`, default `None`): CSS or XPath selector for `click` and `type` actions.
  - `text` (`str | None`, default `None`): Text payload to input when `action="type"`.
  - `viewport_width` (`int`, default `1280`): Browser viewport width.
  - `viewport_height` (`int`, default `720`): Browser viewport height.
  - `timeout_ms` (`int`, default `30000`): Navigation and locator timeout in milliseconds.

#### `gui_start_video_recording`
Launches an asynchronous screen recording sub-process using FFmpeg with minimal CPU overhead.
- **Parameters**:
  - `output_path` (`str | None`, default `None`): Destination file path (defaults to timestamped MP4 in screenshots dir).
  - `fps` (`int`, default `5`): Video capture frame rate (1 to 30 FPS).
  - `monitor_index` (`int`, default `1`): Target monitor index.
  - `duration` (`int | None`, default `None`): Optional automatic duration limit in seconds.

#### `gui_stop_video_recording`
Cleanly terminates the ongoing FFmpeg recording and validates the generated MP4 file container.
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

To cleanly purge `gui-agent`, delete isolated environments, and remove registered MCP configurations:

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

The project enforces strict software engineering standards, verified by an 8-layer pre-commit hook pipeline and full test coverage.

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

Every commit is gated through 8 strict static validation layers to eliminate technical debt and security vulnerabilities:

```bash
# Run the 8-layer Zero-Slop validation hook locally
ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit
```

| Layer | Validator | Scope & Quality Invariants Enforced |
| :--- | :--- | :--- |
| 1 | `anti-leak` | Blocks secret tokens, private keys, and `.env` credentials from staged files. |
| 2 | `pip-audit` | Audits Python dependency tree against known CVE vulnerability databases. |
| 3 | `ruff check` | Enforces zero lint warnings, PEP 8 standards, and modern Python 3.10+ idioms. |
| 4 | `ruff format` | Verifies deterministic, uniform code formatting across all Python sources. |
| 5 | `mypy` | Strict static type checking with zero untyped definitions permitted. |
| 6 | `sonar/smells` | Checks cognitive complexity (McCabe C90 <= 25), bug hazards, and simplifications. |
| 7 | `bandit` | Static AST security analysis preventing insecure subprocess calls and patterns. |
| 8 | `semgrep` | SAST security scanner detecting code injection and system boundary risks. |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Scroll.png" alt="Scroll" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> License

This project is licensed under the terms of the [MIT License](LICENSE).

Copyright (c) 2026 Leandre. All rights reserved.
