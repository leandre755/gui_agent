import base64
import contextlib
import logging
import math
import os
import shlex
import shutil
import subprocess
import tempfile
import time
from typing import Any
from PIL import Image, ImageDraw

# S'assurer que la variable DISPLAY existe pour éviter KeyError sous Linux headless/CI
os.environ.setdefault("DISPLAY", ":0")
import pyautogui

# S'assurer que le SDK MCP est accessible
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as err:
    raise ImportError(
        "Erreur : Le SDK 'mcp' version 1.x (FastMCP) est requis pour faire fonctionner gui-agent."
    ) from err

# Configuration de la sécurité de PyAutoGUI
pyautogui.FAILSAFE = True  # Déplacer la souris dans le coin supérieur gauche lève une exception FailSafeException
pyautogui.PAUSE = 0.15  # Pause légère entre chaque commande d'action pour la stabilité

# Configurer les logs du serveur
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp_gui_server")

# Création du serveur MCP
mcp = FastMCP("GUI Agent Server")

# Répertoire de stockage des captures d'écran (configurable via GUI_AGENT_SCREENSHOTS_DIR)
SCREENSHOTS_DIR = os.path.abspath(
    os.environ.get(
        "GUI_AGENT_SCREENSHOTS_DIR",
        os.path.join(os.path.expanduser("~"), ".local", "share", "gui-agent", "screenshots"),
    )
)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def check_display_env() -> None:
    """Vérifie que la variable d'environnement DISPLAY est définie pour X11."""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"


def capture_screen_pil(monitor_index: int = 1) -> Image.Image:
    """
    Capture l'écran actif avec fallback automatique sur spectacle (Wayland/X11)
    si mss retourne une image vide ou uniforme.
    """
    check_display_env()
    # 1. Tentative via spectacle (indispensable sous XWayland/KDE si mss capture un framebuffer noir)
    spectacle_bin = shutil.which("spectacle")
    if spectacle_bin:
        with tempfile.NamedTemporaryFile(suffix=".png", prefix="_mcp_screen_tmp_", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        try:
            res = subprocess.run(
                [spectacle_bin, "-b", "-n", "-o", tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            )
            if res.returncode == 0 and os.path.exists(tmp_path):
                img = Image.open(tmp_path).convert("RGB")
                with contextlib.suppress(Exception):
                    os.remove(tmp_path)
                import numpy as np

                if np.std(np.array(img)) > 0.001:
                    return img
        except Exception as e_spec:
            logger.debug(f"Fallback spectacle ignoré : {e_spec}")
        finally:
            with contextlib.suppress(Exception):
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    # 2. Fallback / méthode standard via mss
    import mss

    with mss.MSS() as sct:
        if monitor_index < 0 or monitor_index >= len(sct.monitors):
            monitor_index = 1 if len(sct.monitors) > 1 else 0
        monitor = sct.monitors[monitor_index]
        sct_img = sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")


def get_monitor_geometry(monitor_index: int = 1) -> tuple[int, int, int, int]:
    """Obtient les coordonnées (left, top, width, height) d'un moniteur spécifique."""
    if not isinstance(monitor_index, int) or isinstance(monitor_index, bool):
        raise TypeError(f"monitor_index doit être un entier, reçu : {type(monitor_index).__name__}")
    check_display_env()
    import mss

    with mss.MSS() as sct:
        if monitor_index < 0 or monitor_index >= len(sct.monitors):
            raise ValueError(
                f"Index de moniteur invalide : {monitor_index}. Index valides : 0 à {len(sct.monitors) - 1}."
            )
        mon = sct.monitors[monitor_index]
        return mon["left"], mon["top"], mon["width"], mon["height"]


def normalize_coordinates(
    x: float, y: float, normalized: bool = False, inverse: bool = False, monitor_index: int = 1
) -> tuple[int, int]:
    """
    Convertit des coordonnées du référentiel [0, 1000] x [0, 1000] vers les pixels réels de l'écran (ou inversement).
    Garantit l'indexation exacte dans les bornes [left, left + width - 1] et [top, top + height - 1].
    """
    if not isinstance(normalized, bool):
        raise TypeError(f"Le paramètre 'normalized' doit être un booléen, reçu : {type(normalized).__name__}")
    if not isinstance(inverse, bool):
        raise TypeError(f"Le paramètre 'inverse' doit être un booléen, reçu : {type(inverse).__name__}")
    if not (isinstance(x, (int, float)) and isinstance(y, (int, float))) or isinstance(x, bool) or isinstance(y, bool):
        raise TypeError("Les coordonnées x et y doivent être des nombres réels (int ou float).")
    if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
        raise ValueError("Les coordonnées x et y ne peuvent pas être NaN ou Infinity.")

    left, top, width, height = get_monitor_geometry(monitor_index)
    max_x = left + max(0, width - 1)
    max_y = top + max(0, height - 1)

    if inverse:
        rel_x = float(x) - float(left)
        rel_y = float(y) - float(top)
        denom_w = float(max(1, width - 1))
        denom_h = float(max(1, height - 1))
        norm_x = round(max(0.0, min(1000.0, (rel_x / denom_w) * 1000.0)))
        norm_y = round(max(0.0, min(1000.0, (rel_y / denom_h) * 1000.0)))
        return norm_x, norm_y

    if normalized:
        fx = float(x)
        fy = float(y)
        # Auto-détection si l'utilisateur transmet des valeurs float dans [0.0, 1.0] au lieu de [0, 1000]
        if 0.0 <= fx <= 1.0:
            fx *= 1000.0
        if 0.0 <= fy <= 1.0:
            fy *= 1000.0

        x_clamped = max(0.0, min(1000.0, fx))
        y_clamped = max(0.0, min(1000.0, fy))
        real_x = left + round((x_clamped / 1000.0) * float(max(0, width - 1)))
        real_y = top + round((y_clamped / 1000.0) * float(max(0, height - 1)))
    else:
        real_x = round(max(float(left), min(float(max_x), float(x))))
        real_y = round(max(float(top), min(float(max_y), float(y))))

    return real_x, real_y


@mcp.tool()
def gui_get_screen_info() -> dict[str, Any]:
    """
    Obtient les informations sur la configuration d'écran actuelle.
    Retourne la résolution d'écran, les moniteurs détectés et l'état des variables de session graphique.
    """
    check_display_env()
    try:
        width, height = pyautogui.size()
        monitors_info = []
        try:
            import mss

            with mss.MSS() as sct:
                for idx, mon in enumerate(sct.monitors):
                    monitors_info.append(
                        {
                            "index": idx,
                            "width": mon["width"],
                            "height": mon["height"],
                            "top": mon["top"],
                            "left": mon["left"],
                            "is_primary": (idx == 1 if len(sct.monitors) > 1 else idx == 0),
                        }
                    )
        except Exception as e_mon:
            logger.warning(f"Impossible d'obtenir la liste des moniteurs : {e_mon}")

        return {
            "status": "success",
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height,
            "monitors": monitors_info,
            "display_env": os.environ.get("DISPLAY", "None"),
            "wayland_display": os.environ.get("WAYLAND_DISPLAY", "None"),
            "failsafe_enabled": pyautogui.FAILSAFE,
        }
    except Exception as e:
        return {"status": "error", "message": f"Impossible d'obtenir les dimensions de l'écran : {e!s}"}


def _reserve_unique_file_path(
    base_dir: str, stem: str, ext: str, original_candidate: str | None = None
) -> tuple[str, bool, tuple[int, int]]:
    """Réserve atomiquement un chemin de fichier unique sur disque et enregistre son identifiant (dev, ino).

    Crée un fichier vide via os.O_CREAT | os.O_EXCL pour garantir qu'aucun
    autre processus concurrent ne puisse s'approprier le même nom de fichier.
    Retourne le chemin, le booléen de renommage et la signature inode (st_dev, st_ino)
    pour sécuriser les opérations ultérieures contre les substitutions de fichiers.
    """
    os.makedirs(base_dir, exist_ok=True)
    counter = 0
    renamed = False

    while True:
        if counter == 0:
            candidate = original_candidate or os.path.join(base_dir, f"{stem}.{ext}")
        else:
            candidate = os.path.join(base_dir, f"{stem} ({counter}).{ext}")

        try:
            fd = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            try:
                st = os.fstat(fd)
                file_identity = (st.st_dev, st.st_ino)
            finally:
                os.close(fd)

            if counter > 0:
                renamed = True
            return candidate, renamed, file_identity
        except FileExistsError as err:
            counter += 1
            if counter > 10000:
                raise RuntimeError(
                    f"Impossible de trouver un nom de fichier libre après {counter} tentatives dans {base_dir}"
                ) from err


def _write_pil_image_safely(
    img: Any, target_path: str, expected_identity: tuple[int, int], pil_format: str, save_kwargs: dict[str, Any]
) -> None:
    """Écrit une image PIL dans un fichier réservé en garantissant l'identité de l'inode."""
    # Ouvre le descripteur et vérifie que le fichier correspond exactement au descripteur réservé (pas de substitution)
    fd = os.open(target_path, os.O_WRONLY)
    try:
        st = os.fstat(fd)
        if (st.st_dev, st.st_ino) != expected_identity:
            raise RuntimeError(
                f"Détection d'une substitution de fichier concurrente sur '{target_path}'. Écriture annulée."
            )
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        with open(fd, "wb", closefd=False) as f:
            img.save(f, format=pil_format, **{k: v for k, v in save_kwargs.items() if k != "format"})
            f.flush()
    finally:
        os.close(fd)


def _copy_file_safely(
    src_path: str, dst_path: str, expected_src_identity: tuple[int, int], expected_dst_identity: tuple[int, int]
) -> None:
    """Copie le contenu d'un fichier source dans un fichier destination réservé en vérifiant les deux identités d'inodes."""
    fd_src = os.open(src_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        st_src = os.fstat(fd_src)
        if (st_src.st_dev, st_src.st_ino) != expected_src_identity:
            raise RuntimeError(
                f"Détection d'une substitution de fichier concurrente sur la source '{src_path}'. Copie annulée."
            )

        fd_dst = os.open(dst_path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            st_dst = os.fstat(fd_dst)
            if (st_dst.st_dev, st_dst.st_ino) != expected_dst_identity:
                raise RuntimeError(
                    f"Détection d'une substitution de fichier concurrente sur la destination '{dst_path}'. Copie annulée."
                )
            os.ftruncate(fd_dst, 0)
            os.lseek(fd_dst, 0, os.SEEK_SET)
            with open(fd_src, "rb", closefd=False) as f_src, open(fd_dst, "wb", closefd=False) as f_dst:
                shutil.copyfileobj(f_src, f_dst)
                f_dst.flush()
        finally:
            os.close(fd_dst)
    finally:
        os.close(fd_src)


def _cleanup_reserved_file_safely(target_path: str | None, expected_identity: tuple[int, int] | None) -> None:
    """Nettoie un fichier réservé en cas d'erreur de manière sécurisée et sans risque de suppression de fichier étranger.

    Vérifie l'identité d'inode via son descripteur ouvert avec `O_NOFOLLOW` et re-vérifie
    l'entrée répertoire (`os.stat`) liée au descripteur de répertoire parent (`dir_fd`) avant suppression.
    Si la suppression ne peut être liée de manière infaillible à l'inode attendu, le fichier est conservé.
    """
    if not target_path or not expected_identity or not os.path.exists(target_path):
        return

    parent_dir = os.path.dirname(target_path) or "."
    filename = os.path.basename(target_path)

    dir_fd = None
    file_fd = None
    try:
        dir_flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            dir_flags |= os.O_DIRECTORY
        dir_fd = os.open(parent_dir, dir_flags)

        file_flags = os.O_RDWR if hasattr(os, "O_RDWR") else os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            file_flags |= os.O_NOFOLLOW

        file_fd = os.open(filename, file_flags, dir_fd=dir_fd)
        st_file = os.fstat(file_fd)
        if (st_file.st_dev, st_file.st_ino) == expected_identity:
            # Tronquer le fichier réservé à 0 octet via son descripteur vérifié
            with contextlib.suppress(OSError):
                os.ftruncate(file_fd, 0)

            # Re-vérification stricte de l'entrée répertoire avant unlink
            st_entry = os.stat(filename, dir_fd=dir_fd)
            if (st_entry.st_dev, st_entry.st_ino) == expected_identity:
                os.unlink(filename, dir_fd=dir_fd)
    except OSError:
        pass
    finally:
        if file_fd is not None:
            with contextlib.suppress(OSError):
                os.close(file_fd)
        if dir_fd is not None:
            with contextlib.suppress(OSError):
                os.close(dir_fd)


def _resolve_screenshot_destination(
    output_path: str | None, fmt_clean: str, ext: str
) -> tuple[str, str, bool, str | None, tuple[int, int], tuple[int, int]] | dict[str, Any]:
    """Résout et réserve atomiquement le chemin cible final et le chemin brut avec leurs identifiants inode."""
    renamed_due_to_conflict = False
    original_requested_path = None

    if output_path is not None:
        clean_out = str(output_path).strip()
        if not clean_out:
            return {
                "status": "error",
                "message": "output_path ne peut pas être une chaîne vide.",
            }
        final_path_cand = os.path.abspath(clean_out)
        if os.path.isdir(final_path_cand):
            return {
                "status": "error",
                "message": f"output_path '{final_path_cand}' est un dossier existant, un chemin de fichier est requis.",
            }
        _, out_ext = os.path.splitext(final_path_cand)
        out_ext_clean = out_ext.lower().lstrip(".")
        if not out_ext_clean:
            final_path_cand = f"{final_path_cand}.{ext}"
        else:
            valid_exts = {"jpg": ["jpg", "jpeg"], "jpeg": ["jpg", "jpeg"], "png": ["png"]}[fmt_clean]
            if out_ext_clean not in valid_exts:
                return {
                    "status": "error",
                    "message": (
                        f"Incohérence d'extension de fichier : l'extension '{out_ext}' de output_path "
                        f"ne correspond pas au format encodé '{fmt_clean}' (attendu: {', '.join('.' + e for e in valid_exts)})."
                    ),
                }

        parent_dir = os.path.dirname(final_path_cand)
        stem, ext_part = os.path.splitext(os.path.basename(final_path_cand))
        target_ext = ext_part.lstrip(".") or ext

        # Réservation atomique (O_CREAT | O_EXCL) avec incrémentation (1), (2)...
        original_requested_path = final_path_cand
        final_path, renamed_due_to_conflict, final_identity = _reserve_unique_file_path(
            parent_dir, stem, target_ext, original_candidate=final_path_cand
        )
    else:
        configured_dir = os.path.abspath(SCREENSHOTS_DIR)
        timestamp = int(time.time())
        stem = f"screenshot_{timestamp}"
        final_path, _, final_identity = _reserve_unique_file_path(configured_dir, stem, ext)

    configured_raw_dir = os.path.abspath(SCREENSHOTS_DIR)
    timestamp_raw = int(time.time())
    stem_raw = f"raw_screenshot_{timestamp_raw}"
    try:
        raw_path, _, raw_identity = _reserve_unique_file_path(configured_raw_dir, stem_raw, ext)
    except Exception:
        _cleanup_reserved_file_safely(final_path, final_identity)
        raise

    return final_path, raw_path, renamed_due_to_conflict, original_requested_path, final_identity, raw_identity


@mcp.tool()
def gui_take_screenshot(
    monitor_index: int = 1,
    crop_box: list[int] | None = None,
    apply_grid: bool = True,
    grid_interval: int = 100,
    format: str = "png",
    quality: int = 80,
    output_path: str | None = None,
    include_base64: bool = False,
) -> dict[str, Any]:
    """
    Prend une capture d'écran complète ou rognée du bureau avec gestion optimisée de la mémoire et grille adaptative.
    """
    check_display_env()
    if not isinstance(monitor_index, int) or isinstance(monitor_index, bool):
        return {"status": "error", "message": "monitor_index doit être un entier."}

    raw_img = None
    cropped_img = None
    grid_img = None
    final_path = None
    raw_path = None
    final_identity = None
    raw_identity = None
    success = False
    try:
        raw_img = capture_screen_pil(monitor_index=monitor_index)
        working_img = raw_img

        if crop_box is not None:
            if not isinstance(crop_box, (list, tuple)) or len(crop_box) != 4:
                return {"status": "error", "message": "crop_box doit contenir exactement 4 éléments [x, y, w, h]."}
            try:
                cx, cy, cw, ch = [int(v) for v in crop_box]
            except (ValueError, TypeError):
                return {"status": "error", "message": "Les valeurs de crop_box doivent être des entiers valides."}

            if cw <= 0 or ch <= 0:
                return {
                    "status": "error",
                    "message": "Les dimensions w et h de crop_box doivent être strictement positives.",
                }

            img_w, img_h = working_img.size
            cx1 = max(0, min(cx, img_w - 1))
            cy1 = max(0, min(cy, img_h - 1))
            cx2 = max(cx1 + 1, min(cx + cw, img_w))
            cy2 = max(cy1 + 1, min(cy + ch, img_h))
            cropped_img = working_img.crop((cx1, cy1, cx2, cy2))
            working_img = cropped_img

        width, height = working_img.size

        fmt_clean = str(format).lower().strip()
        if fmt_clean not in ["png", "jpeg", "jpg"]:
            return {
                "status": "error",
                "message": f"Format non supporté '{format}'. Formats supportés : 'png', 'jpeg', 'jpg'.",
            }

        if fmt_clean in ["jpeg", "jpg"]:
            ext = "jpg"
            pil_format = "JPEG"
            quality_val = max(1, min(100, int(quality)))
            save_kwargs: dict[str, Any] = {"format": pil_format, "quality": quality_val, "optimize": True}
        else:
            ext = "png"
            pil_format = "PNG"
            save_kwargs = {"format": pil_format, "optimize": True}

        dest_result = _resolve_screenshot_destination(output_path, fmt_clean, ext)
        if isinstance(dest_result, dict):
            return dest_result

        final_path, raw_path, renamed_due_to_conflict, original_requested_path, final_identity, raw_identity = (
            dest_result
        )

        # Sauvegarde sécurisée de l'image brute (avec vérification de l'inode)
        _write_pil_image_safely(working_img, raw_path, raw_identity, pil_format, save_kwargs)

        if apply_grid:
            grid_interval = max(20, int(grid_interval))
            grid_img = working_img.copy()
            draw = ImageDraw.Draw(grid_img, "RGBA")

            scale_factor = max(1.0, width / 1920.0)
            line_w = max(1, round(scale_factor))

            # Lignes d'axes X et étiquettes adaptatives
            for x in range(0, width, grid_interval):
                draw.line([(x, 0), (x, height)], fill=(255, 0, 0, 160), width=line_w)
                txt = str(x)
                box_w = len(txt) * 7 + 8
                draw.rectangle(
                    [(x + 1, 2), (min(width - 1, x + 1 + box_w), 16)], fill=(0, 0, 0, 220), outline=(255, 255, 255, 255)
                )
                draw.text((x + 4, 3), txt, fill=(255, 255, 0, 255))

            # Lignes d'axes Y et étiquettes adaptatives
            for y in range(0, height, grid_interval):
                draw.line([(0, y), (width, y)], fill=(255, 0, 0, 160), width=line_w)
                txt = str(y)
                box_w = len(txt) * 7 + 8
                draw.rectangle(
                    [(2, y + 1), (2 + box_w, min(height - 1, y + 16))],
                    fill=(0, 0, 0, 220),
                    outline=(255, 255, 255, 255),
                )
                draw.text((5, y + 2), txt, fill=(255, 255, 0, 255))

            # Marqueurs d'intersection lisibles sans débordement
            for x in range(grid_interval, width, grid_interval * 2):
                for y in range(grid_interval, height, grid_interval * 2):
                    draw.ellipse([(x - 3, y - 3), (x + 3, y + 3)], fill=(0, 255, 255, 255), outline=(0, 0, 0, 255))
                    lbl = f"{x},{y}"
                    draw.rectangle(
                        [(x + 4, y + 4), (min(width - 1, x + 4 + len(lbl) * 7 + 6), min(height - 1, y + 18))],
                        fill=(0, 0, 0, 200),
                        outline=(0, 255, 255, 255),
                    )
                    draw.text((x + 6, y + 5), lbl, fill=(255, 255, 255, 255))

            # Sauvegarde sécurisée de l'image avec grille (avec vérification de l'inode)
            _write_pil_image_safely(grid_img, final_path, final_identity, pil_format, save_kwargs)
        else:
            # Pas de grille, copie sécurisée de l'image brute vers le fichier final en vérifiant les deux inodes
            _copy_file_safely(raw_path, final_path, raw_identity, final_identity)

        base64_data = None
        if include_base64:
            # Encodage Base64 sécurisé : réouverture avec validation stricte de l'inode (évite toute substitution de contenu)
            target_to_encode = final_path if os.path.exists(final_path) else raw_path
            expected_encode_id = final_identity if target_to_encode == final_path else raw_identity
            read_flags = os.O_RDONLY
            if hasattr(os, "O_NOFOLLOW"):
                read_flags |= os.O_NOFOLLOW
            fd_read = os.open(target_to_encode, read_flags)
            try:
                st_read = os.fstat(fd_read)
                if (st_read.st_dev, st_read.st_ino) != expected_encode_id:
                    raise RuntimeError(
                        f"Détection d'une substitution de fichier concurrente sur '{target_to_encode}' lors de l'encodage Base64."
                    )
                with open(fd_read, "rb", closefd=False) as f_img:
                    base64_data = base64.b64encode(f_img.read()).decode("utf-8")
            finally:
                os.close(fd_read)

        if renamed_due_to_conflict and original_requested_path:
            success_msg = (
                f"Capture d'écran générée avec succès. Le fichier existant a été protégé contre l'écrasement ; "
                f"la capture a été enregistrée sous le nom '{os.path.basename(final_path)}'."
            )
        else:
            success_msg = "Capture d'écran générée avec succès."

        res_dict = {
            "status": "success",
            "screenshot_path": final_path,
            "raw_screenshot_path": raw_path,
            "format": ext,
            "resolution": f"{width}x{height}",
            "cropped": (crop_box is not None),
            "grid_applied": apply_grid,
            "grid_interval": grid_interval if apply_grid else None,
            "renamed_due_to_conflict": renamed_due_to_conflict,
            "message": success_msg,
        }
        if include_base64 and base64_data:
            res_dict["base64_data"] = base64_data

        success = True
        return res_dict
    except Exception as e:
        logger.error(f"Erreur capture d'écran : {e!s}")
        return {"status": "error", "message": f"Échec de la capture d'écran : {e!s}"}
    finally:
        if not success:
            _cleanup_reserved_file_safely(final_path, final_identity)
            _cleanup_reserved_file_safely(raw_path, raw_identity)
        for img in [raw_img, cropped_img, grid_img]:
            if img is not None:
                with contextlib.suppress(Exception):
                    img.close()


@mcp.tool()
def gui_mouse_click(
    x: float, y: float, button: str = "left", clicks: int = 1, normalized: bool = False, monitor_index: int = 1
) -> dict[str, Any]:
    """
    Effectue un ou plusieurs clics de souris à des coordonnées spécifiques (x, y).
    """
    check_display_env()
    try:
        button_clean = str(button).lower().strip()
        if button_clean not in ["left", "right", "middle"]:
            return {"status": "error", "message": "button doit être 'left', 'right' ou 'middle'."}
        clicks_val = max(1, int(clicks))

        try:
            x_real, y_real = normalize_coordinates(x, y, normalized=normalized, monitor_index=monitor_index)
        except (ValueError, TypeError) as e_val:
            return {"status": "error", "message": f"Paramètres de coordonnées invalides : {e_val!s}"}

        pyautogui.moveTo(x_real, y_real, duration=0.2)
        pyautogui.click(x_real, y_real, button=button_clean, clicks=clicks_val)
        return {
            "status": "success",
            "action": f"{clicks_val} clic(s) '{button_clean}' effectué(s) à ({x_real}, {y_real})",
            "coordinates_used": {"x": x_real, "y": y_real, "normalized": normalized},
            "current_position": pyautogui.position(),
        }
    except Exception as e:
        return {"status": "error", "message": f"Échec du clic de souris : {e!s}"}


@mcp.tool()
def gui_mouse_move(
    x: float, y: float, duration: float = 0.2, normalized: bool = False, monitor_index: int = 1
) -> dict[str, Any]:
    """
    Déplace la souris aux coordonnées (x, y) de manière fluide.
    """
    check_display_env()
    try:
        duration_val = max(0.0, float(duration))
        try:
            x_real, y_real = normalize_coordinates(x, y, normalized=normalized, monitor_index=monitor_index)
        except (ValueError, TypeError) as e_val:
            return {"status": "error", "message": f"Paramètres de coordonnées invalides : {e_val!s}"}

        pyautogui.moveTo(x_real, y_real, duration=duration_val)
        return {
            "status": "success",
            "action": f"Souris déplacée à ({x_real}, {y_real})",
            "coordinates_used": {"x": x_real, "y": y_real, "normalized": normalized},
            "current_position": pyautogui.position(),
        }
    except Exception as e:
        return {"status": "error", "message": f"Échec du déplacement de souris : {e!s}"}


@mcp.tool()
def gui_mouse_drag(
    x1: float, y1: float, x2: float, y2: float, duration: float = 0.5, normalized: bool = False, monitor_index: int = 1
) -> dict[str, Any]:
    """
    Glisse-dépose de souris du point (x1, y1) jusqu'au point (x2, y2).
    """
    check_display_env()
    try:
        duration_val = max(0.0, float(duration))
        try:
            x1_real, y1_real = normalize_coordinates(x1, y1, normalized=normalized, monitor_index=monitor_index)
            x2_real, y2_real = normalize_coordinates(x2, y2, normalized=normalized, monitor_index=monitor_index)
        except (ValueError, TypeError) as e_val:
            return {"status": "error", "message": f"Paramètres de coordonnées invalides : {e_val!s}"}

        pyautogui.moveTo(x1_real, y1_real)
        pyautogui.dragTo(x2_real, y2_real, duration=duration_val, button="left")
        return {
            "status": "success",
            "action": f"Glisser-déposer effectué de ({x1_real}, {y1_real}) à ({x2_real}, {y2_real})",
            "coordinates_used": {
                "from": {"x": x1_real, "y": y1_real},
                "to": {"x": x2_real, "y": y2_real},
                "normalized": normalized,
            },
        }
    except Exception as e:
        return {"status": "error", "message": f"Échec du glisser-déposer : {e!s}"}


def run_xdotool(args: list) -> bool:
    """Exécute une commande xdotool sous X11."""
    if not isinstance(args, list) or len(args) == 0:
        logger.error("Arguments invalides pour xdotool.")
        return False

    try:
        env = os.environ.copy()
        env["DISPLAY"] = env.get("DISPLAY", ":0")
        xdotool_bin = shutil.which("xdotool") or "/bin/xdotool"
        res = subprocess.run([xdotool_bin, *args], env=env, capture_output=True, check=False)
        stderr_txt = res.stderr.decode("utf-8", errors="replace").strip()
        if res.returncode != 0 or "No such key name" in stderr_txt or "Ignoring it" in stderr_txt:
            logger.error(f"Erreur xdotool {args}: exit code {res.returncode}, stderr: {stderr_txt}")
            return False
        return True
    except Exception as e:
        logger.error(f"Erreur xdotool {args}: {e}")
        return False


def sleep_human(base_delay: float = 0.05) -> None:
    """Introduit un délai pseudo-aléatoire réaliste pour simuler un humain."""
    if not isinstance(base_delay, (int, float)) or base_delay < 0:
        base_delay = 0.05
    import random

    jitter = random.normalvariate(base_delay, base_delay * 0.3)
    time.sleep(max(0.01, jitter))


def type_char_human(char: str) -> bool:
    """Saisit un unique caractère de façon indifférenciable."""
    if not isinstance(char, str) or len(char) != 1:
        return False
    success = run_xdotool(["type", char])
    sleep_human(0.06)
    return success


@mcp.tool()
def gui_keyboard_type(text: str, delay: float = 0.06) -> dict[str, Any]:
    """TAPE du texte caractère par caractère de façon humaine indifférenciable."""
    if not isinstance(text, str) or len(text) == 0:
        return {"status": "error", "message": "Le texte à taper ne peut pas être vide."}
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
    if not isinstance(key, str) or len(key) == 0:
        return ""
    key_map = {
        "super": "Super_L",
        "win": "Super_L",
        "enter": "Return",
        "return": "Return",
        "escape": "Escape",
        "esc": "Escape",
        "backspace": "BackSpace",
        "tab": "Tab",
        "space": "space",
        "ctrl": "control",
        "control": "control",
        "alt": "alt",
        "shift": "shift",
        "up": "Up",
        "down": "Down",
        "left": "Left",
        "right": "Right",
    }
    return key_map.get(key.lower(), key)


def press_shortcut_human(key: str) -> bool:
    """Simule séquentiellement un raccourci clavier complexe de façon humaine."""
    if not isinstance(key, str) or len(key) == 0:
        return False
    # Support direct de xdotool key si transmis avec la syntaxe X11 directe
    if "+" in key:
        parts = key.split("+")
        translated_parts = [translate_key(p.strip()) for p in parts]
        composite_key = "+".join(translated_parts)
        if run_xdotool(["key", "--clearmodifiers", composite_key]):
            return True
    keys = [translate_key(k.strip()) for k in key.split("+") if k.strip()]
    if not keys:
        return False
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
def gui_keyboard_press(key: str) -> dict[str, Any]:
    """APPUIE sur une touche ou une combinaison de touches de façon indifférenciable."""
    if not isinstance(key, str) or len(key) == 0:
        return {"status": "error", "message": "La touche ne peut pas être vide."}
    check_display_env()
    if press_shortcut_human(key):
        return {"status": "success", "action": f"Appui clavier indifférenciable effectué pour '{key}'"}
    return {"status": "error", "message": f"Échec de l'appui clavier pour '{key}'"}


@mcp.tool()
def gui_window_list() -> dict[str, Any]:
    """
    Liste toutes les fenêtres sous X11 avec leur ID, titre, PID et classe de fenêtre.
    Utilise xdotool, xprop et wmctrl (si disponible).
    """
    check_display_env()

    windows = []
    wmctrl_bin = shutil.which("wmctrl")
    xdotool_bin = shutil.which("xdotool") or "/bin/xdotool"
    xprop_bin = shutil.which("xprop") or "/usr/bin/xprop"

    try:
        if wmctrl_bin:
            try:
                out = subprocess.check_output([wmctrl_bin, "-lx"], stderr=subprocess.DEVNULL).decode("utf-8")
                for line in out.splitlines():
                    parts = line.split(maxsplit=4)
                    if len(parts) >= 5:
                        try:
                            wid = int(parts[0], 16)
                            pid_str = parts[2]
                            pid = int(pid_str) if pid_str.isdigit() and pid_str != "0" else None
                            win_class = parts[3]
                            title = parts[4]
                            windows.append({"id": wid, "title": title, "pid": pid, "wm_class": win_class})
                        except (ValueError, IndexError):
                            continue
            except Exception as e_wmctrl:
                logger.warning(f"Échec wmctrl -lx: {e_wmctrl}")

        if not windows:
            out = subprocess.check_output(
                [xdotool_bin, "search", "--onlyvisible", "--name", ".*"], stderr=subprocess.DEVNULL
            ).decode("utf-8")
            win_ids = [line.strip() for line in out.splitlines() if line.strip().isdigit()]
            for wid_str in win_ids:
                wid = int(wid_str)
                title = ""
                pid = None
                win_class = ""

                with contextlib.suppress(Exception):
                    title = (
                        subprocess.check_output([xdotool_bin, "getwindowname", str(wid)], stderr=subprocess.DEVNULL)
                        .decode("utf-8")
                        .strip()
                    )

                with contextlib.suppress(Exception):
                    pid_out = (
                        subprocess.check_output([xdotool_bin, "getwindowpid", str(wid)], stderr=subprocess.DEVNULL)
                        .decode("utf-8")
                        .strip()
                    )
                    if pid_out.isdigit():
                        pid = int(pid_out)

                with contextlib.suppress(Exception):
                    class_out = subprocess.check_output(
                        [xprop_bin, "-id", str(wid), "WM_CLASS"], stderr=subprocess.DEVNULL
                    ).decode("utf-8")
                    if "=" in class_out:
                        raw_classes = class_out.split("=", 1)[1].strip()
                        classes = [c.strip(' ",') for c in raw_classes.split(",") if c.strip(' ",')]
                        win_class = ".".join(classes) if classes else raw_classes

                if title or win_class:
                    windows.append({"id": wid, "title": title, "pid": pid, "wm_class": win_class})

        return {"status": "success", "windows": windows, "count": len(windows)}
    except Exception as e:
        logger.error(f"Erreur gui_window_list : {e!s}")
        return {"status": "error", "message": f"Échec de la liste des fenêtres : {e!s}"}


@mcp.tool()
def gui_window_focus(window_id: int) -> dict[str, Any]:
    """
    Active et met au premier plan une fenêtre X11 par son ID.
    """
    if not isinstance(window_id, int) or window_id <= 0:
        return {"status": "error", "message": "window_id doit être un entier positif."}
    check_display_env()
    xdotool_bin = shutil.which("xdotool") or "/bin/xdotool"

    try:
        subprocess.run([xdotool_bin, "windowactivate", str(window_id)], check=True, stderr=subprocess.PIPE)
        return {"status": "success", "message": f"Focus et activation effectués pour la fenêtre {window_id}"}
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode("utf-8").strip() if e.stderr else str(e)
        return {"status": "error", "message": f"Impossible d'activer la fenêtre {window_id} : {err_msg}"}
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de l'activation de la fenêtre : {e!s}"}


@mcp.tool()
def gui_window_resize_move(window_id: int, x: int, y: int, width: int, height: int) -> dict[str, Any]:
    """
    Déplace et redimensionne une fenêtre X11 par son ID.
    """
    if not isinstance(window_id, int) or window_id <= 0:
        return {"status": "error", "message": "window_id doit être un entier positif."}
    if not (isinstance(x, int) and isinstance(y, int) and isinstance(width, int) and isinstance(height, int)):
        return {"status": "error", "message": "Les paramètres x, y, width et height doivent être des entiers."}
    if width <= 0 or height <= 0:
        return {"status": "error", "message": "width et height doivent être strictly positifs."}

    check_display_env()
    xdotool_bin = shutil.which("xdotool") or "/bin/xdotool"

    try:
        subprocess.run(
            [xdotool_bin, "windowsize", str(window_id), str(width), str(height)], check=True, stderr=subprocess.PIPE
        )
        subprocess.run([xdotool_bin, "windowmove", str(window_id), str(x), str(y)], check=True, stderr=subprocess.PIPE)
        return {
            "status": "success",
            "message": f"Fenêtre {window_id} déplacée à ({x}, {y}) et redimensionnée à {width}x{height}",
            "window_id": window_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode("utf-8").strip() if e.stderr else str(e)
        return {
            "status": "error",
            "message": f"Échec du redimensionnement/déplacement de la fenêtre {window_id} : {err_msg}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la modification de la fenêtre : {e!s}"}


@mcp.tool()
def gui_window_close(window_id: int) -> dict[str, Any]:
    """
    Ferme proprement une fenêtre X11 par son ID via xdotool windowclose.
    """
    if not isinstance(window_id, int) or window_id <= 0:
        return {"status": "error", "message": "window_id doit être un entier positif."}
    check_display_env()
    xdotool_bin = shutil.which("xdotool") or "/bin/xdotool"

    try:
        subprocess.run([xdotool_bin, "windowclose", str(window_id)], check=True, stderr=subprocess.PIPE)
        return {"status": "success", "message": f"Fenêtre {window_id} fermée avec succès."}
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode("utf-8").strip() if e.stderr else str(e)
        return {"status": "error", "message": f"Échec de la fermeture de la fenêtre {window_id} : {err_msg}"}
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la fermeture de la fenêtre : {e!s}"}


@mcp.tool()
def gui_app_launch(command: str, background: bool = True) -> dict[str, Any]:
    """
    Lance une application X11 de manière non-bloquante ou synchrone.
    """
    if not isinstance(command, str) or not command.strip():
        return {"status": "error", "message": "La commande de lancement ne peut pas être vide."}

    check_display_env()
    env = os.environ.copy()
    env["DISPLAY"] = env.get("DISPLAY", ":0")

    cmd_args = shlex.split(command)
    if not cmd_args:
        return {"status": "error", "message": "Commande vide ou invalide."}

    try:
        if background:
            proc = subprocess.Popen(
                cmd_args, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True
            )
            return {
                "status": "success",
                "message": f"Application lancée en arrière-plan (PID: {proc.pid})",
                "pid": proc.pid,
                "command": command,
            }
        else:
            res = subprocess.run(cmd_args, env=env, capture_output=True, text=True, timeout=30, check=False)
            return {
                "status": "success" if res.returncode == 0 else "error",
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "command": command,
            }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"La commande a expiré (timeout 30s) : {command}"}
    except Exception as e:
        return {"status": "error", "message": f"Échec du lancement de l'application : {e!s}"}


@mcp.tool()
def gui_find_template(template_path: str, threshold: float = 0.8, monitor_index: int = 1) -> dict[str, Any]:
    """Recherche les coordonnées (x,y) d'une image modèle (template) sur l'écran."""
    check_display_env()
    if not isinstance(template_path, str) or not os.path.exists(template_path):
        return {"status": "error", "message": "Fichier template introuvable."}

    threshold_val = max(0.01, min(1.0, float(threshold)))
    screen_img = None
    try:
        import cv2
        import numpy as np

        screen_img = capture_screen_pil(monitor_index=monitor_index)
        screen_cv = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path)
        if template is None:
            return {"status": "error", "message": "Échec de lecture de l'image template."}

        res = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold_val:
            th, tw = template.shape[:2]
            mon_left, mon_top, _, _ = get_monitor_geometry(monitor_index)
            cx = mon_left + max_loc[0] + tw // 2
            cy = mon_top + max_loc[1] + th // 2
            return {"status": "success", "x": cx, "y": cy, "confidence": float(max_val)}
        return {"status": "not_found", "message": f"Template non trouvé. Confiance max : {max_val:.2f}"}
    except Exception as e:
        return {"status": "error", "message": f"Échec de la recherche : {e!s}"}
    finally:
        if screen_img is not None:
            with contextlib.suppress(Exception):
                screen_img.close()


@mcp.tool()
def gui_mouse_scroll(clicks: int, direction: str = "down") -> dict[str, Any]:
    """Simule un défilement vertical ou horizontal de molette de souris."""
    if not isinstance(clicks, int) or clicks <= 0:
        return {"status": "error", "message": "clicks doit être un entier positif."}
    dir_clean = str(direction).lower().strip()
    if dir_clean not in ["up", "down", "left", "right"]:
        return {"status": "error", "message": "direction doit être 'up', 'down', 'left' ou 'right'."}
    check_display_env()
    try:
        btn_map = {"up": "4", "down": "5", "left": "6", "right": "7"}
        btn = btn_map[dir_clean]
        for _ in range(clicks):
            run_xdotool(["click", btn])
            time.sleep(0.02)
        return {"status": "success", "action": f"Défilement de {clicks} pas vers le '{dir_clean}'"}
    except Exception as e:
        return {"status": "error", "message": f"Échec du défilement : {e!s}"}


@mcp.tool()
def gui_clipboard_set(text: str) -> dict[str, Any]:
    """
    Écrit du texte dans le presse-papier système X11.
    Utilise pyperclip avec fallback sur xclip / xsel via subprocess si nécessaire.
    """
    if not isinstance(text, str):
        return {"status": "error", "message": "Le paramètre 'text' doit être une chaîne de caractères."}
    check_display_env()

    # Tentative via pyperclip
    try:
        import pyperclip

        pyperclip.copy(text)
        return {
            "status": "success",
            "action": "Texte copié dans le presse-papier",
            "length": len(text),
            "method": "pyperclip",
        }
    except Exception as e_clip:
        logger.warning(f"Échec pyperclip.copy: {e_clip}. Tentative via xclip...")

    # Fallback via xclip
    xclip_bin = shutil.which("xclip")
    if xclip_bin:
        try:
            env = os.environ.copy()
            env["DISPLAY"] = env.get("DISPLAY", ":0")
            proc = subprocess.Popen([xclip_bin, "-selection", "clipboard"], stdin=subprocess.PIPE, env=env)
            proc.communicate(input=text.encode("utf-8"), timeout=5)
            if proc.returncode == 0:
                return {
                    "status": "success",
                    "action": "Texte copié dans le presse-papier",
                    "length": len(text),
                    "method": "xclip",
                }
        except Exception as e_xclip:
            logger.warning(f"Échec xclip: {e_xclip}")

    # Fallback via xsel
    xsel_bin = shutil.which("xsel")
    if xsel_bin:
        try:
            env = os.environ.copy()
            env["DISPLAY"] = env.get("DISPLAY", ":0")
            proc = subprocess.Popen([xsel_bin, "--clipboard", "--input"], stdin=subprocess.PIPE, env=env)
            proc.communicate(input=text.encode("utf-8"), timeout=5)
            if proc.returncode == 0:
                return {
                    "status": "success",
                    "action": "Texte copié dans le presse-papier",
                    "length": len(text),
                    "method": "xsel",
                }
        except Exception as e_xsel:
            logger.warning(f"Échec xsel: {e_xsel}")

    return {
        "status": "error",
        "message": "Impossible d'écrire dans le presse-papier. pyperclip, xclip et xsel ont échoué ou ne sont pas disponibles.",
    }


@mcp.tool()
def gui_clipboard_get() -> dict[str, Any]:
    """
    Lit et retourne le texte du presse-papier système X11.
    Utilise pyperclip avec fallback sur xclip / xsel.
    """
    check_display_env()

    # Tentative via pyperclip
    try:
        import pyperclip

        content = pyperclip.paste()
        if content is not None:
            return {"status": "success", "text": content, "length": len(content), "method": "pyperclip"}
    except Exception as e_clip:
        logger.warning(f"Échec pyperclip.paste: {e_clip}. Tentative via xclip...")

    # Fallback via xclip
    xclip_bin = shutil.which("xclip")
    if xclip_bin:
        try:
            env = os.environ.copy()
            env["DISPLAY"] = env.get("DISPLAY", ":0")
            out = subprocess.check_output(
                [xclip_bin, "-selection", "clipboard", "-o"], env=env, stderr=subprocess.DEVNULL, timeout=5
            ).decode("utf-8", errors="replace")
            return {"status": "success", "text": out, "length": len(out), "method": "xclip"}
        except Exception as e_xclip:
            logger.warning(f"Échec xclip -o: {e_xclip}")

    # Fallback via xsel
    xsel_bin = shutil.which("xsel")
    if xsel_bin:
        try:
            env = os.environ.copy()
            env["DISPLAY"] = env.get("DISPLAY", ":0")
            out = subprocess.check_output(
                [xsel_bin, "--clipboard", "--output"], env=env, stderr=subprocess.DEVNULL, timeout=5
            ).decode("utf-8", errors="replace")
            return {"status": "success", "text": out, "length": len(out), "method": "xsel"}
        except Exception as e_xsel:
            logger.warning(f"Échec xsel --output: {e_xsel}")

    return {
        "status": "error",
        "message": "Impossible de lire le presse-papier. pyperclip, xclip et xsel ont échoué ou ne sont pas disponibles.",
    }


def _ocr_extract_text_boxes(image: Image.Image) -> list[dict[str, Any]]:
    """
    Extrait les boîtes de texte et confiances d'une image PIL via les moteurs OCR disponibles.
    Tente pytesseract en premier, puis RapidOCR.
    Retourne une liste de dicts: [{"text": str, "x": int, "y": int, "w": int, "h": int, "conf": float}]
    """
    boxes = []

    # 1. Tentative avec pytesseract
    try:
        import pytesseract

        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        n_boxes = len(data["text"])
        for i in range(n_boxes):
            txt = data["text"][i].strip()
            conf_val = float(data["conf"][i])
            if txt and conf_val > 0:
                boxes.append(
                    {
                        "text": txt,
                        "x": int(data["left"][i]),
                        "y": int(data["top"][i]),
                        "w": int(data["width"][i]),
                        "h": int(data["height"][i]),
                        "conf": conf_val / 100.0,
                    }
                )
        if boxes:
            return boxes
    except ImportError:
        logger.debug("pytesseract non disponible.")
    except Exception as e_tess:
        # Intercepte TesseractNotFoundError (et toute autre exception liée au binaire tesseract absente ou échec)
        logger.info(f"pytesseract non disponible ou binaire absente ({type(e_tess).__name__}), bascule sur RapidOCR.")

    # 2. Tentative avec RapidOCR / rapidocr_onnxruntime / rapidocr
    try:
        import numpy as np

        rapid_engine = None
        for mod_name in ["rapidocr_onnxruntime", "rapidocr_onnx", "rapidocr"]:
            try:
                mod = __import__(mod_name, fromlist=["RapidOCR"])
                rapid_engine = mod.RapidOCR()
                break
            except ImportError:
                continue

        if rapid_engine is not None:
            img_np = np.array(image)
            result, _ = rapid_engine(img_np)
            if result:
                for item in result:
                    # item format: [dt_boxes, text, score]
                    dt_box, txt, score = item[0], item[1], float(item[2])
                    xs = [pt[0] for pt in dt_box]
                    ys = [pt[1] for pt in dt_box]
                    min_x, max_x = int(min(xs)), int(max(xs))
                    min_y, max_y = int(min(ys)), int(max(ys))
                    boxes.append(
                        {
                            "text": txt.strip(),
                            "x": min_x,
                            "y": min_y,
                            "w": max_x - min_x,
                            "h": max_y - min_y,
                            "conf": score,
                        }
                    )
            if boxes:
                return boxes
    except Exception as e_rapid:
        logger.warning(f"Erreur RapidOCR: {e_rapid}")

    return boxes


@mcp.tool()
def gui_find_text(text: str, confidence: float = 0.6, monitor_index: int = 1) -> dict[str, Any]:
    """
    Prend une capture d'écran, utilise l'OCR (pytesseract / RapidOCR) pour détecter l'emplacement
    du texte 'text', et retourne son centre (x, y) et sa confiance.
    """
    if not isinstance(text, str) or not text.strip():
        return {"status": "error", "message": "Le texte recherché ne peut pas être vide."}

    try:
        conf_threshold = max(0.0, min(1.0, float(confidence)))
    except (ValueError, TypeError):
        return {"status": "error", "message": "confidence doit être un nombre flottant entre 0.0 et 1.0."}

    if not isinstance(monitor_index, int) or monitor_index < 0:
        return {"status": "error", "message": "monitor_index doit être un entier positif ou nul."}

    check_display_env()

    screen_img = None
    try:
        screen_img = capture_screen_pil(monitor_index=monitor_index)
        mon_left, mon_top, _, _ = get_monitor_geometry(monitor_index)

        boxes = _ocr_extract_text_boxes(screen_img)

        if not boxes:
            return {
                "status": "error",
                "message": "Aucun moteur OCR disponible ou aucun texte extrait de l'écran. Installez pytesseract ou rapidocr_onnx.",
            }

        target_clean = text.strip().lower()

        # Recherche de correspondance exacte ou partielle sans interprétation regex
        best_match = None
        highest_conf = -1.0

        for box in boxes:
            box_txt_clean = box["text"].lower()
            if (
                box["conf"] >= conf_threshold
                and (target_clean == box_txt_clean or target_clean in box_txt_clean)
                and box["conf"] > highest_conf
            ):
                highest_conf = box["conf"]
                best_match = box

        if best_match:
            center_x = mon_left + best_match["x"] + best_match["w"] // 2
            center_y = mon_top + best_match["y"] + best_match["h"] // 2
            return {
                "status": "success",
                "text_found": best_match["text"],
                "x": center_x,
                "y": center_y,
                "confidence": round(best_match["conf"], 4),
                "bbox": [mon_left + best_match["x"], mon_top + best_match["y"], best_match["w"], best_match["h"]],
            }

        return {
            "status": "not_found",
            "message": f"Texte '{text}' non trouvé sur l'écran (seuil de confiance : {conf_threshold}).",
        }

    except Exception as e:
        logger.error(f"Erreur gui_find_text: {e}")
        return {"status": "error", "message": f"Échec de la recherche de texte par OCR : {e!s}"}
    finally:
        if screen_img is not None:
            with contextlib.suppress(Exception):
                screen_img.close()


@mcp.tool()
def gui_click_text(text: str, button: str = "left", clicks: int = 1, monitor_index: int = 1) -> dict[str, Any]:
    """
    Recherche 'text' sur l'écran via l'OCR et clique automatiquement en son centre s'il est trouvé.
    """
    find_res = gui_find_text(text=text, confidence=0.5, monitor_index=monitor_index)
    if find_res.get("status") != "success":
        return find_res

    cx = find_res["x"]
    cy = find_res["y"]

    click_res = gui_mouse_click(x=cx, y=cy, button=button, clicks=clicks, normalized=False, monitor_index=monitor_index)

    if click_res.get("status") == "success":
        click_res["ocr_text_found"] = find_res["text_found"]
        click_res["ocr_confidence"] = find_res["confidence"]

    return click_res


# ==============================================================================
# BRIQUE 4 : PONT HYBRIDE WEB & AUDIT VIDÉO
# ==============================================================================

# Variable globale pour suivre le sous-processus d'enregistrement vidéo actif
_video_recording_process: subprocess.Popen | None = None
_video_recording_file: str | None = None


@mcp.tool()
async def gui_web_action(
    url: str,
    action: str = "aria_tree",
    selector: str | None = None,
    text: str | None = None,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    timeout_ms: int = 30000,
) -> dict[str, Any]:
    """
    Exécute des actions Web déterministes et d'inspection ARIA/DOM via Playwright (Headless).
    Actions supportées : 'aria_tree', 'click', 'type', 'screenshot'.
    """
    import asyncio

    if not isinstance(url, str) or not url.strip():
        return {"status": "error", "message": "L'URL ne peut pas être vide."}

    action_clean = str(action).lower().strip()
    valid_actions = ["aria_tree", "click", "type", "screenshot"]
    if action_clean not in valid_actions:
        return {"status": "error", "message": f"Action invalide : '{action}'. Actions valides : {valid_actions}."}

    if action_clean in ["click", "type"] and not selector:
        return {"status": "error", "message": f"L'action '{action_clean}' nécessite un paramètre 'selector'."}

    if action_clean == "type" and text is None:
        return {"status": "error", "message": "L'action 'type' nécessite un paramètre 'text'."}

    try:
        vp_w = max(320, min(7680, int(viewport_width)))
        vp_h = max(240, min(4320, int(viewport_height)))
    except (ValueError, TypeError):
        return {"status": "error", "message": "viewport_width et viewport_height doivent être des entiers positifs."}

    try:
        t_ms = max(500, min(300000, int(timeout_ms)))
    except (ValueError, TypeError):
        return {"status": "error", "message": "timeout_ms doit être un entier positif (en ms)."}

    url_clean = url.strip()
    if not (
        url_clean.startswith("http://")
        or url_clean.startswith("https://")
        or url_clean.startswith("file://")
        or url_clean.startswith("about:")
    ):
        url_clean = "https://" + url_clean

    def _sync_playwright_work() -> dict[str, Any]:
        """Exécute les opérations synchrones Playwright dans un thread isolé."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "status": "error",
                "message": "Le package 'playwright' n'est pas installé dans le système/environnement.",
            }

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(viewport={"width": vp_w, "height": vp_h})
                page = context.new_page()
                page.set_default_timeout(t_ms)

                page.goto(url_clean, wait_until="domcontentloaded")

                result: dict[str, Any] = {"status": "success", "url": page.url, "title": page.title()}

                if action_clean == "aria_tree":
                    try:
                        aria_text = page.locator("body").aria_snapshot()
                    except Exception as e_aria:
                        logger.warning(f"Échec locator.aria_snapshot: {e_aria}")
                        aria_text = "Arbre ARIA indisponible."
                    result["aria_tree"] = aria_text

                elif action_clean == "click":
                    if not selector:
                        return {
                            "status": "error",
                            "message": "Le paramètre 'selector' est requis pour l'action 'click'.",
                        }
                    page.click(selector)
                    result["action_performed"] = f"Clic effectué sur le sélecteur '{selector}'"

                elif action_clean == "type":
                    if not selector:
                        return {
                            "status": "error",
                            "message": "Le paramètre 'selector' est requis pour l'action 'type'.",
                        }
                    page.fill(selector, text or "")
                    result["action_performed"] = f"Texte '{text}' saisi dans le sélecteur '{selector}'"

                elif action_clean == "screenshot":
                    timestamp = int(time.time())
                    screenshot_filename = f"web_screenshot_{timestamp}.png"
                    screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
                    page.screenshot(path=screenshot_path, full_page=False)

                    result["screenshot_path"] = screenshot_path
                    result["action_performed"] = f"Capture d'écran Web enregistrée à {screenshot_path}"

                return result
            finally:
                with contextlib.suppress(Exception):
                    context.close()
                with contextlib.suppress(Exception):
                    browser.close()

    try:
        res = await asyncio.to_thread(_sync_playwright_work)
        return res
    except Exception as e:
        logger.error(f"Erreur gui_web_action : {e!s}")
        return {"status": "error", "message": f"Échec de l'action Web ({action_clean}) : {e!s}"}


@mcp.tool()
def gui_start_video_recording(
    output_path: str | None = None, fps: int = 5, monitor_index: int = 1, duration: int | None = None
) -> dict[str, Any]:
    """
    Démarre l'enregistrement vidéo à faible rafraîchissement (5 FPS par défaut) sous X11 via ffmpeg.
    """
    global _video_recording_process, _video_recording_file

    try:
        fps_val = max(1, min(30, int(fps)))
    except (ValueError, TypeError):
        return {"status": "error", "message": "fps doit être un entier entre 1 et 30."}

    try:
        mon_idx = int(monitor_index)
    except (ValueError, TypeError):
        return {"status": "error", "message": "monitor_index doit être un entier positif ou nul."}

    dur_val = None
    if duration is not None:
        try:
            dur_val = int(duration)
            if dur_val <= 0:
                return {"status": "error", "message": "duration doit être un entier strictement positif."}
        except (ValueError, TypeError):
            return {"status": "error", "message": "duration doit être un entier valide."}

    if _video_recording_process is not None:
        if _video_recording_process.poll() is None:
            return {
                "status": "error",
                "message": f"Un enregistrement vidéo est déjà en cours (Fichier: {_video_recording_file}, PID: {_video_recording_process.pid}).",
            }
        else:
            # Nettoyer les ressources de l'ancien processus terminé/tué
            with contextlib.suppress(Exception):
                for stream in [
                    _video_recording_process.stdin,
                    _video_recording_process.stdout,
                    _video_recording_process.stderr,
                ]:
                    if stream:
                        stream.close()
            _video_recording_process = None
            _video_recording_file = None

    check_display_env()

    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        return {"status": "error", "message": "Le binaire 'ffmpeg' n'est pas installé sur le système."}

    if not output_path:
        timestamp = int(time.time())
        output_path = os.path.join(SCREENSHOTS_DIR, f"recording_{timestamp}.mp4")

    # S'assurer que le dossier parent existe
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    except Exception as e_dir:
        return {"status": "error", "message": f"Impossible de créer le dossier pour le fichier vidéo : {e_dir}"}

    display_str = os.environ.get("DISPLAY", ":0")

    try:
        left, top, width, height = get_monitor_geometry(mon_idx)
    except Exception as e:
        logger.warning(f"Impossible de lire la géométrie du moniteur {mon_idx}: {e}. Utilisation de la taille totale.")
        left, top, width, height = 0, 0, 1920, 1080

    # ffmpeg nécessite que la largeur et la hauteur soient des nombres pairs
    width = width if width % 2 == 0 else width - 1
    height = height if height % 2 == 0 else height - 1

    cmd = [
        ffmpeg_bin,
        "-y",
        "-video_size",
        f"{width}x{height}",
        "-framerate",
        str(fps_val),
        "-f",
        "x11grab",
        "-i",
        f"{display_str}.0+{left},{top}",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-pix_fmt",
        "yuv420p",
    ]

    if dur_val:
        cmd.extend(["-t", str(dur_val)])

    cmd.append(output_path)

    try:
        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True
        )
        time.sleep(0.2)
        if proc.poll() is not None:
            # Le processus a échoué au démarrage
            for stream in [proc.stdin, proc.stdout, proc.stderr]:
                if stream:
                    with contextlib.suppress(Exception):
                        stream.close()
            return {"status": "error", "message": "Le processus ffmpeg a quitté immédiatement après le démarrage."}

        _video_recording_process = proc
        _video_recording_file = output_path

        return {
            "status": "success",
            "message": f"Enregistrement vidéo démarré à {fps_val} FPS (PID: {proc.pid})",
            "output_path": output_path,
            "fps": fps_val,
            "pid": proc.pid,
        }
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'enregistrement vidéo: {e}")
        _video_recording_process = None
        _video_recording_file = None
        return {"status": "error", "message": f"Échec du démarrage de l'enregistrement vidéo : {e!s}"}


@mcp.tool()
def gui_stop_video_recording() -> dict[str, Any]:
    """
    Arrête l'enregistrement vidéo en cours proprement sans fuite de descripteurs de fichiers.
    """
    global _video_recording_process, _video_recording_file

    if _video_recording_process is None:
        return {"status": "error", "message": "Aucun enregistrement vidéo n'est en cours."}

    proc = _video_recording_process
    filepath = _video_recording_file

    _video_recording_process = None
    _video_recording_file = None

    try:
        if proc.poll() is None:
            # Envoyer 'q' sur stdin pour que ffmpeg finalise proprement le conteneur MP4
            if proc.stdin:
                with contextlib.suppress(Exception):
                    proc.stdin.write(b"q\n")
                    proc.stdin.flush()

            # Attendre 3 secondes la fermeture propre
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # Si ffmpeg ne s'arrête pas, envoyer SIGTERM puis SIGKILL
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=1)

        file_exists = os.path.exists(filepath) if filepath else False
        file_size = os.path.getsize(filepath) if (file_exists and filepath) else 0

        return {
            "status": "success",
            "message": "Enregistrement vidéo arrêté avec succès.",
            "output_path": filepath,
            "file_exists": file_exists,
            "file_size_bytes": file_size,
        }

    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt de l'enregistrement vidéo: {e}")
        return {"status": "error", "message": f"Échec de l'arrêt de l'enregistrement vidéo : {e!s}"}
    finally:
        # Garantir la fermeture stricte de tous les descripteurs de fichiers
        for stream in [proc.stdin, proc.stdout, proc.stderr]:
            if stream:
                with contextlib.suppress(Exception):
                    stream.close()


def main() -> None:
    """Point d'entrée principal pour démarrer le serveur MCP GUI Agent."""
    logger.info("Démarrage du serveur MCP GUI Agent...")
    check_display_env()
    mcp.run()


if __name__ == "__main__":
    main()
