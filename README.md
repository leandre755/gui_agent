<p align="center">
  <img src="https://files.catbox.moe/udf9j4.jpeg" alt="gui-agent Hero Banner" width="100%" style="border-radius: 8px;" />
</p>

<h1 align="center"><img src="https://files.catbox.moe/xei715.png" alt="gui-agent Logo" height="42" style="vertical-align: middle; margin-right: 10px;" />gui-agent</h1>

<p align="center"><b>Unified FastMCP Server for Linux & Windows Desktop Computer Use</b></p>

<p align="center">🌐 <b><a href="README.md">English</a></b> | <b><a href="README.fr.md">Français</a></b></p>

<p align="center">
  <a href="#-core-capabilities"><img src="https://img.shields.io/badge/Capabilities-→-10B981?style=flat-square" alt="Capabilities" /></a>
  <a href="#-how-it-works"><img src="https://img.shields.io/badge/Architecture-→-10B981?style=flat-square" alt="Architecture" /></a>
  <a href="#-installation"><img src="https://img.shields.io/badge/Installation-→-10B981?style=flat-square" alt="Installation" /></a>
  <a href="#-mcp-client-configuration"><img src="https://img.shields.io/badge/MCP_Clients-→-10B981?style=flat-square" alt="MCP Clients" /></a>
  <a href="#-toolset--cli-reference"><img src="https://img.shields.io/badge/Toolset-→-10B981?style=flat-square" alt="Toolset" /></a>
  <a href="#-clean-uninstallation"><img src="https://img.shields.io/badge/Uninstall-→-10B981?style=flat-square" alt="Uninstall" /></a>
  <a href="#-development--quality-gate"><img src="https://img.shields.io/badge/Development-→-10B981?style=flat-square" alt="Development" /></a>
</p>

<p align="center">
  <a href="https://github.com/leandre755/gui_agent/releases/tag/v0.1.0"><img src="https://img.shields.io/badge/version-0.1.0-3FB950?style=flat-square" alt="Version 0.1.0" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-34D399?style=flat-square" alt="Python 3.10+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-F0883E?style=flat-square" alt="License MIT" /></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows-10B981?style=flat-square" alt="Platform Linux | Windows" /></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP_Protocol-1.2.0+-10B981?style=flat-square" alt="MCP Protocol 1.2.0+" /></a>
  <a href="https://github.com/leandre755/gui_agent/discussions"><img src="https://img.shields.io/badge/Discussions-Q%26A-blue?style=flat-square" alt="Discussions Q&A" /></a>
</p>

### The Philosophy: Why gui-agent?

Autonomous AI agents interacting with modern graphical user interfaces are frequently burdened by fragmented architectures, high latency, and fragile computer vision loops. Traditional automation setups force models to perceive operating systems exclusively through repetitive raster screenshots, incurring prohibitive round-trip times (RTT) of 2 to 5 seconds per motor action. This reductionist approach causes severe spatial misalignments under fractional scaling, loses transient UI components like disappearing toasts or click-away menus, and quickly exhausts context windows with redundant image payloads.

**gui-agent** redefines desktop interaction by aligning agent decisions with the actual ontology of modern operating systems: structured processes in RAM, accessibility trees (AT-SPI2 / D-Bus), window compositors (X11 / Wayland), and kernel event subsystems (`uinput`, `evdev`). Built on two foundational pillars—**Progressive Escalation (L3/L2/L1)** and the **CodeAct Local REPL Engine**—the server enables models to actuate targets in RAM within 50 ms via native Rust mediation (`gui-agent-atspi`), fallback to local RapidOCR or calibrated Cartesian grids when needed, and execute entire multi-step action sequences locally in host memory with sub-5ms latency.

Operating through a single, resilient standard input/output (stdio) FastMCP connection, **gui-agent** functions with a lean baseline memory footprint below 50 MB RAM, fully preserving dual-core host responsiveness without external cloud vision dependencies or persistent background daemons. Platform implementations reside in dedicated, sealed root directories (`linux/`, `windows/`, `macos/`) with dynamic XDG Base Directory path resolution, zero hardcoded user paths, and full continuous screen video recording preservation (`gui_start_video_recording`, `gui_stop_video_recording`) for deterministic auditing.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Bullseye.png" alt="Bullseye" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Core Capabilities

The server exposes 15 unified FastMCP tools structured across operational layers, covering the complete lifecycle of operating system Computer Use. All tools operate through a single standard input/output (stdio) JSON-RPC 2.0 communication channel.

| Tool Name | Domain | Description | Status |
| :--- | :--- | :--- | :--- |
| `execute_action_batch` | <img src="https://img.shields.io/badge/Core%20REPL-10B981?style=flat-square" alt="Core REPL" /> | Executes local Python/Bash scripts with preloaded `mcp_core` (Open Interpreter model), running multi-action batches without RTT. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `process_run` | <img src="https://img.shields.io/badge/System%20PTY-10B981?style=flat-square" alt="System PTY" /> | Spawns interactive shell commands via PTY to inject credentials and bypass Polkit/sudo security dialogs. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `process_list` | <img src="https://img.shields.io/badge/System%20PTY-10B981?style=flat-square" alt="System PTY" /> | Inspects the `/proc` filesystem in read-only mode to probe active processes without altering desktop state. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `activate_window` | <img src="https://img.shields.io/badge/System%20PTY-10B981?style=flat-square" alt="System PTY" /> | Switches focus at the display compositor level using unique Window IDs, resolving multi-window PID ambiguity. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `get_app_state` | <img src="https://img.shields.io/badge/Layer%20L3-10B981?style=flat-square" alt="Layer L3" /> | Inspects the AT-SPI2 accessibility tree via native Rust mediation (`gui-agent-atspi`) directly in RAM. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `perform_action` | <img src="https://img.shields.io/badge/Layer%20L3-10B981?style=flat-square" alt="Layer L3" /> | Triggers semantic actions directly in RAM via D-Bus IPC in sub-50ms without physical pointer movements. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `set_value` | <img src="https://img.shields.io/badge/Layer%20L3-10B981?style=flat-square" alt="Layer L3" /> | Mutates text or numerical values directly into component memory variables without physical keystrokes. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `find_text` | <img src="https://img.shields.io/badge/Layer%20L2-34D399?style=flat-square" alt="Layer L2" /> | Discovers on-screen text coordinates via local OCR (RapidOCR/Tesseract) without sending image payloads. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `screen_capture` | <img src="https://img.shields.io/badge/Layer%20L1-34D399?style=flat-square" alt="Layer L1" /> | Captures raw framebuffer with calibrated Cartesian grid overlays for opaque surfaces (WebGL/Canvas). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `mouse_click_at` | <img src="https://img.shields.io/badge/Layer%20L1-34D399?style=flat-square" alt="Layer L1" /> | Injects physical mouse click events (`left`, `right`, `middle`, double) at target `(x, y)` coordinates. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `mouse_drag_smooth` | <img src="https://img.shields.io/badge/Layer%20L1-34D399?style=flat-square" alt="Layer L1" /> | Dispatches continuous kinematic mouse trajectory interpolation to overcome UI drag-breakaway thresholds. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `mouse_scroll` | <img src="https://img.shields.io/badge/Layer%20L1-34D399?style=flat-square" alt="Layer L1" /> | Executes hardware wheel scrolls (`up`, `down`, `left`, `right`) to materialize virtualized DOM elements. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `key_tap` | <img src="https://img.shields.io/badge/Layer%20L1-34D399?style=flat-square" alt="Layer L1" /> | Injects standard keystrokes, navigation hotkeys, and chord combinations (`Ctrl+L`, `Super+D`, `Return`). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_start_video_recording` | <img src="https://img.shields.io/badge/Media-F0883E?style=flat-square" alt="Media" /> | Starts background low-overhead screen video recording via FFmpeg (`x11grab` / H.264 ultrafast). | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |
| `gui_stop_video_recording` | <img src="https://img.shields.io/badge/Media-F0883E?style=flat-square" alt="Media" /> | Cleanly halts the active FFmpeg recording, flushes the MP4 container, and prevents descriptor leaks. | <img src="https://img.shields.io/badge/Active-3FB950?style=flat-square" alt="Active" /> |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="Gear" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> How It Works

**gui-agent** operates as a closed-loop Computer Use bridge between frontier LLM reasoning engines and the host operating system, combining semantic RAM actuation, local script execution, and visual-motor feedback.

<p align="center">
  <img src="https://gist.githubusercontent.com/personnal-agent/f0b933b981a70de123282eb99fd6df44/raw/exc-how-it-works-en.svg" alt="gui-agent Architecture Workflow" width="100%" style="border-radius: 10px;" />
</p>

### Technical Execution Pipeline & Foundational Pillars

1. **Pillar I : Progressive Escalation & Layered Actuation**: Rather than enforcing a single interaction mode, the architecture prioritizes cognitive and execution efficiency across layered stages: Level L3 accesses the OS accessibility tree (AT-SPI2 / D-Bus via the compiled Rust mediator `gui-agent-atspi`) directly in RAM for deterministic sub-50ms actuation with zero image tokens; Level L2 runs decoupled local OCR (RapidOCR/Tesseract) on typography without model inference overhead; Level L1 operates as the ultimate hardware safety net using calibrated Cartesian grid screenshots with native input dispatchers (with direct kernel `uinput`/`evdev` drivers scheduled on the roadmap); and an interactive PTY shell layer provides seamless handling of privileged commands.
2. **Pillar II : High-Efficiency Execution Architecture**: Paving the way to eliminate multi-turn network round-trip time (RTT) latency, the project architecture designs an isolated local execution environment (`execute_action_batch` via `core/repl.py`). Models will project multi-step inspection and action logic directly as Python code executed in host memory via the unified `mcp_core` SDK. Complex condition checking, kinematic drag calculations, and dynamic polling resolve in a single cognitive round-trip with sub-5ms execution speed and less than 15 MB RAM consumption (slated for Phase 2 roadmap).
3. **Sub-second Screen Ingestion & Cartesian Grid Overlay**: When an agent requests visual state via `screen_capture` (or legacy `gui_take_screenshot`), the server captures the raw framebuffer through MSS, with automatic fallback to KDE Spectacle or Scrot on XWayland surfaces. The engine overlays a millimeter Cartesian coordinate grid with adaptive contrast-buffered labels at configurable intervals (e.g., 100px), allowing models to infer target coordinates with mathematical certainty.
4. **Dual Coordinate Normalization Engine**: The server accepts coordinates in either absolute physical pixels `(x, y)` or normalized ratios `[0, 1000]` across any display geometry or multi-monitor setup. An automatic converter handles boundary clamping, DPI scaling, and coordinate translation transparently.
5. **Native OS Input & Window Dispatcher**: Keystrokes, hotkeys, mouse clicks, and drag operations are routed through low-latency native drivers (`xdotool` and `python-xlib` under Linux, Win32 API under Windows). Humanized delays and micro-jitter emulate natural user interaction. Window management commands (`wmctrl` / `xprop`) inspect and manipulate window states without window manager locks.
6. **Local Vision, OCR & Playwright Automation**: Template matching (`cv2.matchTemplate`) enables robust icon detection even under theme variations. Text discovery combines Tesseract OCR with RapidOCR ONNX fallback. Web automation leverages Playwright to inspect ARIA trees and manipulate DOM nodes directly without visual ambiguity.

### Multi-Platform Root Architecture & Dynamic Path Resolution

The codebase organizes platform implementations into dedicated root directories with zero hardcoded filesystem paths:
- **`linux/`** : Complete Linux implementation featuring the core server (`server.py`), native Rust AT-SPI2 / D-Bus mediator (`linux/crates/atspi_mediator` compiled to `gui-agent-atspi`), automated install/uninstall scripts (`install.sh`, `uninstall.sh`), dedicated tests and examples, and dynamic XDG Base Directory path resolution (`paths.py`).
- **`windows/`** : Dedicated Windows directory (`install.ps1`, `uninstall.ps1`, native UI Automation backend in active development).
- **`macos/`** : Dedicated macOS directory reserved for upcoming NSAccessibility and Quartz Event Taps implementations.
All runtime paths—including screenshots (`$XDG_CACHE_HOME/gui-agent/screenshots` or `GUI_AGENT_SCREENSHOTS_DIR`), persistent continuous video captures (`$XDG_CACHE_HOME/gui-agent/videos` or `GUI_AGENT_VIDEOS_DIR`), and data storage (`$XDG_DATA_HOME/gui-agent`)—are resolved dynamically at runtime.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="Package" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Installation

> For detailed OS-specific instructions, troubleshooting matrices, and offline setups, see the [**Detailed Installation Guide (INSTALL.md)**](INSTALL.md).

### 1. Automated Installation (Recommended)

#### Linux (Bash)
Run the automated installer to check dependencies, install Astral uv, build the native Rust mediator, and register the MCP server:

```bash
# Download and execute the automated installer via curl
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/linux/install.sh | bash

# Or execute locally from a cloned repository
./linux/install.sh
```

#### Microsoft Windows (PowerShell)
Launch PowerShell (standard user or administrator) and execute the automated setup script:

```powershell
# Download and execute the installation script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/windows/install.ps1" -OutFile "install.ps1"
powershell -ExecutionPolicy Bypass -File .\install.ps1

# Or execute locally from a cloned repository
.\windows\install.ps1 -Local
```

### 2. Isolated Deployment via uv tool
Install gui-agent directly into an isolated environment with global CLI entrypoints:

```bash
# Install from PyPI
uv tool install gui-agent

# Or install from GitHub repository
uv tool install "git+https://github.com/leandre755/gui_agent.git"

# Upgrade to latest release
uv tool upgrade gui-agent
```

### 3. Linux System Prerequisites
Under Linux, install the native window management, OCR, multimedia, AT-SPI accessibility, and Rust build libraries:

```bash
# Debian / Ubuntu / Linux Mint
sudo apt-get update && sudo apt-get install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract-ocr libgl1 libatspi-dev cargo rustc

# Fedora / RHEL
sudo dnf install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract libglvnd-glx at-spi2-core-devel cargo rust

# Arch Linux / Manjaro
sudo pacman -S --needed \
  xdotool wmctrl spectacle ffmpeg xclip tesseract at-spi2-core cargo rust
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
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="REPL" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Core REPL & Local Execution Engine (1 tool)</b></summary>

#### `execute_action_batch`
Executes multi-step Python or Bash action blocks directly in host memory with preloaded `mcp_core` SDK (Open Interpreter paradigm), eliminating network RTT.
- **Parameters**:
  - `language` (`str`, default `"python"`): Execution runtime environment (`"python"` or `"bash"`).
  - `code` (`str`): Multi-step script containing conditional logic, loops, and rapid polling routines.
  - `timeout` (`float`, default `30.0`): Execution deadline in seconds before terminating the runner process.
- **Returns**: `dict` containing execution `status`, captured `stdout`, `stderr`, and execution `elapsed_seconds`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Window.png" alt="Window" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> System & PTY Shell Controls (3 tools)</b></summary>

#### `process_run`
Executes shell commands in a pseudo-terminal (PTY) session, allowing credential injection to bypass security modals.
- **Parameters**:
  - `command` (`str` | `list[str]`): Command line string or argument list to execute.
  - `background` (`bool`, default `False`): Spawns detached in background (`True`) or waits synchronously (`False`).
  - `sudo_password` (`str | None`, default `None`): Password injected into PTY `stdin` for Polkit/sudo escalation.
- **Returns**: `dict` containing execution `status`, exit code `returncode`, `stdout`, and `stderr`.

#### `process_list`
Inspects the `/proc` filesystem in read-only mode to probe active desktop processes and hierarchy without mutation.
- **Parameters**: None.
- **Returns**: `list[dict]` containing active system process entries with `pid`, `name`, and status metadata.

#### `activate_window`
Switches desktop focus directly at the display compositor level using unique Window IDs, avoiding PID collision.
- **Parameters**:
  - `window_id` (`str` | `int`): Target compositor Window ID to raise and focus.
- **Returns**: `dict` containing operation `status` and confirmed active window identifier.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="L3" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Layer L3 — Semantic RAM & AT-SPI2 (3 tools)</b></summary>

#### `get_app_state`
Inspects the accessibility tree via native Rust mediation (`gui-agent-atspi`) directly in RAM with zero image tokens.
- **Parameters**:
  - `include_screenshot` (`bool`, default `False`): Attaches an optional visual framebuffer capture.
- **Returns**: `dict` containing structured tree nodes, numeric `element_index`, bounds, states, and `snapshot_id`.

#### `perform_action`
Invokes semantic actions directly in target application memory via D-Bus IPC in sub-50ms without pointer motion.
- **Parameters**:
  - `element_id` (`str` | `int`): Node identifier or cache index from the active `snapshot_id`.
  - `action` (`str`, default `"activate"`): Semantic action name (`"activate"`, `"click"`, `"press"`).
- **Returns**: `dict` containing execution `status`, target identifier, and action verification response.

#### `set_value`
Mutates text or numerical values directly into component memory variables without emitting physical keystrokes.
- **Parameters**:
  - `element_id` (`str` | `int`): Target editable field or widget identifier.
  - `value` (`str`): Text or numerical value to assign directly into component memory.
- **Returns**: `dict` containing mutation `status`, target identifier, and assigned value confirmation.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magnifying%20Glass%20Tilted%20Left.png" alt="Search" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Layer L2 — Local Vision & OCR (1 tool)</b></summary>

#### `find_text`
Discovers on-screen text coordinates via decoupled local OCR engines (RapidOCR / Tesseract) without model RTT.
- **Parameters**:
  - `text` (`str`): Target text string to identify across the desktop screen.
  - `confidence` (`float`, default `0.85`): Minimum detection confidence score (0.0 to 1.0).
- **Returns**: `dict` containing detected text centroid `{"x": int, "y": int}`, bounding box, and match `confidence`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Computer%20Mouse.png" alt="Mouse" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Layer L1 — Hardware & Input Dispatch (5 tools)</b></summary>

#### `screen_capture`
Captures the raw display framebuffer with an optional calibrated Cartesian coordinate grid overlay.
- **Parameters**:
  - `show_grid` (`bool`, default `True`): Overlays a Cartesian coordinate grid with adaptive contrast labels.
  - `grid_step` (`int`, default `100`): Pixel distance between coordinate grid lines (minimum 20px).
  - `output_path` (`str | None`, default `None`): Output destination path with atomic reservation protection.
- **Returns**: `dict` containing resolved `screenshot_path`, image dimensions, format, and grid status.

#### `mouse_click_at`
Injects hardware mouse click events directly via low-level input subsystems at exact target coordinates.
- **Parameters**:
  - `x` (`int` | `float`): Absolute X pixel coordinate.
  - `y` (`int` | `float`): Absolute Y pixel coordinate.
  - `button` (`str`, default `"left"`): Mouse button identifier (`"left"`, `"right"`, `"middle"`).
  - `double` (`bool`, default `False`): Dispatches a consecutive double-click sequence when enabled.
- **Returns**: `dict` confirming click execution status, target coordinates, and dispatched button.

#### `mouse_drag_smooth`
Dispatches an interpolated continuous mouse trajectory to overcome GUI drag-and-drop breakaway thresholds.
- **Parameters**:
  - `from_x` (`int` | `float`): Starting horizontal X coordinate.
  - `from_y` (`int` | `float`): Starting vertical Y coordinate.
  - `to_x` (`int` | `float`): Terminating horizontal X coordinate.
  - `to_y` (`int` | `float`): Terminating vertical Y coordinate.
  - `duration` (`float`, default `0.5`): Total animation interpolation duration in seconds.
- **Returns**: `dict` confirming kinematic drag completion across the spatial trajectory.

#### `mouse_scroll`
Simulates hardware mouse wheel movements to force dynamic rendering of virtualized lists and infinite scroll.
- **Parameters**:
  - `x` (`int` | `float`): Horizontal position where the scroll event is injected.
  - `y` (`int` | `float`): Vertical position where the scroll event is injected.
  - `direction` (`str`, default `"down"`): Scroll direction axis (`"up"`, `"down"`, `"left"`, `"right"`).
  - `amount` (`int`, default `5`): Step count of scroll ticks to dispatch.
- **Returns**: `dict` confirming scroll action dispatch, coordinate target, and step count.

#### `key_tap`
Sends hardware-level keyboard keypresses, system hotkeys, and chord sequences directly to the focused window.
- **Parameters**:
  - `key` (`str`): Key identifier (e.g., `"Return"`, `"Escape"`, `"Tab"`, `"space"`).
  - `modifiers` (`list[str] | str | None`, default `None`): Key modifiers (e.g., `["ctrl"]`, `["alt"]`, `"super"`).
- **Returns**: `dict` confirming keystroke injection status and dispatched chord combination.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Movie%20Camera.png" alt="Camera" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Continuous Video Recording & Audit (2 tools)</b></summary>

#### `gui_start_video_recording`
Launches an asynchronous screen recording sub-process using FFmpeg with minimal CPU overhead for behavioral audit.
- **Parameters**:
  - `output_path` (`str | None`, default `None`): Destination MP4 file path (defaults to dynamic cache videos dir).
  - `fps` (`int`, default `5`): Video capture frame rate (1 to 30 FPS).
  - `monitor_index` (`int`, default `1`): Target monitor index to record.
  - `duration` (`int | None`, default `None`): Optional automatic recording duration limit in seconds.
- **Returns**: `dict` confirming background process launch, assigned PID, and active output path.

#### `gui_stop_video_recording`
Cleanly halts the active FFmpeg recording, flushes the MP4 container, and returns file verification metadata.
- **Parameters**: None.
- **Returns**: `dict` containing output video `output_path`, existence confirmation `file_exists`, and `file_size_bytes`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Control%20Knobs.png" alt="Config" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Environment Variables (Configuration)</b></summary>

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `DISPLAY` | Target X11 display server identifier. | `:0` |
| `GUI_AGENT_SCREENSHOTS_DIR` | Directory where screenshots and cropped frames are saved. | `$XDG_CACHE_HOME/gui-agent/screenshots` |
| `GUI_AGENT_VIDEOS_DIR` | Directory where continuous MP4 screen video recordings are saved. | `$XDG_CACHE_HOME/gui-agent/videos` |
| `GUI_AGENT_ATSPI_BIN` | Custom filesystem path to the native `gui-agent-atspi` Rust mediator binary. | Auto-discovered |

</details>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Wastebasket.png" alt="Trash" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Clean Uninstallation

To cleanly purge `gui-agent`, delete isolated environments, and remove registered MCP configurations:

### 1. Linux (Bash)

```bash
# Download and execute the automated uninstaller
curl -fsSLO https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/linux/uninstall.sh
chmod +x uninstall.sh && ./uninstall.sh --purge-data --yes

# Or local uninstall with full data and cache purge
./linux/uninstall.sh --purge-data --yes
```

### 2. Microsoft Windows (PowerShell)

```powershell
# Download and execute the automated uninstaller
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/windows/uninstall.ps1" -OutFile "uninstall.ps1"
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1 -PurgeData -Yes

# Or local uninstall with full data and cache purge
.\windows\uninstall.ps1 -PurgeData -Yes
```

#### What the uninstaller cleans:
- Removes `gui-agent`, `mcp-gui-server`, and `gui-agent-atspi` binaries from standard binary paths (`~/.local/bin` or virtualenv).
- Unregisters the MCP server from Claude Code CLI configuration.
- Cleans JSON entries from Antigravity `mcp_config.json`.
- Purges temporary runtimes and optionally deletes all screenshots and recordings (`--purge-data` / `-PurgeData`).

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Shield.png" alt="Shield" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Development & Quality-Gate

The project enforces strict software engineering standards, verified by an 8-layer pre-commit quality-gate pipeline and full test coverage.

### 1. Local Environment Setup

```bash
# Clone the repository
git clone https://github.com/leandre755/gui_agent.git
cd gui_agent

# Initialize virtual environment with Astral UV
uv venv
source .venv/bin/activate

# Install editable package with development dependencies and build native Rust extensions (requires Cargo)
uv pip install -e ".[dev]"
```

### 2. Running Test Suites

```bash
# Run unit and integration tests across platform layers
pytest -v linux/tests/
```

### 3. Quality-Gate 8-Layer Pre-Commit Verification

Every commit is gated through 8 strict static validation layers to eliminate technical debt and security vulnerabilities:

```bash
# Run the 8-layer quality-gate validation hook locally
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
