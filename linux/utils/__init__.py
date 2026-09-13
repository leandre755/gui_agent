"""Utilitaires et drivers partagés pour gui_agent."""

from . import coordinates, human_mimic, video
from .coordinates import get_monitor_geometry, normalize_coordinates
from .human_mimic import generate_smooth_path, sleep_human, type_char_human
from .video import validate_video_recording_params

__all__ = [
    "coordinates",
    "generate_smooth_path",
    "get_monitor_geometry",
    "human_mimic",
    "normalize_coordinates",
    "sleep_human",
    "type_char_human",
    "validate_video_recording_params",
    "video",
]
