#!/usr/bin/env python3
import os
import sys
import time

# Permettre l'importation de mcp_gui_server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import mcp_gui_server
except ImportError as e:
    print(f"Erreur d'importation de mcp_gui_server : {e}", file=sys.stderr)
    sys.exit(1)


def run_integration_test():
    print("=== DÉBUT DU TEST DE L'AGENT GUI ===")

    # 1. Vérification des infos écran
    print("\n[Étape 1] Récupération des informations d'écran...")
    screen_info = mcp_gui_server.gui_get_screen_info()
    print(f"Résultat : {screen_info}")

    if screen_info.get("status") == "error":
        print(f"Échec : {screen_info.get('message')}")
        print("Veuillez vous assurer que la variable DISPLAY est correcte et qu'une session X11 est active.")
        sys.exit(1)

    width = screen_info.get("width")
    height = screen_info.get("height")
    assert width > 0 and height > 0, "Assertion échouée : Résolution invalide !"

    # 2. Prendre une capture d'écran initiale avec grille de coordonnées
    print("\n[Étape 2] Prise de capture d'écran initiale (avec grille)...")
    screenshot_res = mcp_gui_server.gui_take_screenshot(apply_grid=True, grid_interval=150)
    print(f"Résultat : {screenshot_res}")

    assert screenshot_res.get("status") == "success", "Assertion échouée : La capture a échoué !"
    screenshot_path = screenshot_res.get("screenshot_path")
    assert os.path.exists(screenshot_path), f"Assertion échouée : Fichier image absent ({screenshot_path}) !"
    print(f"Capture enregistrée à : {screenshot_path}")

    # 3. Simulation sécurisée de mouvements de souris au centre de l'écran
    print("\n[Étape 3] Simulation de mouvements de souris sécurisés...")
    cx, cy = width // 2, height // 2
    print(f"Déplacement de la souris vers le centre : ({cx}, {cy})")

    # Dessiner un petit carré virtuel autour du centre
    move_offsets = [(cx - 50, cy - 50), (cx + 50, cy - 50), (cx + 50, cy + 50), (cx - 50, cy + 50), (cx, cy)]

    for ox, oy in move_offsets:
        res = mcp_gui_server.gui_mouse_move(ox, oy, duration=0.15)
        print(f"  Déplacement vers ({ox}, {oy}) -> {res.get('status')}")
        assert res.get("status") == "success", "Assertion échouée : Le mouvement a échoué !"
        time.sleep(0.1)

    # 4. Simulation de raccourci clavier sécurisé
    print("\n[Étape 4] Simulation d'appui clavier sécurisé...")
    # Nous allons simuler un appui sur 'super' ou 'alt' puis 'escape' pour ne pas perturber l'utilisateur.
    # 'alt' seul ou 'super' est sans danger.
    print("Appui sur la touche 'super' (pour ouvrir le menu système sous Linux)...")
    res_key = mcp_gui_server.gui_keyboard_press("super")
    print(f"Résultat appui : {res_key}")

    # Attendre que le menu s'affiche (1 seconde)
    time.sleep(1.0)

    # Prendre une capture d'écran du menu ouvert
    print("Prise de capture d'écran du menu ouvert...")
    screenshot_menu = mcp_gui_server.gui_take_screenshot(apply_grid=True, grid_interval=150)
    print(f"Capture menu : {screenshot_menu.get('status')}")

    # Refermer le menu
    print("Appui sur la touche 'escape' (pour fermer le menu)...")
    mcp_gui_server.gui_keyboard_press("escape")

    print("\n=== TEST DE L'AGENT GUI TERMINÉ AVEC SUCCÈS ===")
    print("Vous pouvez inspecter les captures d'écran générées dans le dossier :")
    print("  /home/omni/Code/gui_agent/screenshots/")


if __name__ == "__main__":
    run_integration_test()
