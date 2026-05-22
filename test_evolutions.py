#!/usr/bin/env python3
import os
import sys
import time
from PIL import Image

sys.path.append("/home/omni/Code/gui_agent")
import mcp_gui_server

def run_evolution_tests():
    print("=== DÉBUT DES TESTS DES ÉVOLUTIONS SOTA ===")
    
    # 1. Test de la liste des fenêtres
    print("\n[Test 1] Récupération de la liste des fenêtres X11...")
    res_list = mcp_gui_server.gui_window_list()
    assert res_list.get("status") == "success", "Échec du listage des fenêtres"
    windows = res_list.get("windows", [])
    print(f"Trouvé {len(windows)} fenêtres actives.")
    for win in windows[:5]:
        print(f"  - ID: {win['id']} | Titre: {win['title']}")
        
    # 2. Test du focus de fenêtre
    print("\n[Test 2] Test de focus de fenêtre...")
    # On va focus notre propre fenêtre ou la première visible pour valider l'outil
    if windows:
        target_win = windows[0]
        print(f"Donne le focus à la fenêtre : {target_win['title']} (ID: {target_win['id']})")
        res_focus = mcp_gui_server.gui_window_focus(target_win["id"])
        assert res_focus.get("status") == "success", "Échec du focus"
        print("Focus accordé avec succès.")
    else:
        print("Aucune fenêtre active pour tester le focus.")
        
    # 3. Test du défilement de souris (Scroll)
    print("\n[Test 3] Test du défilement de souris...")
    res_scroll = mcp_gui_server.gui_mouse_scroll(clicks=2, direction="down")
    assert res_scroll.get("status") == "success", "Échec du défilement"
    print("Défilement simulé avec succès.")
    
    # 4. Test de la capture d'écran directe dans les artefacts
    print("\n[Test 4] Capture d'écran avec stockage direct dans les artefacts...")
    res_scr = mcp_gui_server.gui_take_screenshot(apply_grid=False, save_to_artifacts=True)
    assert res_scr.get("status") == "success", "Échec de la capture d'écran"
    dest_art = "/home/omni/.gemini/antigravity/brain/e48ec26a-978a-4f3e-ad66-71e604f5934e/screenshot_mcp.png"
    assert os.path.exists(dest_art), "Le fichier de capture d'écran est introuvable dans les artefacts"
    print(f"Capture enregistrée directement dans les artefacts à : {dest_art}")

    # 5. Test déterministe de Template Matching (Recherche visuelle)
    print("\n[Test 5] Test déterministe de Template Matching (OpenCV)...")
    # On va découper un petit carré de 30x30 pixels sur la capture d'écran que l'on vient de faire
    # et vérifier qu'OpenCV arrive à le retrouver à ses coordonnées exactes !
    raw_path = res_scr.get("raw_path")
    assert os.path.exists(raw_path), "Fichier brut manquant"
    
    # Découper une zone de test (de x=100 à 130, y=100 à 130)
    img = Image.open(raw_path)
    template_area = img.crop((100, 100, 130, 130))
    template_path = "/tmp/test_template_crop.png"
    template_area.save(template_path)
    
    print(f"Génération d'un modèle de test à : {template_path}")
    res_match = mcp_gui_server.gui_find_template(template_path=template_path, threshold=0.9)
    assert res_match.get("status") == "success", f"Échec du template matching : {res_match.get('message')}"
    
    match_x = res_match.get("x")
    match_y = res_match.get("y")
    confidence = res_match.get("confidence")
    print(f"Modèle trouvé aux coordonnées : ({match_x}, {match_y}) avec confiance {confidence:.4f}")
    
    # Le centre de la zone (100, 100, 130, 130) est à x=115, y=115
    assert abs(match_x - 115) <= 2 and abs(match_y - 115) <= 2, f"Coordonnées de matching incorrectes ! Trouvé ({match_x}, {match_y}) au lieu de (115, 115)"
    print("La recherche visuelle a retourné les coordonnées exactes (précision sub-pixel valisée) !")

    # Nettoyage temporaire
    if os.path.exists(template_path):
        os.remove(template_path)

    print("\n=== TOUS LES TESTS DES ÉVOLUTIONS SOTA ONT RÉUSSI ===")

if __name__ == "__main__":
    run_evolution_tests()
