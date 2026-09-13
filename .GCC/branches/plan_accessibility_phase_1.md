# Execution Plan: Médiation d'Accessibilité Programmatique via AT-SPI / D-Bus (Issue #130)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: CI 100% PASS (`./ci.sh` : compileall, workflows, ruff check, ruff format, mypy, pytest 100%). Intégrité et robustesse du connecteur AT-SPI en Rust (`linux/crates/atspi_mediator`) et de la couche Python `linux.layers.accessibility`. Zéro régression sur les 65 tests initiaux.
- **Pre-requisites**: Branche `feat/accessibility-mediation-phase-1`. Compilation locale du binaire Rust `linux/crates/atspi_mediator/target/release/gui-agent-atspi` et connectivité D-Bus AT-SPI (`org.a11y.Bus`).

## 🛠️ Step-by-Step Sequence

### Step 1: Création & Compilation du Crate Rust Natif `linux/crates/atspi_mediator`
- [x] **Action**: Implémentation de `linux/crates/atspi_mediator/` avec `Cargo.toml`, `src/lib.rs` et `src/main.rs`. Implémentation des primitives AT-SPI2 / D-Bus (`snapshot_tree`, `perform_action`, `set_element_value`, `list_accessible_apps`, `connect`). Support CLI unifié (`state`, `action`, `value`, `apps`, `doctor`) et serveur MCP stdio JSON-RPC (`mcp`) pour les requêtes distantes. Résolution automatique des index numériques vers `object_ref` et repli sur les actions génériques (`activate`, `click`, `press`, `default`).
- [x] **Verify**: `cargo build --release --manifest-path linux/crates/atspi_mediator/Cargo.toml`
- **Verification Proof**:
```text
   Compiling atspi-mediator v0.1.0 (/home/omni/Code/gui_agent/linux/crates/atspi_mediator)
    Finished `release` profile [optimized] target(s) in 1m 06s
-rwxrwxr-x 2 omni omni 3,0M 12 sept. 02:28 /home/omni/Code/gui_agent/linux/crates/atspi_mediator/target/release/gui-agent-atspi
```

### Step 2: Implémentation & Durcissement de la couche Python `linux/layers/accessibility.py`
- [x] **Action**: Connecteur AT-SPI dans `linux/layers/accessibility.py`. Détection prioritaire du binaire Rust natif compilé localement (`gui-agent-atspi` en release ou debug), extraction d'arbres sémantiques en JSON, cache local de correspondance `_last_node_cache` (`element_index -> object_ref`), priorisation de `element_identifier` pour éviter les échecs de nœuds non trouvés, déclenchement d'actions et mutation de valeurs.
- [x] **Verify**: `./venv/bin/python -c "from linux.layers.accessibility import get_app_state, perform_action; s = get_app_state(app_name='antigravity'); print('State:', s['status'], s['count']); print('Action on 0:', perform_action('0', '0'))"`
- **Verification Proof**:
```text
State: success 2
Action on 0: True
```

### Step 3: Tests Unitaires & Intégration de la Couche Accessibilité
- [x] **Action**: Ajout de 18 tests unitaires dans `linux/tests/test_accessibility.py` et 8 tests unitaires Rust dans `linux/crates/atspi_mediator/src/lib.rs` couvrant : détection du binaire, extraction nominale et filtrée, gestion des timeouts et erreurs subprocess, mocks d'état et de handlers, protocole MCP JSON-RPC, résolution par cache de nœuds (`_last_node_cache`), gestion stricte de `snapshot_id`, sélection déterministe d'action (`select_action_index`), rejet fail-closed des index périmés, et intégration façade `mcp_core`.
- [x] **Verify**: `./venv/bin/pytest linux/tests/test_accessibility.py -v && cargo test --manifest-path linux/crates/atspi_mediator/Cargo.toml`
- **Verification Proof**:
```text
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- /home/omni/Code/gui_agent/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/omni/Code/gui_agent
configfile: pyproject.toml
plugins: anyio-4.13.0
collecting ... collected 18 items

tests/test_accessibility.py::test_find_atspi_mediator_binary PASSED      [  5%]
tests/test_accessibility.py::test_get_app_state_nominal_or_error PASSED  [ 11%]
tests/test_accessibility.py::test_get_app_state_with_screenshot PASSED   [ 16%]
tests/test_accessibility.py::test_get_app_state_mock PASSED              [ 22%]
tests/test_accessibility.py::test_get_app_state_binary_missing PASSED    [ 27%]
tests/test_accessibility.py::test_get_app_state_subprocess_error PASSED  [ 33%]
tests/test_accessibility.py::test_get_app_state_subprocess_timeout PASSED [ 38%]
tests/test_accessibility.py::test_perform_action_mock PASSED             [ 44%]
tests/test_accessibility.py::test_perform_action_binary_missing PASSED   [ 50%]
tests/test_accessibility.py::test_perform_action_mcp_mock_protocol PASSED [ 55%]
tests/test_accessibility.py::test_set_value_mock PASSED                  [ 61%]
tests/test_accessibility.py::test_set_value_binary_missing PASSED        [ 66%]
tests/test_accessibility.py::test_set_value_mcp_mock_protocol PASSED     [ 72%]
tests/test_accessibility.py::test_perform_action_and_set_value_with_node_cache PASSED [ 77%]
tests/test_accessibility.py::test_mcp_core_sdk_facade_integration PASSED [ 83%]
tests/test_accessibility.py::test_get_app_state_invalid_tree_payload PASSED [ 88%]
tests/test_accessibility.py::test_perform_action_and_set_value_with_snapshot_id_mismatch PASSED [ 94%]
tests/test_accessibility.py::test_perform_action_and_set_value_with_missing_cache_index PASSED [100%]

============================== 18 passed in 7.75s ==============================

running 8 tests
test tests::test_select_action_index_ambiguous_rejected ... ok
test tests::test_select_action_index_empty_actions ... ok
test tests::test_select_action_index_exact_match ... ok
test tests::test_select_action_index_numeric_index ... ok
test tests::test_split_object_ref_id_valid ... ok
test tests::test_select_action_index_generic_resolves_primary ... ok
test tests::test_select_action_index_single_action ... ok
test tests::test_split_object_ref_id_invalid ... ok

test result: ok. 8 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

### Step 4: Validation Complète de la Suite CI
- [x] **Action**: Exécution du runner CI local `./ci.sh` pour valider l'ensemble des étapes de qualité (compileall, workflows, linter Ruff, formateur Ruff, typage Mypy strict, suite Pytest 83 tests).
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 216ms      |
| Validation Workflows GitHub Actions        | PASS     | 69ms       |
| Linter de Code (Ruff Check)                | PASS     | 68ms       |
| Formatage de Code (Ruff Format)            | PASS     | 81ms       |
| Typage Statique Strict (Mypy)              | PASS     | 529ms      |
| Suite de Tests Pytest                      | PASS     | 34169ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès !
============================= 83 passed in 33.29s ==============================
```

### Step 5: Durcissement exhaustif suite aux retours de revues (Greptile & CodeRabbit)
- [x] **Action**: Correction complète de l'ensemble des constats :
  1. Résolution du bus AT-SPI dédié (`_get_atspi_bus_address` interrogeant `AT_SPI_BUS_ADDRESS`, `org.a11y.Bus.GetAddress` et `/run/user/<uid>/at-spi/bus_0`).
  2. Durcissement du serveur stdio Rust MCP : interruption de boucle sur EOF/erreur stdin (`break`), liaison stricte des index numériques aux snapshots (`snapshot_token`).
  3. Sécurisation XDG et répertoires d'exécution (`_validate_xdg_env_path` absolu, `_is_secure_runtime_directory` vérifiant UID et mode `0700`).
  4. Isolation du build Cargo dans `linux/install.sh` avec `TARGET_DIR` dédié et validation d'artefact.
  5. Correction de l'interpolation de chemin hatchling dans `hatch_build.py`.
  6. Décalage des coordonnées d'écran virtuel sous KDE spectacle multi-écrans dans `linux/server.py`.
  7. Correction des chemins de test CI dans `.github/workflows/ci.yml` (`linux/tests/`).
  8. Ajout des tests de non-régression (110 tests au total).
- [x] **Verify**: `./ci.sh && cargo check`
- **Verification Proof**:
```text
============================= 110 passed in 33.40s =============================
✔ Validé (35302ms)
```

### Step 6: Résolution finale des 3 constats bloquants Greptile (P1)
- [x] **Action**: Traitement chirurgical et exhaustif :
  1. Transmission directe de `element_identifier` sans `element_index` depuis Python et priorité aux identifiants non-numériques dans Rust `resolve_mcp_target` (suppression de l'erreur "Aucun snapshot actif" sur les processus MCP fraîchement démarrés).
  2. Parsing universel de `_get_atspi_bus_address` acceptant les sorties `busctl` et `dbus-send` avec ou sans guillemets (`s unix:path=...` ou `s "unix:path=..."`).
  3. Confinement strict de `--purge-data` dans `linux/uninstall.sh` au cache approuvé de gui-agent, ignorant les variables d'environnement arbitraires externes.
  4. Nouveaux tests de validation comportementale : 111 tests unitaires et d'intégration validés.
- [x] **Verify**: `./ci.sh && cargo test --all-features && cargo fmt --check`
- **Verification Proof**:
```text
============================= 111 passed in 38.12s =============================
✔ Validé (40012ms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 234ms      |
| Validation Workflows GitHub Actions        | PASS     | 93ms       |
| Linter de Code (Ruff Check)                | PASS     | 22ms       |
| Formatage de Code (Ruff Format)            | PASS     | 21ms       |
| Typage Statique Strict (Mypy)              | PASS     | 554ms      |
| Suite de Tests Pytest                      | PASS     | 40012ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès !
```

### Step 7: Prise en charge sécurisée des répertoires de captures personnalisés lors de la désinstallation (Greptile 5/5)
- [x] **Action**: Mise à jour de `linux/uninstall.sh` pour consulter et purger `GUI_AGENT_SCREENSHOTS_DIR` en plus du cache par défaut, tout en maintenant la protection contre les répertoires système/racines/utilisateurs critiques (`/`, `$HOME`, `/tmp`, `/var`, etc.), la vérification stricte de propriété UID (`-O`), la purge ciblée des captures sans destruction des fichiers tiers dans les dossiers partagés, et l'ajout de tests unitaires dans `linux/tests/test_package.py` (112 tests PASS).
- [x] **Verify**: `./ci.sh && cargo test --all-features`
- **Verification Proof**:
```text
============================= 112 passed in 38.04s =============================
✔ Validé (39766ms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 282ms      |
| Validation Workflows GitHub Actions        | PASS     | 86ms       |
| Linter de Code (Ruff Check)                | PASS     | 23ms       |
| Formatage de Code (Ruff Format)            | PASS     | 20ms       |
| Typage Statique Strict (Mypy)              | PASS     | 631ms      |
| Suite de Tests Pytest                      | PASS     | 39766ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès !
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Saturation CPU / mémoire lors de la compilation de `atspi` et `zbus` sur machine modeste.
- **Mitigation**: Compilation séquentielle contrôlée avec build profile release optimisé (`codegen-units = 1`, `lto = "fat"`, `strip = "symbols"`), exclusion de `target/` de git via `.gitignore` pour préserver la légèreté du dépôt (binaire release 3,0M).
- **Risk**: Absence de bus AT-SPI dans les runners CI ou environnements conteneurisés sans interface graphique.
- **Mitigation**: Détection automatique de la présence du bus AT-SPI (`AT_SPI_BUS_ADDRESS`, `org.a11y.Bus` ou socket `/run/user/<uid>/at-spi/bus_0`). En cas d'indisponibilité du bus ou de l'exécutable Rust, retour gracieux d'un état d'erreur structuré sans crash ni exception non gérée.
- **Risk**: Perte de correspondance entre index numérique et identifiant AT-SPI lors d'appels `perform_action` ou `set_value` consécutifs.
- **Mitigation**: Implémentation du cache mémoire `_last_node_cache` associant chaque `index` à son `object_ref`, injectant automatiquement `element_identifier` auprès du moteur Rust.
