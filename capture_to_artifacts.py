#!/usr/bin/env python3
import os
import sys
import shutil

sys.path.append("/home/omni/Code/gui_agent")
import mcp_gui_server

def main():
    print("Prise de la capture d'écran...")
    res = mcp_gui_server.gui_take_screenshot(apply_grid=True, grid_interval=100)
    if res.get("status") != "success":
        print(f"Erreur : {res.get('message')}")
        sys.exit(1)
        
    scr_path = res.get("screenshot_path")
    dest_dir = "/home/omni/.gemini/antigravity/brain/e48ec26a-978a-4f3e-ad66-71e604f5934e"
    dest_path = os.path.join(dest_dir, "screenshot_xboard.png")
    
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(scr_path, dest_path)
    print(f"Capture enregistrée et copiée vers : {dest_path}")
    print(f"Dimensions : {res.get('width')}x{res.get('height')}")

if __name__ == "__main__":
    main()
