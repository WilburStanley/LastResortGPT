import os
import platform

def detect_device() -> str:
    """Returns "phone", "pc", or "unknown" based on the runtime environment."""
    android_markers = ["/system/build.prop", "/system/bin/app_process"]
    is_android = any(os.path.exists(path) for path in android_markers)

    system_name = platform.system()
    known_desktop_systems = {"Windows", "Darwin", "Linux"}

    if is_android:
        return "phone"
    if system_name in known_desktop_systems:
        return "pc"

    return "unknown"