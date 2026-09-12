#!/usr/bin/env python3
import os
import sys
import shutil

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT_DIR)

try:
    import mcp_gui_server
except ImportError as err:
    print(f"Erreur d'importation : {err}", file=sys.stderr)
    sys.exit(1)


def main():
    print("Prise de la capture d'écran...")
    res = mcp_gui_server.gui_take_screenshot(apply_grid=True, grid_interval=100)
    if res.get("status") != "success":
        print(f"Erreur : {res.get('message')}")
        sys.exit(1)

    scr_path = res.get("screenshot_path")
    if not scr_path or not os.path.isfile(scr_path):
        print("Erreur : Fichier de capture d'écran introuvable dans le retour.")
        sys.exit(1)

    try:
        try:
            from paths import get_screenshots_dir
        except ImportError:
            from linux.paths import get_screenshots_dir

        fallback_artifacts = os.path.join(os.path.dirname(get_screenshots_dir()), "artifacts")
    except Exception:
        fallback_artifacts = os.path.join(os.getcwd(), "artifacts")

    dest_dir = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GUI_AGENT_ARTIFACTS_DIR", fallback_artifacts)
    dest_path = os.path.join(dest_dir, "screenshot_xboard.png")

    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(scr_path, dest_path)
    print(f"Capture enregistrée et copiée vers : {dest_path}")
    print(f"Dimensions : {res.get('width')}x{res.get('height')}")


if __name__ == "__main__":
    main()
