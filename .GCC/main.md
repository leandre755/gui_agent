# Current Project Context

## 🏆 Major Milestones (Archived Epics)
- [2026-08-14] FastMCP Monolithic Architecture & 21 Desktop Tools Implementation
- [2026-08-14] Multi-Layer Quality & Pre-Commit 8-Layer Zero-Slop Pipeline
- [2026-08-15] Complete README Overhaul: Landing Page UX, Hosted Excalidraw SVGs, Official Transparent Logo & Landscape Hero Banner, Bilingual Line-for-Line Isomorphism (475 lines), and De-AI Humanization Pass

## 🎯 Objective
High-performance, monolithic FastMCP server engineered for direct, low-latency Computer Use on Linux (X11/XWayland) and Windows desktop environments (<50 MB RAM, 21 tools, zero-leak process lifecycle).

## 🧠 Decisions Made
- [2026-08-14] Monolithic FastMCP Architecture over Multi-Microservice Topology
  - **Context**: LLM context limits and port conflict risks under multiple concurrent tool servers.
  - **Discarded Options**: Dynamic subprocess spawning per tool group; separated multi-server endpoints.
  - **Rationale**: Monolithic stdio design preserves <50 MB RAM, single connection, zero port risk.
- [2026-08-14] Animated Fluent 3D Emojis & Zero Keyboard Emojis in Headers
  - **Context**: Standard keyboard emojis in headers appear unstyled and inconsistent across OS.
  - **Discarded Options**: Raw unicode emojis in H2/H3; plain text headings.
  - **Rationale**: Microsoft Fluent 3D Animated Emojis via raw CDN URLs provide state-of-the-art landing page aesthetics matching the Emerald palette.
- [2026-08-14] External Media Hosting (Gist & CDN) over Local Repository Assets
  - **Context**: Storing images, banners, and SVGs inside repository tree pollutes codebase and increases clone size.
  - **Discarded Options**: Committing media to `assets/` in git tracking.
  - **Rationale**: Public GitHub Gist for SVGs and fast CDN for PNG/JPEG assets keep the codebase 100% lightweight and clean.
- [2026-08-15] Excalidraw Architecture Flowcharts over Mermaid for Expressive Systems
  - **Context**: Mermaid renders emojis poorly and creates tall vertical flowcharts.
  - **Discarded Options**: ASCII text boxes, raw inline Mermaid code.
  - **Rationale**: Excalidraw compact landscape layout (920x640px) enables hand-drawn cartoon aesthetics, expressive icons, and clean SVG vector rendering.
- [2026-08-15] Documentation Humanization (De-AI Prose)
  - **Context**: Generic LLM prose often contains repetitive promotional fluff, superficial analysis, and heavy connectives.
  - **Discarded Options**: Keeping default generated marketing text.
  - **Rationale**: Direct systems engineering prose improves clarity, readability, and authority.

## 🌿 Active Branches / Plans
- `main` : Stable production release with complete bilingual landing pages and Zero-Slop test harness.

## 📈 Current Status
- ✅ Done: 21 FastMCP tools implemented, tested (7/7 tests passed), 8-layer pre-commit hook operational, `README.md` & `README.fr.md` fully overhauled, humanized, and isomorphic (475 lines each).
- 🔄 In progress: Session handoff and maintenance readiness.
- ⏳ Pending: Windows Win32 native backend abstraction layer (`WindowBackend`).

## 👉 Next Session Direction
Proceed with multiplatform window management abstraction and extended OS backend integrations.
