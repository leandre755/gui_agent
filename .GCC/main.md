# Current Project Context

## 🏆 Major Milestones (Archived Epics)
- [2026-08-14] FastMCP Monolithic Architecture & 21 Desktop Tools Implementation
- [2026-08-14] Multi-Layer Quality & Pre-Commit 8-Layer Zero-Slop Pipeline
- [2026-08-15] Complete README Overhaul: Landing Page UX, Hosted Excalidraw SVGs, Official Transparent Logo & Landscape Hero Banner, Bilingual Line-for-Line Isomorphism (475 lines), and De-AI Humanization Pass
- [2026-08-15] Local CI Runner (`ci.sh`) & Exhaustive Multi-Agent Repository Audit (`organize-repos`)
- [2026-08-16] Parameter `output_path` Migration, Inode Security Hardening & Zero-Slop Rollback (PR #7, Confidence Score 5/5)
- [2026-08-16] Atomic xdotool Chaining & Input Boundaries in `gui_window_resize_move` (PR #8, Confidence Score 5/5 Greptile & CodeRabbit, 27/27 Tests)
- [2026-08-16] Dynamic Issue Template Compliance & Triage Labeling Hardening (PR #16, Confidence Score 5/5 Greptile & CodeRabbit)
- [2026-08-20] Timeouts xdotool sur focus, close et resize_move (PR #50, Confidence Score 5/5 Greptile)
- [2026-08-27] Synchronisation Concurrente et Nettoyage Déterministe de l'Enregistrement Vidéo (PR #57, Confidence Score 5/5 Greptile)
- [2026-08-27] Bornage Déterministe et Deadline Globale pour le Listing X11 (PR #55, Confidence Score 5/5 Greptile)
- [2026-09-12] Modular Architecture Scaffolding, Execution Primitives Hardening & Dependencies Modernization (PR #136, Confidence Score 5/5 Greptile, 0 findings CodeRabbit, 65/65 tests)
- [2026-09-13] Médiation d'Accessibilité Programmatique AT-SPI & Durcissement Purge Uninstall (PR #137, Confidence Score 5/5 Greptile, 12/12 fils CodeRabbit résolus, 112/112 tests)

## 🎯 Objective
High-performance FastMCP server engineered with a decoupled modular architecture (core, layers, utils) for direct, low-latency Computer Use on Linux (X11/XWayland) and Windows desktop environments (<50 MB RAM, 21 tools, zero-leak process lifecycle).

## 🛡️ Protocole de Validation par Pull Request & Critères 5/5 Inviolables
- **Mode de travail exclusif par Pull Request (PR)** : Toute évolution, correctif de sécurité ou refactorisation est développée sur une branche dédiée et soumise via PR.
- **Règle absolue d'évaluation des bots (Optibot, CodeRabbit & Greptile)** :
  - ❌ **NE JAMAIS se baser sur les signaux GitHub Check-Runs de l'API** (`gh api repos/leandre755/gui_agent/commits/<sha>/check-runs`). Dans l'interface GitHub, `conclusion: "success"` signifie uniquement que l'agent de revue a terminé l'exécution de son script d'analyse sans crasher, et NON que le code est validé ou sans erreur.
  - ✅ **EXIGER la lecture textuelle intégrale du message de la PR (description), des bilans et de 100% des commentaires** :
    - **Optibot (`@agent-optibot`)** :
      1. Exiger formellement **0 blocage (`0 blocking issues`)** et **0 constat non résolu**.
      2. Traiter l'intégralité des alertes de sécurité (ex: deny-list des agents), de dette technique ou de documentation.
    - **CodeRabbit (`@coderabbitai`)** :
      1. Inspecter le bilan de revue complet (`Walkthrough`, `Review Summary` et checklist pré-merge).
      2. Résoudre 100% des commentaires actionnables (`Actionable comments: 0` restant, 0 constat).
      3. Obtenir l'approbation formelle sans aucune réserve sur la sécurité, la maintenabilité ou la concurrence.
    - **Greptile (`@greptile-apps`)** :
      1. Inspecter le résumé mis à jour dans le message principal de la PR (`Greptile Summary`).
      2. Exiger formellement un **`Confidence Score: 5/5`** (rejet absolu de tout score 1/5, 2/5, 3/5 ou 4/5).
      3. Vérifier l'absence totale d'échecs de sécurité (`Zero reproduced security failures remaining`).
      4. Traiter tous les commentaires spécifiques de lignes (P1/P2/Security) laissés par le bot avec les artefacts T-Rex de reproduction (0 constat restant).
  - 🛠️ **Outillage d'assistance aux revues** : Utiliser `/greploop` et `/code-review` pour analyser et corriger localement, mais désactiver toute boucle automatique de push/review. Aucun outil ne doit relancer une revue distante sans autorisation explicite.
  - 🚀 **Condition stricte de fusion** : Ce n'est qu'après avoir lu le message de la PR, parcouru tous les commentaires, et obtenu la validation intégrale des 3 moteurs (Optibot, CodeRabbit, Greptile) à **5/5, 0 constat et 0 bloquant** que la fusion (merge) de la PR est autorisée.
- **Protocole anti-gaspillage pour PR #36 et toute future PR** :
  - **Phase 1 — compréhension exhaustive obligatoire** : lire la description complète de la PR, tous les commits de la branche, le diff total contre `main`, tous les commentaires, tous les threads et les derniers bilans des agents avant d'écrire ou de pousser du code.
  - **Phase 2 — implémentation exhaustive** : anticiper les variantes valides du format concerné, corriger la cause racine, ajouter les régressions correspondantes et vérifier les fichiers adjacents impactés. Regrouper tous les findings connus dans une seule passe locale au lieu de corriger un finding isolé puis de relancer une review.
  - **Phase 3 — validation locale complète** : exécuter `./ci.sh`, les tests ciblés, les contrôles statiques, puis TestSprite/Greptile/CodeRabbit CLI si disponibles et authentifiés. La revue locale finale coûte environ **1 $** selon le suivi du projet ; elle doit être lancée au maximum une fois par lot de corrections, avec un prompt couvrant toute la branche contre `main`, pas un seul cas choisi artificiellement.
  - **Phase 4 — revue GitHub parcimonieuse** : un push déclenche une revue Greptile complète de toute la PR et de son historique, contrairement à la revue locale ciblée. Ne pousser qu'après la phase locale complète et une autorisation explicite ; prévoir une seule revue GitHub par lot exhaustif de corrections. La revue distante coûte environ **3 $** par PR/revue selon le suivi du projet et peut épuiser le quota flex mensuel.
  - **Règle d'échec sans boucle** : si une revue locale ou GitHub trouve un bug, ne pas relancer immédiatement l'agent. Lire 100 % du verdict, regrouper tous les constats, corriger localement, puis refaire toute la validation locale. Une nouvelle revue GitHub nécessite un changement réel, une validation locale complète et une autorisation explicite tenant compte du coût/quota.
  - **Portée Greptile à ne jamais confondre** : `greptile review` local analyse le commit/working tree selon le prompt fourni ; Greptile GitHub analyse la PR complète après push. Un score local 5/5 ne prédit donc pas le score GitHub.
  - Après chaque revue GitHub, lire le message principal de la PR, le résumé Greptile complet, le bilan T-Rex et 100 % des commentaires/threads ; ne jamais conclure à partir du seul score ou d'un check-run.
  - **Temporisation d'attente Greptile** : Les revues automatiques Greptile GitHub prennent environ **8 minutes**. Ne jamais régler de timer d'attente court (ex: 30 secondes ou 5 minutes) qui entraîne des boucles de vérification prématurées ou inutiles ; configurer impérativement un délai d'attente de **8 minutes (480 secondes)** avant de relever le verdict Greptile.
  - **Identité de publication de la PR** : La Pull Request doit être créée et finalisée avec le compte GitHub **personal agent**.
  - CodeRabbit distant est déclenché explicitement par un commentaire `@coderabbitai review` uniquement après la validation locale et avec autorisation explicite ; ne pas le relancer si une revue est déjà en cours, rate-limitée ou non nécessaire.
  - Les check-runs seuls ne valent pas validation ; le critère final reste Greptile **5/5**, zéro échec de sécurité, zéro commentaire actionnable et zéro bloquant Optibot/CodeRabbit. La priorité est de réduire le nombre total de reviews, pas de boucler jusqu'à un score parfait.
- **Analyse des vulnérabilités de rollback capture identifiées par Greptile (PR #7)** :
  - *P1 - Réservations en lecture seule non nettoyées* : Si un fichier réservé devient read-only, l'ouverture `O_RDWR` échoue et l'erreur étouffée laisse le fichier sur disque, forçant les retentatives vers des suffixes inutiles `(1)`. Solution : ouvrir d'abord en `O_RDONLY` pour vérifier l'identité et ne tronquer que si accessible en écriture.
  - *P1 - Course TOCTOU lors de la suppression par chemin* : La séquence `os.stat()` puis `os.unlink(filename, dir_fd)` permet à un attaquant de remplacer l'entrée entre les deux appels et d'entraîner la suppression de son fichier tiers. Solution : bannir la suppression destructive basée sur le nom dans un répertoire concurrent ; retenir le descripteur ouvert de la réservation à l'écriture, ou s'abstenir de tout `unlink` non lié de manière exclusive.

## 🧠 Decisions Made
- [2026-09-12] Bundle Unique Natif par Système d'Exploitation (Rust + REPL PyO3)
  - **Context**: Besoin de livrer un artefact directement exécutable par OS (`gui-agent` sous Linux, `gui-agent.exe` sous Windows, `gui-agent` sous macOS), compilable directement sur la machine hôte via Cargo sans surcoût d'environnement virtuel Python ni fragmentation multi-processus.
  - **Discarded Options**: Bundle Python auto-extractible via PyInstaller/Nuitka (>150 Mo, latence au démarrage, décompression) ; distribution multi-binaires fragmentée (FastMCP Python appelant des sous-processus séparés).
  - **Rationale**: Un binaire autonome Rust garantit une latence quasi-nulle (<5 ms), une consommation mémoire minime (<15 Mo), une compilation locale unifiée (`cargo build --release`), une étanchéité par plateforme via des crates dédiés (`linux/crates/`, `windows/crates/`), et une intégration native du REPL CodeAct (`execute_script`) via PyO3.
- [2026-09-12] Durcissement de la Résolution d'Index, Livraison Native et Sélection Déterministe d'Actions (Phase 1 #130)
  - **Context**: Retours de revue Greptile et CodeRabbit : repli arbitraire sur l'index 1 dans `select_action_index`, maintien de l'exécution sur index périmés sans snapshot actif ou sur cache absent, et omission de la compilation/installation de `gui-agent-atspi` dans le workflow `install.sh`.
  - **Discarded Options**: Tolérer un repli permissif sur une action arbitraire ; ignorer l'invalidation de cache et relancer un snapshot non filtré en tâche de fond ; exiger l'installation manuelle d'outils tiers.
  - **Rationale**: Rejet fail-closed strict (return False) de tout index numérique non résolu dans `_last_node_cache` ou sur snapshot mismatch ; sélection d'action déterministe (exacte, numérique, sous-chaîne unique, synonymes sémantiques ou rejet avec listing des actions disponibles) ; build et installation automatique de `gui-agent-atspi` dans `install.sh` ; création du workspace `Cargo.toml` racine activant la détection CI native.
- [2026-09-12] Médiation d'Accessibilité Programmatique via Moteur Natif Rust AT-SPI / D-Bus (Phase 1 #130)
  - **Context**: L'accès à l'interface graphique Linux par perception visuelle seule (captures d'écran et OCR) souffre de cécité sémantique (menus contextuels éphémères, scaling HiDPI, dialogues modaux bloquants). L'accès direct à AT-SPI2 via D-Bus (`org.a11y.Bus`) est requis avec une latence d'extraction minimale (< 50 ms).
  - **Discarded Options**: Bibliothèque Python `pyatspi` (obsolète, fuites mémoire et dépendances C non isolées) ; binding C pur / ctypes ; réécriture complète du serveur MCP en Rust (rupture de compatibilité avec l'écosystème FastMCP Python existant).
  - **Rationale**: Moteur autonome bivalent écrit en Rust (`linux/crates/atspi_mediator` produisant le binaire release autonome `gui-agent-atspi` de 3,0M épuré) exploitant `atspi` et `zbus`, avec support CLI et mode serveur stdio JSON-RPC MCP (`initialize`, `tools/call`), interfacé depuis Python via `linux/layers/accessibility.py` avec mise en cache synchronisée par verrou (`_cache_lock`) des index vers `object_ref`, communication par flux process borné avec timeouts stricts et mocks complets pour CI headless.
- [2026-09-11] Architecture Modulaire Découplée (core, layers, utils #129)
  - **Context**: Monolithe historique couplant REPL, gestion PTY, drivers bas niveau et helpers.
  - **Discarded Options**: Monolithe persistant ; micro-paquets distribués séparément.
  - **Rationale**: Découpage en 3 sous-packages (core: REPL/PTY/SDK, layers: accessibilité/fenêtres/entrées/OCR, utils: géométrie/vidéo/cinématique) garantissant isolation et testabilité unitaire sans régression.
- [2026-08-28] Support Bivalent Multi-Versions SDK MCP (1.x et 2.x+)
  - **Context**: Dependabot et les environnements clients récents migrent vers `mcp>=2.0.0`. Le test unitaire `test_fastmcp_tools_registration` dépendait d'attributs privés fragiles (`_tool_manager`), et `gui_agent/server.py` restreignait explicitement la compatibilité à la version 1.x.
  - **Discarded Options**: Bloquer strictement sur `mcp<2.0.0` (empêche les montées de versions et mises à jour de sécurité de Dependabot) ; réécrire l'intégralité du serveur en MCP bas niveau (complexe et inutile car FastMCP est préservé en v2).
  - **Rationale**: Élargissement de la contrainte de dépendance à `"mcp>=1.2.0,<3.0.0"`, abstraction défensive de l'introspection des outils enregistrés dans `tests/test_package.py` avec replis successifs (`_tool_manager`, `_tools`, `list_tools()` ou inspection du namespace), et neutralisation du message d'erreur d'import dans `gui_agent/server.py`. 100% de la suite de tests validée (64/64 PASS).
- [2026-08-27] Bornage Déterministe et Deadline Globale pour le Listing X11 (PR #55)
  - **Context**: Dans `gui_window_list`, lorsque `wmctrl` ne renvoie aucune fenêtre, le mode fallback interrogeait chaque fenêtre visible séquentiellement via `getwindowname`, `getwindowpid` et `xprop` avec des timeouts indépendants de 5s sans deadline globale, cumulant jusqu'à 15s par fenêtre non réactive.
  - **Discarded Options**: Conserver des timeouts indépendants par commande sans horloge globale ; paralléliser avec des threads sans deadline stricte ; supprimer le fallback.
  - **Rationale**: Définition d'une deadline globale (`deadline = time.monotonic() + 5.0`) pour l'ensemble de la fonction `gui_window_list`. Chaque sous-processus reçoit comme timeout le temps résiduel effectif `max(0.1, deadline - time.monotonic())`. La boucle de collecte s'interrompt immédiatement dès l'épuisement de la deadline, garantissant que l'opération totale ne dépasse jamais le budget temporel imparti. Ajout d'un test de non-régression validé par `./ci.sh` (64/64 tests).
- [2026-08-27] Synchronisation Concurrente et Nettoyage Déterministe de l'Enregistrement Vidéo (PR #57)
  - **Context**: L'enregistrement vidéo (`gui_start_video_recording` et `gui_stop_video_recording`) manipulait des variables d'état globales (`_video_recording_process`, `_video_recording_file`) sans verrou, exposant le serveur FastMCP à des conditions de concurrence lors d'appels simultanés, et risquait de laisser des descripteurs de fichiers (`stdin`, `stdout`, `stderr`) ou des processus ffmpeg orphelins lors d'échecs au démarrage.
  - **Discarded Options**: Utiliser un `multiprocessing.Lock` ou IPC (inutile car le serveur FastMCP fonctionne au sein d'un seul processus Python multi-threadé) ; laisser l'état sans synchronisation ; faire confiance au garbage collector pour fermer les flux de descripteurs.
  - **Rationale**: Introduction d'un verrou `threading.Lock()` (`_video_recording_lock`) sérialisant tous les points d'entrée d'enregistrement vidéo. Modularisation via les helpers `_validate_video_recording_params` et `_close_subprocess_streams`. Enregistrement d'un hook `atexit.register(_cleanup_video_on_exit)` pour garantir la terminaison propre de tout processus ffmpeg résiduel. Validation stricte de `output_path` (normalisation absolue, interdiction de répertoires, extension `.mp4` obligatoire) et validation stricte de `fps`, `monitor_index >= 0`, et `duration > 0`. Ajout d'une suite exhaustive de tests unitaires et de concurrence (63 tests validés à 100% dans `./ci.sh`).
- [2026-08-17] Validation finale locale de la PR #36 après corrections Greptile
  - **Context**: Le parseur texte de `.github/scripts/verify_workflows.py` a nécessité plusieurs corrections pour couvrir les ancres YAML directes, scalaires, flow, multilignes, alias imbriqués et mappings `concurrency`.
  - **Discarded Options**: Pousser après chaque finding ; relancer Greptile sans lire le retour précédent ; ajouter des regex isolées sans test de reproduction.
  - **Rationale**: Les findings ont été reproduits localement, corrigés par tests comportementaux, validés par `./ci.sh` et quality gate, puis revus sans push. Le commit local `27c4380` obtient Greptile **5/5**, sans blocage ni commentaire.
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
- `docs/readme-how-it-works-update` : Mise à jour des README (EN & FR) et génération des nouveaux diagrammes d'architecture Excalidraw (Architecture v1.0) [plan_readme_maj.md](.GCC/branches/plan_readme_maj.md)
- `main` : Production release with multi-platform decoupled architecture (`linux/`, `windows/`, `macos/`), native Rust AT-SPI mediator, dynamic XDG path resolution, bilingual landing pages, 112/112 Zero-Slop test harness, and thread-safe video recording.

## 📈 Current Status
- ✅ Done:
  - Suppression définitive des 8 issues obsolètes (#3, #4, #5, #9, #12, #28, #30, #48).
  - Création des 7 issues d'architecture v1.0 (#129 à #135) couvrant l'arborescence, les phases 1-4 et la recherche d'équivalents Windows/macOS.
  - Fusion de la PR #136 (`refactor/modular-architecture-issue-129`, Closes #129) avec Confidence Score 5/5 sur Greptile et 0 findings CodeRabbit (65/65 tests validés).
  - Implémentation et durcissement complets de la Phase 1 (#130) : Médiation d'accessibilité programmatique via AT-SPI / D-Bus (moteur natif Rust `linux/crates/atspi_mediator` produisant `gui-agent-atspi`, couche Python `linux/layers/accessibility.py`, 112/112 tests CI validés au dernier `./ci.sh`).
  - Fermeture de la PR obsolète #112 (traitement de la sécurité subprocess #44 transféré à l'Issue #132).
  - Fusion des PRs précédentes (#7, #8, #16, #35, #50, #57, #55).
  - Fermeture des issues résolues (#42, #56, #69, #106, #70, #68, #63, #59, #46, #45, #13, #107, #43).
  - Nettoyage et suppression de l'ensemble des branches résiduelles distantes et locales.
  - Restructuration étanche par système d'exploitation (`linux/`, `windows/`, `macos/`), migration de `tests/` et `examples/` dans `linux/`, zéro code/test/cache à la racine.
  - Durcissement exhaustif de `.gitignore` et purge des caches résiduels (1,5 Go de target crate et __pycache__).
  - Alignement du workspace Cargo racine (`Cargo.toml`) sur `linux/crates/atspi_mediator` validé par `cargo check`.
  - Décision d'architecture actée : Bundle Unique Natif par OS en Rust (avec REPL PyO3 embarqué) directement exécutable et compilable sur l'hôte.
  - Validation CI 112/112 tests PASS, Mypy strict (36 fichiers), Bandit, Semgrep et quality gate pre-commit PASS sur la branche `feat/accessibility-mediation-phase-1`.
  - Application intégrale et exhaustive des retours de revue Greptile et CodeRabbit : transmission directe d'identifiant résolu et priorité dans le médiateur MCP Rust, parsing universel de l'adresse de bus AT-SPI (formats bruts/cités busctl et dbus-send), prise en charge sécurisée des répertoires de captures personnalisés (`GUI_AGENT_SCREENSHOTS_DIR`) avec protection stricte des racines système/utilisateurs, vérification de propriété UID, restriction chirurgicale aux motifs applicatifs authentiques (timestamps numériques et UUID stricts), et préservation à 100% des fichiers médias tiers plausibles (`video_projet.mp4`, `recording_interview.mp4`, `screenshot_final.png`).
  - Validation et certification officielle de la Pull Request [#137](https://github.com/leandre755/gui_agent/pull/137) : **Confidence Score: 5/5 sur Greptile**, **0 commentaire ajouté**, verdict *Safe to merge*, **12/12 fils CodeRabbit résolus** et fusion dans `main` (commit `7a49514`).
  - Validation CI complète : 112/112 tests PASS, Mypy strict (36 fichiers), Bandit, Semgrep, Rust clippy/test/fmt et quality gate pre-commit PASS.
  - Conception et génération des nouveaux diagrammes vectoriels Excalidraw (`how-it-works-en.excalidraw`, `how-it-works-fr.excalidraw`, SVG/PNG dans `assets/`, hébergement GitHub Gist public `f0b933b981a70de123282eb99fd6df44`).
  - Refonte intégrale et isomorphe de `README.md` et `README.fr.md` (485 lignes strictes, 0 emoji Unicode dans les en-têtes, 0 mention d'historique de version, intégration des 2 Piliers, de la médiation Rust AT-SPI2, des chemins dynamiques XDG et de la préservation vidéo).
- 🔄 In progress: Revue et publication de la branche `docs/readme-how-it-works-update`.
- ⏳ Pending:
  - 2. **Phase 2 (#131)** : Moteur d'exécution local CodeAct et SDK unifié `mcp_core` (`core/repl.py`).
  - 3. **Phase 3 (#132)** : Émulation d'entrées noyau (`uinput/evdev`), perception visuelle (`RapidOCR`) et gestion de fenêtrage (`process_run` sécurisé).
  - 4. **Phase 4 (#133)** : Déclaration FastMCP des 13 outils chirurgicaux, suppression des redondances et mise à jour CI.
  - 5. **Recherche OS tiers (#134, #135)** : Adaptation Windows (UI Automation) et macOS (NSAccessibility).

## 👉 Next Session Direction
Soumettre la Pull Request pour `docs/readme-how-it-works-update` sous le compte `personnal-agent` ou initier la Phase 2 (Issue #131 : Moteur REPL CodeAct).
