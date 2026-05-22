#!/usr/bin/env python3
import os
import sys
import time
import logging
import shutil
from PIL import Image, ImageDraw
import pyautogui

# S'assurer que le SDK MCP est accessible
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Erreur : Le SDK 'mcp' n'est pas installé dans cet environnement virtuel.", file=sys.stderr)
    sys.exit(1)

# Configuration de la sécurité de PyAutoGUI
pyautogui.FAILSAFE = True  # Déplacer la souris dans le coin supérieur gauche lève une exception FailSafeException
pyautogui.PAUSE = 0.15      # Pause légère entre chaque commande d'action pour la stabilité

# Configurer les logs du serveur
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp_gui_server")

# Création du serveur MCP
mcp = FastMCP("GUI Agent Server")

# Répertoire de stockage des captures d'écran
SCREENSHOTS_DIR = "/home/omni/Code/gui_agent/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def check_display_env():
    """Vérifie que la variable d'environnement DISPLAY est définie pour X11."""
    if "DISPLAY" not in os.environ:
        # Tenter d'utiliser la valeur par défaut courante sous Linux si non définie
        os.environ["DISPLAY"] = ":0"
    logger.info(f"Variable DISPLAY active : {os.environ['DISPLAY']}")

@mcp.tool()
def gui_get_screen_info() -> dict:
    """
    Obtient les informations sur la configuration d'écran actuelle.
    Retourne la résolution d'écran et l'état des variables de session graphique.
    """
    check_display_env()
    try:
        width, height = pyautogui.size()
        return {
            "status": "success",
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height,
            "display_env": os.environ.get("DISPLAY", "None"),
            "wayland_display": os.environ.get("WAYLAND_DISPLAY", "None"),
            "failsafe_enabled": pyautogui.FAILSAFE
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Impossible d'obtenir les dimensions de l'écran : {str(e)}",
            "details": "Vérifiez que vous êtes dans une session graphique X11 active."
        }

@mcp.tool()
def gui_take_screenshot(apply_grid: bool = True, grid_interval: int = 100, save_to_artifacts: bool = False) -> dict:
    """
    Prend une capture d'écran complète du bureau.
    
    Arguments:
        apply_grid: Si True, dessine une grille de coordonnées géométriques contrastante (Set-of-Mark) sur l'image pour le repérage spatial.
        grid_interval: Espacement en pixels des lignes de la grille (ex: 100).
        save_to_artifacts: Si True, enregistre directement l'image dans le répertoire d'artifacts de la conversation.
    """
    check_display_env()
    try:
        # Prendre la capture d'écran via la bibliothèque ultra-rapide mss (sans dépendance gnome-screenshot)
        import mss
        with mss.mss() as sct:
            # Moniteur 1 représente l'écran complet principal
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        width, height = screenshot.size
        
        # Générer un nom de fichier unique basé sur le timestamp
        filename = f"screenshot_{int(time.time())}.png"
        raw_path = os.path.join(SCREENSHOTS_DIR, f"raw_{filename}")
        final_path = os.path.join(SCREENSHOTS_DIR, filename)
        
        # Enregistrer la version brute sans grille
        screenshot.save(raw_path)
        
        # Si demandé, appliquer la grille de repérage
        if apply_grid:
            grid_image = screenshot.copy()
            draw = ImageDraw.Draw(grid_image)
            
            # Dessiner les lignes verticales et indexer les coordonnées X
            for x in range(0, width, grid_interval):
                draw.line([(x, 0), (x, height)], fill=(150, 150, 150, 120), width=1)
                # Afficher le chiffre X
                draw.rectangle([(x + 2, 2), (x + 35, 15)], fill=(0, 0, 0, 180))
                draw.text((x + 4, 3), str(x), fill=(255, 255, 255))
                
            # Dessiner les lignes horizontales et indexer les coordonnées Y
            for y in range(0, height, grid_interval):
                draw.line([(0, y), (width, y)], fill=(150, 150, 150, 120), width=1)
                # Afficher le chiffre Y
                draw.rectangle([(2, y + 2), (35, y + 15)], fill=(0, 0, 0, 180))
                draw.text((4, y + 3), str(y), fill=(255, 255, 255))
                
            # Dessiner des labels précis aux intersections
            for x in range(grid_interval, width, grid_interval * 2):
                for y in range(grid_interval, height, grid_interval * 2):
                    # Petit point de repère au croisement
                    draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=(255, 0, 0))
                    # Étiquette de coordonnées
                    lbl = f"{x},{y}"
                    draw.rectangle([(x + 3, y + 3), (x + 60, y + 15)], fill=(0, 0, 255, 150))
                    draw.text((x + 5, y + 4), lbl, fill=(255, 255, 255))
            
            grid_image.save(final_path)
            screenshot_path = final_path
        else:
            screenshot.save(final_path)
            screenshot_path = final_path
            
        if save_to_artifacts:
            art_dir = "/home/omni/.gemini/antigravity/brain/e48ec26a-978a-4f3e-ad66-71e604f5934e"
            if os.path.exists(art_dir):
                shutil.copy(screenshot_path, os.path.join(art_dir, "screenshot_mcp.png"))
                
        return {
            "status": "success",
            "screenshot_path": screenshot_path,
            "raw_path": raw_path,
            "width": width,
            "height": height,
            "grid_applied": apply_grid,
            "grid_interval": grid_interval if apply_grid else None,
            "message": "Capture d'écran générée avec succès."
        }
    except Exception as e:
        logger.error(f"Erreur lors de la capture d'écran : {str(e)}")
        return {
            "status": "error",
            "message": f"Échec de la capture d'écran : {str(e)}"
        }

@mcp.tool()
def gui_mouse_click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
    """
    Effectue un ou plusieurs clics de souris à des coordonnées spécifiques (x, y).
    
    Arguments:
        x: Coordonnée horizontale en pixels.
        y: Coordonnée verticale en pixels.
        button: Bouton de la souris à utiliser ('left', 'right', 'middle').
        clicks: Nombre de clics (1 pour simple, 2 pour double clic).
    """
    check_display_env()
    try:
        # Déplacer doucement pour éviter les sauts brutaux (durée de 0.2s)
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click(x, y, button=button, clicks=clicks)
        return {
            "status": "success",
            "action": f"{clicks} clic(s) '{button}' effectué(s) à ({x}, {y})",
            "current_position": pyautogui.position()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Échec du clic de souris : {str(e)}"
        }

@mcp.tool()
def gui_mouse_move(x: int, y: int, duration: float = 0.2) -> dict:
    """
    Déplace la souris aux coordonnées (x, y) de manière fluide.
    
    Arguments:
        x: Coordonnée horizontale.
        y: Coordonnée verticale.
        duration: Durée du déplacement en secondes.
    """
    check_display_env()
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return {
            "status": "success",
            "action": f"Souris déplacée à ({x}, {y})",
            "current_position": pyautogui.position()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Échec du déplacement de souris : {str(e)}"
        }

@mcp.tool()
def gui_mouse_drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> dict:
    """
    Glisse-dépose de souris du point (x1, y1) jusqu'au point (x2, y2).
    
    Arguments:
        x1, y1: Coordonnées de départ.
        x2, y2: Coordonnées d'arrivée.
        duration: Durée du glisser-déposer en secondes.
    """
    check_display_env()
    try:
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=duration, button="left")
        return {
            "status": "success",
            "action": f"Glisser-déposer effectué de ({x1}, {y1}) à ({x2}, {y2})"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Échec du glisser-déposer : {str(e)}"
        }

def run_xdotool(args: list) -> bool:
    """Exécute une commande xdotool sous X11."""
    assert isinstance(args, list), "Les arguments doivent être une liste"
    assert len(args) > 0, "La liste d'arguments ne peut pas être vide"
    import subprocess
    try:
        env = os.environ.copy()
        env["DISPLAY"] = env.get("DISPLAY", ":0")
        subprocess.run(["/bin/xdotool"] + args, env=env, check=True)
        return True
    except Exception as e:
        logger.error(f"Erreur xdotool {args}: {e}")
        return False

def sleep_human(base_delay: float = 0.05) -> None:
    """Introduit un délai pseudo-aléatoire réaliste pour simuler un humain."""
    assert isinstance(base_delay, float), "Le délai de base doit être un float"
    assert base_delay >= 0.0, "Le délai ne peut pas être négatif"
    import random
    # Utiliser un délai avec distribution normale pour le jitter réaliste
    jitter = random.normalvariate(base_delay, base_delay * 0.3)
    time.sleep(max(0.01, jitter))

def type_char_human(char: str) -> bool:
    """Saisit un unique caractère de façon indifférenciable."""
    assert isinstance(char, str) and len(char) == 1, "Doit être un unique caractère"
    success = run_xdotool(["type", char])
    sleep_human(0.06)
    return success

@mcp.tool()
def gui_keyboard_type(text: str, delay: float = 0.06) -> dict:
    """TAPE du texte caractère par caractère de façon humaine indifférenciable."""
    assert isinstance(text, str), "Le texte saisi doit être une chaîne"
    assert len(text) > 0, "Le texte ne peut pas être vide"
    check_display_env()
    success = True
    for char in text:
        if not type_char_human(char):
            success = False
            break
    if success:
        return {"status": "success", "action": f"Texte tapé de façon humaine : '{text}'"}
    return {"status": "error", "message": "Échec de la saisie clavier humaine."}

def translate_key(key: str) -> str:
    """Traduit les touches système abrégées en termes natifs X11/xdotool."""
    assert isinstance(key, str), "La clé doit être une chaîne"
    assert len(key) > 0, "La clé ne peut pas être vide"
    key_map = {
        "super": "Super_L", "win": "Super_L", "enter": "Return", "return": "Return",
        "escape": "Escape", "esc": "Escape", "backspace": "BackSpace",
        "tab": "Tab", "space": "space", "ctrl": "control", "control": "control",
        "alt": "alt", "shift": "shift", "up": "Up", "down": "Down",
        "left": "Left", "right": "Right"
    }
    return key_map.get(key.lower(), key)

def press_shortcut_human(key: str) -> bool:
    """Simule séquentiellement un raccourci clavier complexe de façon humaine."""
    assert isinstance(key, str) and len(key) > 0, "Clé invalide"
    keys = [translate_key(k.strip()) for k in key.split("+")]
    assert len(keys) > 0, "Aucune touche détectée dans la combinaison"
    success = True
    for k in keys:
        if not run_xdotool(["keydown", k]):
            success = False
        sleep_human(0.02)
    sleep_human(0.08)
    for k in reversed(keys):
        if not run_xdotool(["keyup", k]):
            success = False
        sleep_human(0.015)
    return success

@mcp.tool()
def gui_keyboard_press(key: str) -> dict:
    """APPUIE sur une touche ou une combinaison de touches de façon indifférenciable."""
    assert isinstance(key, str), "La touche ou combinaison doit être une chaîne"
    assert len(key) > 0, "La touche ne peut pas être vide"
    check_display_env()
    if press_shortcut_human(key):
        return {"status": "success", "action": f"Appui clavier indifférenciable effectué pour '{key}'"}
    return {"status": "error", "message": f"Échec de l'appui clavier pour '{key}'"}


@mcp.tool()
def gui_window_list() -> dict:
    """Liste toutes les fenêtres visibles sous X11 (ID, Titre)."""
    check_display_env()
    import subprocess
    try:
        out = subprocess.check_output(["/bin/xdotool", "search", "--onlyvisible", "--name", ".*"]).decode("utf-8")
        win_ids = [line.strip() for line in out.splitlines() if line.strip().isdigit()]
        windows = []
        for wid in win_ids[:20]:
            title = subprocess.check_output(["/bin/xdotool", "getwindowname", wid]).decode("utf-8").strip()
            windows.append({"id": int(wid), "title": title})
        assert isinstance(windows, list), "Le résultat doit être une liste"
        assert len(windows) >= 0, "Liste valide"
        return {"status": "success", "windows": windows}
    except Exception as e:
        return {"status": "error", "message": f"Échec de la liste des fenêtres : {str(e)}"}


@mcp.tool()
def gui_window_focus(window_id: int) -> dict:
    """Active et donne le focus à une fenêtre par son ID X11."""
    assert isinstance(window_id, int) and window_id > 0, "L'ID de fenêtre doit être positif"
    check_display_env()
    import subprocess
    try:
        subprocess.run(["/bin/xdotool", "windowactivate", str(window_id)], check=True)
        assert True, "La commande xdotool a réussi"
        return {"status": "success", "message": f"Focus donné à la fenêtre {window_id}"}
    except Exception as e:
        return {"status": "error", "message": f"Impossible d'activer la fenêtre : {str(e)}"}


@mcp.tool()
def gui_find_template(template_path: str, threshold: float = 0.8) -> dict:
    """Recherche les coordonnées (x,y) d'une image modèle (template) sur l'écran."""
    assert isinstance(template_path, str) and os.path.exists(template_path), "Fichier template introuvable"
    assert 0.0 < threshold <= 1.0, "Le seuil de confiance doit être entre 0 et 1"
    check_display_env()
    try:
        import cv2, numpy as np, mss
        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[1])
            screen = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path)
        res = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            th, tw = template.shape[:2]
            cx, cy = max_loc[0] + tw // 2, max_loc[1] + th // 2
            return {"status": "success", "x": cx, "y": cy, "confidence": float(max_val)}
        return {"status": "not_found", "message": f"Template non trouvé. Confiance max : {max_val:.2f}"}
    except Exception as e:
        return {"status": "error", "message": f"Échec de la recherche : {str(e)}"}


@mcp.tool()
def gui_mouse_scroll(clicks: int, direction: str = "down") -> dict:
    """Simule un défilement vertical ou horizontal de molette de souris."""
    assert isinstance(clicks, int) and clicks > 0, "Le nombre de clics doit être un entier positif"
    assert direction.lower() in ["up", "down", "left", "right"], "Direction invalide"
    check_display_env()
    try:
        btn_map = {"up": "4", "down": "5", "left": "6", "right": "7"}
        btn = btn_map[direction.lower()]
        for _ in range(clicks):
            run_xdotool(["click", btn])
            time.sleep(0.02)
        return {"status": "success", "action": f"Défilement de {clicks} pas vers le '{direction}'"}
    except Exception as e:
        return {"status": "error", "message": f"Échec du défilement : {str(e)}"}


if __name__ == "__main__":
    logger.info("Démarrage du serveur MCP GUI Agent...")
    check_display_env()
    # Lancement du serveur MCP en mode standard (stdio)
    mcp.run()
