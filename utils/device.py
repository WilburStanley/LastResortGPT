import os
import platform
from utils.colors import colorize, GREEN, RED

def detect_device() -> str:
    """Returns "phone", "pc", or "unknown" based on the runtime environment."""
    android_markers = ["/system/build.prop", "/system/bin/app_process"]
    has_android_file_marker = any(os.path.exists(path) for path in android_markers)

    prefix_value = os.environ.get("PREFIX", "")
    has_termux_env = "com.termux" in prefix_value

    is_android = has_android_file_marker or has_termux_env

    system_name = platform.system()
    known_desktop_systems = {"Windows", "Darwin", "Linux"}

    if is_android:
        return colorize("PHONE", GREEN)

    if system_name in known_desktop_systems:
        return colorize("PC", GREEN)

    return colorize("UNKNOWN", RED)