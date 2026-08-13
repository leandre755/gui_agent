# Execution Plan: Test des 21 outils MCP GUI par 21 Sous-Agents Séquentiels

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Chaque outil MCP GUI est testé isolément par un sous-agent dédié. Chaque sous-agent rapporte le résultat exact du test dans le journal global avant de terminer. La mémoire système est maintenue stable (< 4 Go RAM utilisée).
- **Pre-requisites**: Serveur `mcp_gui_server.py` et environnement virtuel Python opérationnels (`./venv/bin/python`).

## 🛠️ Step-by-Step Sequence

### Phase 1 : Informatique & Fenêtres (Subagents 1 à 6)
- [ ] **Step 1**: Subagent 01 - Test `gui_get_screen_info`
- [x] **Step 2**: Subagent 02 - Test `gui_take_screenshot`
  - **Verification Proof**:
  ```json
  {
    "status": "success",
    "screenshot_path": "/home/omni/Code/gui_agent/screenshots/screenshot_1786631107.png",
    "raw_path": "/home/omni/Code/gui_agent/screenshots/raw_screenshot_1786631107.png",
    "width": 1366,
    "height": 768,
    "monitor_index": 1,
    "cropped": false,
    "format": "png",
    "grid_applied": true,
    "grid_interval": 100,
    "message": "Capture d'écran générée avec succès."
  }
  ```
- [ ] **Step 3**: Subagent 03 - Test `gui_window_list`
- [ ] **Step 4**: Subagent 04 - Test `gui_app_launch` (`xclock` / `kcalc`)
- [ ] **Step 5**: Subagent 05 - Test `gui_window_focus`
- [ ] **Step 6**: Subagent 06 - Test `gui_window_resize_move`

### Phase 2 : Enregistrement & Souris/Clavier (Subagents 7 à 13)
- [ ] **Step 7**: Subagent 07 - Test `gui_start_video_recording`
- [ ] **Step 8**: Subagent 08 - Test `gui_mouse_move`
- [ ] **Step 9**: Subagent 09 - Test `gui_mouse_click`
- [ ] **Step 10**: Subagent 10 - Test `gui_clipboard_set`
- [ ] **Step 11**: Subagent 11 - Test `gui_clipboard_get`
- [x] **Step 12**: Subagent 12 - Test `gui_keyboard_type`
  - **Verification Proof**:
  ```json
  {
    "status": "success",
    "action": "Texte tapé de façon humaine : 'Hello Subagent 12'"
  }
  ```
- [x] **Step 13**: Subagent 13 - Test `gui_keyboard_press`
  - **Verification Proof**:
  ```json
  {
    "status": "success",
    "action": "Appui clavier indifférenciable effectué pour 'Return'"
  }
  ```

### Phase 3 : Vision, Web & Finalisation (Subagents 14 à 21)
- [ ] **Step 14**: Subagent 14 - Test `gui_find_text`
- [ ] **Step 15**: Subagent 15 - Test `gui_click_text`
- [ ] **Step 16**: Subagent 16 - Test `gui_find_template`
- [ ] **Step 17**: Subagent 17 - Test `gui_mouse_drag`
- [ ] **Step 18**: Subagent 18 - Test `gui_mouse_scroll`
- [ ] **Step 19**: Subagent 19 - Test `gui_web_action`
- [ ] **Step 20**: Subagent 20 - Test `gui_stop_video_recording`
- [x] **Step 21**: Subagent 21 - Test `gui_window_close`
  - **Verification Proof**:
  ```json
  {
    "status": "success",
    "message": "Fenêtre 83886093 fermée avec succès."
  }
  ```

## ⚠️ Mitigations & Edge Cases
- **Risque**: Embouteillage de sous-agents ou fuite mémoire sur le CPU i5.
- **Mitigation**: Exécution 100% séquentielle (1 sous-agent lancé à la fois), libération mémoire à la fin de chaque sous-agent.
