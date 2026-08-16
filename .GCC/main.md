# Current Project Context

## 🏆 Major Milestones (Archived Epics)
- [2026-08-14] FastMCP Monolithic Architecture & 21 Desktop Tools Implementation
- [2026-08-14] Multi-Layer Quality & Pre-Commit 8-Layer Zero-Slop Pipeline
- [2026-08-15] Complete README Overhaul: Landing Page UX, Hosted Excalidraw SVGs, Official Transparent Logo & Landscape Hero Banner, Bilingual Line-for-Line Isomorphism (475 lines), and De-AI Humanization Pass
- [2026-08-15] Local CI Runner (`ci.sh`) & Exhaustive Multi-Agent Repository Audit (`organize-repos`)

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
- [2026-08-15] Remplacement de `save_to_artifacts` par `output_path`, Réservation Atomique, Inode Verification et Rollback sur Échec (PR #7)
  - **Context**: `save_to_artifacts` était un vestige mort non lu. `output_path` permet d'enregistrer les captures à n'importe quel emplacement.
  - **Discarded Options**: Conserver le flag mort ; écraser les fichiers existants sans contrôle ; accepter des extensions contradictoires (ex: JPEG sauvé en .png) ; laisser des fichiers vides réservés après un échec d'écriture ; écraser ou supprimer aveuglément des chemins substitués par un tiers.
  - **Rationale**: Rejet strict des incohérences format/extension, réservation atomique par `os.O_CREAT | os.O_EXCL`, protection des fichiers existants par renommage incrémental `(1)`, `(2)`, vérification stricte de l'inode `(st_dev, st_ino)` avant écriture ou copie, rejet des répertoires, normalisation absolue des chemins et nettoyage garanti (rollback sécurisé par inode) des fichiers réservés en cas d'erreur de sauvegarde.
- [2026-08-15] Préservation Intégrale de `git_credential.json` et Coexistence `CLAUDE.md` / `AGENTS.md`
  - **Context**: `git_credential.json` est strictement local et exclu de Git ; `CLAUDE.md` et `AGENTS.md` desservent des écosystèmes clients distincts (Claude Code CLI vs assistants standards).
  - **Discarded Options**: Suppression du fichier d'identifiants ; déduplication/suppression de `CLAUDE.md`.
  - **Rationale**: Respect strict des contraintes utilisateur et interopérabilité immédiate entre outils sans rupture de contexte.
- [2026-08-15] Maintien de l'Arborescence Actuelle pour Validation de l'Audit Utilisateur
  - **Context**: L'utilisateur dispose d'un rapport d'audit en cours d'évaluation.
  - **Discarded Options**: Application immédiate de déplacements destructifs dans `tests/` et `examples/`.
  - **Rationale**: Geler la structure jusqu'à la revue utilisateur afin de ne pas invalider les chemins de son audit, et reporter les corrections futures dans l'audit.

## 🌿 Active Branches / Plans
- `main` : Stable production release with complete bilingual landing pages and Zero-Slop test harness.
- `fix/screenshot-output-path-param` (PR #7) : Remplacement de `save_to_artifacts` par `output_path`, validation d'extensions, protection anti-écrasement et normalisation absolue des chemins de capture — *Validé CI (8/8 tests) & CodeRabbit*.
- `organize_repo` : Plan de réorganisation et harmonisation gouvernance/CI ([plan_organize_repo.md](file:///home/omni/Code/gui_agent/.GCC/branches/plan_organize_repo.md)) — *En attente de revue utilisateur*.

## 📈 Current Status
- ✅ Done: Correctif `output_path` pour `gui_take_screenshot` implémenté, documenté et testé (PR #7 ouverte et poussée avec résolution des remarques CodeRabbit) ; Script `ci.sh` opérationnel (5/5 étapes validées) ; 8/8 tests Pytest passés sous Xvfb.
- 🔄 In progress: Gel temporaire de la structure à la demande de l'utilisateur pour préserver la validité de son audit et traitement point par point des retours.
- ⏳ Pending: Reprise des points suivants de l'audit de l'utilisateur lors de la prochaine session.

## 👉 Next Session Direction
Poursuivre la correction des points relevés dans l'audit utilisateur (sur la base de la PR #7 ou de la branche de travail convenue) en appliquant le protocole de vérification irréfutable et en maintenant la structure du dépôt alignée.
