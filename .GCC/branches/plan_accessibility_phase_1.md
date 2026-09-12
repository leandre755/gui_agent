# Execution Plan: Médiation d'Accessibilité Programmatique via AT-SPI / D-Bus (Issue #130)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: CI 100% PASS (`./ci.sh` : compileall, workflows, ruff check, ruff format, mypy, pytest 100%). Intégrité et robustesse du connecteur AT-SPI en Rust (`crates/atspi_mediator`) et de la couche Python `gui_agent.layers.accessibility`. Zéro régression sur les 65 tests initiaux.
- **Pre-requisites**: Branche `feat/accessibility-mediation-phase-1`. Compilation locale du binaire Rust `crates/atspi_mediator/target/release/gui-agent-atspi` et connectivité D-Bus AT-SPI (`org.a11y.Bus`).

## 🛠️ Step-by-Step Sequence

### Step 1: Création & Compilation du Crate Rust Natif `crates/atspi_mediator`
- [x] **Action**: Implémentation de `crates/atspi_mediator/` avec `Cargo.toml`, `src/lib.rs` et `src/main.rs`. Implémentation des primitives AT-SPI2 / D-Bus (`snapshot_tree`, `perform_action`, `set_element_value`, `list_accessible_apps`, `connect`). Support CLI unifié (`state`, `action`, `value`, `apps`, `doctor`) et serveur MCP stdio JSON-RPC (`mcp`) pour les requêtes distantes. Résolution automatique des index numériques vers `object_ref` et repli sur les actions génériques (`activate`, `click`, `press`, `default`).
- [x] **Verify**: `cargo build --release --manifest-path crates/atspi_mediator/Cargo.toml`
- **Verification Proof**:
```text
   Compiling atspi-mediator v0.1.0 (/home/omni/Code/gui_agent/crates/atspi_mediator)
    Finished `release` profile [optimized] target(s) in 1m 06s
-rwxrwxr-x 2 omni omni 3,0M 12 sept. 02:28 /home/omni/Code/gui_agent/crates/atspi_mediator/target/release/gui-agent-atspi
```

### Step 2: Implémentation & Durcissement de la couche Python `gui_agent/layers/accessibility.py`
- [x] **Action**: Connecteur AT-SPI dans `gui_agent/layers/accessibility.py`. Détection prioritaire du binaire Rust natif compilé localement (`gui-agent-atspi` en release ou debug), extraction d'arbres sémantiques en JSON, cache local de correspondance `_last_node_cache` (`element_index -> object_ref`), priorisation de `element_identifier` pour éviter les échecs de nœuds non trouvés, déclenchement d'actions et mutation de valeurs.
- [x] **Verify**: `./venv/bin/python -c "from gui_agent.layers.accessibility import get_app_state, perform_action; s = get_app_state(app_name='antigravity'); print('State:', s['status'], s['count']); print('Action on 0:', perform_action('0', '0'))"`
- **Verification Proof**:
```text
State: success 2
Action on 0: True
```

### Step 3: Tests Unitaires & Intégration de la Couche Accessibilité
- [x] **Action**: Ajout de 15 tests unitaires dans `tests/test_accessibility.py` couvrant : détection du binaire, extraction nominale et filtrée, gestion des timeouts et erreurs subprocess, mocks d'état et de handlers, protocole MCP JSON-RPC, résolution par cache de nœuds (`_last_node_cache`), et intégration façade `mcp_core`.
- [x] **Verify**: `./venv/bin/pytest tests/test_accessibility.py -v`
- **Verification Proof**:
```text
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- /home/omni/Code/gui_agent/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/omni/Code/gui_agent
configfile: pyproject.toml
plugins: anyio-4.13.0
collecting ... collecting 15 items                                                            collected 15 items                                                             

tests/test_accessibility.py::test_find_atspi_mediator_binary PASSED      [  6%]
tests/test_accessibility.py::test_get_app_state_nominal_or_error PASSED  [ 13%]
tests/test_accessibility.py::test_get_app_state_with_screenshot PASSED   [ 20%]
tests/test_accessibility.py::test_get_app_state_mock PASSED              [ 26%]
tests/test_accessibility.py::test_get_app_state_binary_missing PASSED    [ 33%]
tests/test_accessibility.py::test_get_app_state_subprocess_error PASSED  [ 40%]
tests/test_accessibility.py::test_get_app_state_subprocess_timeout PASSED [ 46%]
tests/test_accessibility.py::test_perform_action_mock PASSED             [ 53%]
tests/test_accessibility.py::test_perform_action_binary_missing PASSED   [ 60%]
tests/test_accessibility.py::test_perform_action_mcp_mock_protocol PASSED [ 66%]
tests/test_accessibility.py::test_set_value_mock PASSED                  [ 73%]
tests/test_accessibility.py::test_set_value_binary_missing PASSED        [ 80%]
tests/test_accessibility.py::test_set_value_mcp_mock_protocol PASSED     [ 86%]
tests/test_accessibility.py::test_perform_action_and_set_value_with_node_cache PASSED [ 93%]
tests/test_accessibility.py::test_mcp_core_sdk_facade_integration PASSED [100%]

============================== 15 passed in 7.02s ==============================
```

### Step 4: Validation Complète de la Suite CI
- [x] **Action**: Exécution du runner CI local `./ci.sh` pour valider l'ensemble des étapes de qualité (compileall, workflows, linter Ruff, formateur Ruff, typage Mypy strict, suite Pytest 82 tests).
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 221ms      |
| Validation Workflows GitHub Actions        | PASS     | 89ms       |
| Linter de Code (Ruff Check)                | PASS     | 78ms       |
| Formatage de Code (Ruff Format)            | PASS     | 63ms       |
| Typage Statique Strict (Mypy)              | PASS     | 2106ms     |
| Suite de Tests Pytest                      | PASS     | 31990ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès !
============================= 82 passed in 31.00s ==============================
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Saturation CPU / mémoire lors de la compilation de `atspi` et `zbus` sur machine modeste.
- **Mitigation**: Compilation séquentielle contrôlée avec build profile release optimisé (`codegen-units = 1`, `lto = "fat"`, `strip = "symbols"`), exclusion de `target/` de git via `.gitignore` pour préserver la légèreté du dépôt (binaire release 3,0M).
- **Risk**: Absence de bus AT-SPI dans les runners CI ou environnements conteneurisés sans interface graphique.
- **Mitigation**: Détection automatique de la présence du bus AT-SPI (`AT_SPI_BUS_ADDRESS`, `org.a11y.Bus` ou socket `/run/user/<uid>/at-spi/bus_0`). En cas d'indisponibilité du bus ou de l'exécutable Rust, retour gracieux d'un état d'erreur structuré sans crash ni exception non gérée.
- **Risk**: Perte de correspondance entre index numérique et identifiant AT-SPI lors d'appels `perform_action` ou `set_value` consécutifs.
- **Mitigation**: Implémentation du cache mémoire `_last_node_cache` associant chaque `index` à son `object_ref`, injectant automatiquement `element_identifier` auprès du moteur Rust.
