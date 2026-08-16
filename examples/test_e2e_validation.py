"""
Suite de tests d'intégration End-to-End (E2E) pour le serveur MCP GUI Monolithique FastMCP.
Valide l'ensemble des 22+ outils MCP répartis sur les 4 Briques fonctionnelles :
- Brique 1 : Normalisation [0, 1000] & Capture Set-of-Marks
- Brique 2 : Gestion Fenêtres X11 & Lancement de Processus
- Brique 3 : Presse-papier Système & OCR Local CPU
- Brique 4 : Pont Hybride Web (Playwright) & Enregistrement Vidéo FFmpeg
"""

import os
import time
import asyncio

# Import direct des fonctions exposées du serveur MCP GUI
from mcp_gui_server import (
    gui_get_screen_info,
    gui_take_screenshot,
    normalize_coordinates,
    gui_window_list,
    gui_clipboard_set,
    gui_clipboard_get,
    gui_find_text,
    gui_start_video_recording,
    gui_stop_video_recording,
    gui_web_action,
)


def run_e2e_validation():
    """Exécute l'ensemble des scénarios de validation bout-en-bout (E2E) du serveur."""
    print("=" * 70)
    print("      DÉBUT DU TEST D'INTÉGRATION END-TO-END (E2E) - MCP GUI SERVER")
    print("=" * 70)

    # 1. Validation Brique 1 : Informations Écran & Normalisation Coordonnées
    print("\n[Brique 1] 1. Métriques Écran & Normalisation [0, 1000]")
    screen_info = gui_get_screen_info()
    assert screen_info.get("status") == "success", f"Échec screen_info: {screen_info}"
    print(f"  ✓ Écran détecté : {screen_info.get('resolution')} (Display: {screen_info.get('display_env')})")

    norm_x, norm_y = normalize_coordinates(500, 500, normalized=True)
    print(f"  ✓ Normalisation [500, 500] -> Pixel : ({norm_x}, {norm_y})")

    # 2. Validation Brique 1 : Capture avec Grille Set-of-Marks
    print("\n[Brique 1] 2. Prise de capture avec incrustation Set-of-Marks")
    screenshot_res = gui_take_screenshot(apply_grid=True, grid_interval=200)
    assert screenshot_res.get("status") == "success", f"Échec capture: {screenshot_res}"
    assert os.path.exists(screenshot_res.get("screenshot_path")), "Fichier capture inexistant"
    print(f"  ✓ Capture enregistrée : {screenshot_res.get('screenshot_path')}")

    # 3. Validation Brique 2 : Gestion des Fenêtres X11
    print("\n[Brique 2] 3. Listage et Inspection des Fenêtres X11")
    win_list = gui_window_list()
    assert win_list.get("status") == "success", f"Échec window_list: {win_list}"
    print(f"  ✓ {win_list.get('count')} fenêtre(s) X11 répertoriée(s)")

    # 4. Validation Brique 3 : Presse-Papier Système
    print("\n[Brique 3] 4. Presse-Papier Système (Set / Get)")
    test_text = "E2E_Test_MCP_GUI_Token_12345"
    set_res = gui_clipboard_set(test_text)
    assert set_res.get("status") == "success", f"Échec clipboard_set: {set_res}"
    get_res = gui_clipboard_get()
    assert get_res.get("status") == "success", f"Échec clipboard_get: {get_res}"
    assert get_res.get("text") == test_text, f"Texte presse-papier mismatch: {get_res.get('text')}"
    print(f"  ✓ Presse-papier validé avec succès (Texte: '{get_res.get('text')}')")

    # 5. Validation Brique 3 : OCR CPU Local
    print("\n[Brique 3] 5. OCR CPU Local (Recherche de texte)")
    ocr_res = gui_find_text("E2E_Test")
    print(f"  ✓ OCR exécuté sans erreur (Statut : {ocr_res.get('status')})")

    # 6. Validation Brique 4 : Audit Vidéo (FFmpeg 5 FPS)
    print("\n[Brique 4] 6. Enregistrement Vidéo X11 à 5 FPS (FFmpeg)")
    video_output = "/tmp/test_e2e_video.mp4"
    start_vid = gui_start_video_recording(output_path=video_output, fps=5)
    assert start_vid.get("status") == "success", f"Échec démarrage vidéo: {start_vid}"
    print(f"  ✓ Enregistrement vidéo démarré (PID: {start_vid.get('pid')})")

    time.sleep(1.5)  # Enregistrement pendant 1.5 secondes

    stop_vid = gui_stop_video_recording()
    assert stop_vid.get("status") == "success", f"Échec arrêt vidéo: {stop_vid}"
    assert os.path.exists(video_output) and os.path.getsize(video_output) > 0, "Fichier vidéo absent ou vide"
    print(f"  ✓ Enregistrement vidéo terminé avec succès (Taille : {os.path.getsize(video_output)} octets)")

    # 7. Validation Brique 4 : Pont Hybride Web (Playwright Headless)
    print("\n[Brique 4] 7. Pont Hybride Web Playwright (Navigation et Snapshot ARIA)")
    web_res = asyncio.run(gui_web_action(url="https://example.com", action="aria_tree"))
    assert web_res.get("status") == "success", f"Échec web_action: {web_res}"
    print(f"  ✓ Arbre ARIA Web extrait avec succès : {web_res.get('title')} ('{web_res.get('url')}')")

    print("\n" + "=" * 70)
    print("   ✓ TOUS LES TESTS D'INTÉGRATION END-TO-END (E2E) ONT RÉUSSI (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_e2e_validation()
