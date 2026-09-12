import platform
import subprocess

from core.display import print_error

def kill_ollama_process() -> bool:
    system_name = platform.system()
    try:
        if system_name == "Windows":
            result = subprocess.run(
                ["taskkill", "/IM", "ollama.exe", "/F"],
                capture_output=True,
                text=True,
            )
        elif system_name in ("Linux", "Darwin"):
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
    elif system_name in ("Linux", "Darwin"):
        return "pkill ollama"
    else:
        return "Manually close Ollama using your system's process manager."