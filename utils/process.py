import platform
import subprocess

from core.display import print_error

LINUX_LIKE_SYSTEMS = ("Linux", "Darwin", "Android")

def kill_ollama_process() -> bool:
    system_name = platform.system()
    try:
        if system_name == "Windows":
            result = subprocess.run(
                ["taskkill", "/IM", "ollama.exe", "/F"],
                capture_output=True,
                text=True,
            )
        elif system_name in LINUX_LIKE_SYSTEMS:
            result = subprocess.run(
                ["pkill", "ollama"],
                capture_output=True,
                text=True,
            )
        else:
            print_error(f"Unsupported OS '{system_name}' for shutting down Ollama")
            return False

        return result.returncode == 0
    except FileNotFoundError:
        print_error("Could not find the process manager command for this system.")
        return False


def get_manual_kill_command() -> str:
    system_name = platform.system()
    if system_name == "Windows":
        return "taskkill /IM ollama.exe /F"
    elif system_name in LINUX_LIKE_SYSTEMS:
        return "pkill ollama"
    else:
        return "Manually close Ollama using your system's process manager."

def get_manual_kill_hint() -> str:
    system_name = platform.system()
    if system_name == "Windows":
        return "On Windows, try running your terminal as Administrator to allow this to work automatically."
    elif system_name in LINUX_LIKE_SYSTEMS:
        return "Try running the command above directly in your terminal."
    else:
        return ""

def clear_terminal() -> None:
    system_name = platform.system()
    if system_name == "Windows":
        subprocess.run(["cls"], shell=True, check=False)
    else:
        subprocess.run(["clear"], check=False)