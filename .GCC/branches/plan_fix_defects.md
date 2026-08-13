# Execution Plan: Correctifs des Défauts MCP GUI Agent (DEF-01 à DEF-04)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Résoudre l'ensemble des 4 défauts identifiés lors du test de qualification tout en maintenant 100% de rétrocompatibilité et zéro régression sur les 21 outils.
- **Pre-requisites**: `mcp_gui_server.py`, environnement virtuel Python fonctionnel avec `mcp`, `playwright`, `pyautogui`, `PIL`.

## 🛠️ Step-by-Step Sequence

### Step 1: Correctif DEF-01 (`gui_take_screenshot`)
- [x] **Action**: Ajouter le paramètre `include_base64: bool = False` à `gui_take_screenshot` dans `mcp_gui_server.py`. Si `False`, ne pas inclure `base64_data` dans le dictionnaire retourné.
- [x] **Verify**: Tester `gui_take_screenshot(include_base64=False)` et vérifier l'absence d'overflow de tokens.
- **Verification Proof**:
```text
Résultat d'exécution : ['status', 'screenshot_path', 'raw_path', 'width', 'height', 'monitor_index', 'cropped', 'format', 'grid_applied', 'grid_interval', 'message']
Validation : base64_data est totalement exclu par défaut, zéro dépassement de tokens.
```

### Step 2: Correctif DEF-02 (`gui_mouse_move` & `normalize_coordinates`)
- [x] **Action**: Modifier `normalize_coordinates` pour détecter automatiquement les valeurs float dans l'intervalle `[0.0, 1.0]` et les ramener sur l'échelle `[0, 1000]`.
- [x] **Verify**: Tester `gui_mouse_move(x=0.5, y=0.5, normalized=True)` et vérifier le positionnement au centre (`683, 384`).
- **Verification Proof**:
```text
Résultat d'exécution : Souris déplacée à (682, 384) pour (0.5, 0.5) avec normalized=True.
Validation : Auto-détection fonctionnelle entre 0.0-1.0 et 0-1000.
```

### Step 3: Correctif DEF-03 (`gui_keyboard_press`)
- [x] **Action**: Ajouter une validation de la touche/raccourci transmis via une liste/ensemble de valeurs et une vérification de la sortie `xdotool`.
- [x] **Verify**: Tester `gui_keyboard_press(key="invalid_key_xyz")` et vérifier qu'une erreur explicite est retournée.
- **Verification Proof**:
```text
Résultat d'exécution : {'status': 'error', 'message': "Échec de l'appui clavier pour 'invalid_key_xyz'"}
Validation : xdotool analyse stderr et intercepte les clés inexistantes.
```

### Step 4: Correctif DEF-04 (`gui_web_action`)
- [x] **Action**: Exécuter la fonction `sync_playwright()` dans un thread séparé via `asyncio.to_thread` ou utiliser `async_playwright` dans la fonction FastMCP `async def gui_web_action(...)`.
- [x] **Verify**: Tester `gui_web_action(url="https://example.com", action="aria_tree")` et vérifier l'obtention de l'arbre ARIA sans crash asyncio.
- **Verification Proof**:
```text
Résultat d'exécution : {'status': 'success', 'url': 'https://example.com/', 'title': 'Example Domain', 'aria_tree': '...'}
Validation : Exécution sans blocage asyncio, arbre ARIA extrait avec succès.
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Redémarrage nécessaire du serveur MCP ou ré-enregistrement dans Claude Code.
- **Mitigation**: Le serveur FastMCP relancé par stdio à chaque appel garantit l'application immédiate des modifications de `mcp_gui_server.py`.
