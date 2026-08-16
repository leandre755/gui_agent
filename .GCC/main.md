# Current Project Context

## 🏆 Major Milestones (Archived Epics)
- [2026-08-14] FastMCP Monolithic Architecture & 21 Desktop Tools Implementation
- [2026-08-14] Multi-Layer Quality & Pre-Commit 8-Layer Zero-Slop Pipeline
- [2026-08-15] Complete README Overhaul: Landing Page UX, Hosted Excalidraw SVGs, Official Transparent Logo & Landscape Hero Banner, Bilingual Line-for-Line Isomorphism (475 lines), and De-AI Humanization Pass
- [2026-08-15] Local CI Runner (`ci.sh`) & Exhaustive Multi-Agent Repository Audit (`organize-repos`)
- [2026-08-16] Parameter `output_path` Migration, Inode Security Hardening & Zero-Slop Rollback (PR #7, Confidence Score 5/5)
- [2026-08-16] Atomic xdotool Chaining & Input Boundaries in `gui_window_resize_move` (PR #8, Confidence Score 5/5 Greptile & CodeRabbit, 27/27 Tests)
- [2026-08-16] Dynamic Issue Template Compliance & Triage Labeling Hardening (PR #16, Confidence Score 5/5 Greptile & CodeRabbit)

## 🎯 Objective
High-performance, monolithic FastMCP server engineered for direct, low-latency Computer Use on Linux (X11/XWayland) and Windows desktop environments (<50 MB RAM, 21 tools, zero-leak process lifecycle).

## 🛡️ Protocole de Validation par Pull Request & Critères 5/5 Inviolables
- **Mode de travail exclusif par Pull Request (PR)** : Toute évolution, correctif de sécurité ou refactorisation est développée sur une branche dédiée et soumise via PR.
- **Règle absolue d'évaluation des bots (Optibot, CodeRabbit & Greptile)** :
  - ❌ **NE JAMAIS se baser sur les signaux GitHub Check-Runs de l'API** (`gh api repos/leandre755/gui_agent/commits/<sha>/check-runs`). Dans l'interface GitHub, `conclusion: "success"` signifie uniquement que l'agent de revue a terminé l'exécution de son script d'analyse sans crasher, et NON que le code est validé ou sans erreur.
  - ✅ **EXIGER la lecture textuelle intégrale du message de la PR (description), des bilans et de 100% des commentaires** :
    - **Optibot (`@agent-optibot`)** :
      1. Inspecter le bilan et le statut de la revue (`Status: Code Looks Good 👍`).
      2. Exiger formellement **0 blocage (`0 blocking issues`)** et **0 constat non résolu**.
      3. Traiter l'intégralité des alertes de sécurité (ex: deny-list des agents), de dette technique ou de documentation.
    - **CodeRabbit (`@coderabbitai`)** :
      1. Inspecter le bilan de revue complet (`Walkthrough`, `Review Summary` et checklist pré-merge).
      2. Résoudre 100% des commentaires actionnables (`Actionable comments: 0` restant, 0 constat).
      3. Obtenir l'approbation formelle sans aucune réserve sur la sécurité, la maintenabilité ou la concurrence.
    - **Greptile (`@greptile-apps`)** :
      1. Inspecter le résumé mis à jour dans le message principal de la PR (`Greptile Summary`).
      2. Exiger formellement un **`Confidence Score: 5/5`** (rejet absolu de tout score 1/5, 2/5, 3/5 ou 4/5).
      3. Vérifier l'absence totale d'échecs de sécurité (`Zero reproduced security failures remaining`).
      4. Traiter tous les commentaires spécifiques de lignes (P1/P2/Security) laissés par le bot avec les artefacts T-Rex de reproduction (0 constat restant).
  - 🛠️ **Outillage d'assistance aux revues** : Utiliser proactivement les skills `/greploop` et `/code-review` (CodeRabbit) pour automatiser l'analyse, l'application des correctifs et les cycles itératifs jusqu'à l'obtention du score parfait 5/5.
  - 🚀 **Condition stricte de fusion** : Ce n'est qu'après avoir lu le message de la PR, parcouru tous les commentaires, et obtenu la validation intégrale des 3 moteurs (Optibot, CodeRabbit, Greptile) à **5/5, 0 constat et 0 bloquant** que la fusion (merge) de la PR est autorisée.
- **Analyse des vulnérabilités de rollback capture identifiées par Greptile (PR #7)** :
  - *P1 - Réservations en lecture seule non nettoyées* : Si un fichier réservé devient read-only, l'ouverture `O_RDWR` échoue et l'erreur étouffée laisse le fichier sur disque, forçant les retentatives vers des suffixes inutiles `(1)`. Solution : ouvrir d'abord en `O_RDONLY` pour vérifier l'identité et ne tronquer que si accessible en écriture.
  - *P1 - Course TOCTOU lors de la suppression par chemin* : La séquence `os.stat()` puis `os.unlink(filename, dir_fd)` permet à un attaquant de remplacer l'entrée entre les deux appels et d'entraîner la suppression de son fichier tiers. Solution : bannir la suppression destructive basée sur le nom dans un répertoire concurrent ; retenir le descripteur ouvert de la réservation à l'écriture, ou s'abstenir de tout `unlink` non lié de manière exclusive.

## 🧠 Decisions Made
- [2026-08-16] Synchronisation Exhaustive des Chemins Protégés de Gouvernance, Permissions Agent et CI (PR #35)
  - **Context**: La PR #35 a initialement mis à jour `governance.yml`. Les revues automatisées (CodeRabbit, Greptile, Agent-Optibot) ont détecté un désalignement avec `.github/PULL_REQUEST_TEMPLATE.md`, `.agents/settings.json`, `.github/CODEOWNERS` et l'omission de `ci.sh`.
  - **Discarded Options**: Corriger uniquement `governance.yml` en ignorant le template PR et les règles de permissions locales ; maintenir `ci.sh` non protégé en gouvernance.
  - **Rationale**: Traitement holistique de la frontière d'automatisation : synchronisation rigoureuse de 100% des fichiers (`governance.yml`, `PULL_REQUEST_TEMPLATE.md`, `.agents/settings.json`, `CODEOWNERS`) incluant `.githooks/*`, `install.*`, `uninstall.*`, `.coding-stuff/*` et `ci.sh` pour obtenir un accord parfait entre détection, checklist déclarative, permissions agents et score 5/5.
- [2026-08-16] Chaînage de commandes `xdotool` dans `gui_window_resize_move` (PR #8)
  - **Context**: L'exécution de deux appels `subprocess.run` séparés (`windowsize` puis `windowmove`) créait un état intermédiaire et un surcoût de processus.
  - **Discarded Options**: Conserver deux appels distincts ; exécuter via un script shell intermédiaire.
  - **Rationale**: Une commande xdotool unique chaînée regroupe les arguments dans une seule invocation, supprime le surcoût de démarrage de processus et réduit la fenêtre de course tout en maintenant la compatibilité sur l'ensemble des gestionnaires de fenêtres X11.
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
- `fix/ci-verify-workflows-logic` : Enrichissement de `verify_workflows.py` pour valider la logique métier et les invariants de sécurité des workflows GitHub Actions ([plan_verify_workflows_logic.md](branches/plan_verify_workflows_logic.md)).
- `main` : Stable production release with complete bilingual landing pages, 27/27 Zero-Slop test harness, hardened screenshot rollback lifecycle and atomic window resize/move chaining.
- `organize_repo` : Plan de réorganisation et harmonisation gouvernance/CI ([plan_organize_repo.md](branches/plan_organize_repo.md)) — *En attente de revue utilisateur*.

## 📈 Current Status
- ✅ Done:
  - Fusion de la PR #7 (`fix/screenshot-output-path-param`) avec Confidence Score 5/5 sur Greptile et CodeRabbit.
  - Fusion de la PR #8 (`fix/atomic-window-resize-move`) avec Confidence Score 5/5 sur Greptile et CodeRabbit (27/27 tests validés).
  - Fusion de la PR #16 (`fix/issue-triage-template-compliance`) avec Confidence Score 5/5 sur Greptile et CodeRabbit.
  - Fusion de la PR #35 (`fix/governance-workflows-paths`) avec Confidence Score 5/5 sur Greptile et CodeRabbit.
  - Résolution de l'issue #26 via la **PR #36** (`fix/ci-verify-workflows-logic`) avec Confidence Score 5/5 Greptile & 0 commentaire restant (37/37 tests validés).
- 🔄 In progress: Validation finale et merge de la PR #36.
- ⏳ Pending:
  - 1. **Assainissement Gouvernance/CI/Hooks** : Traiter #32 (fallback silencieux pip dev), #33 (matrice Python 3.10-3.13), #34 (épinglage versions uv run) et #24 (Mypy strict).
  - 2. **Refactoring Arborescence (#30)** : Migrer vers `src/gui_agent/` selon le plan `plan_organize_repo.md`.
  - 3. **Tests Comportementaux (#28)** : Mettre en place la suite modulaire pour les 19 outils restants.
  - 4. **Bugs Fonctionnels & Prérequis (#31, #18, #17, #19, #20, #21, #13)** : Correction séquentielle TDD et ajout `python3-tk`.
  - 5. **Documentation (#29, #14, #15)** : Déploiement de `/documentation` modulaire.

## 👉 Next Session Direction
Surveiller les analyses de la PR #35 jusqu'à l'obtention des validations CodeRabbit / Greptile (score 5/5).
