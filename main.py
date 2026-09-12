import json
import os
import sys

from core.confidence import calculate_confidence
from core.display import print_banner, print_response, PROMPT_PREFIX
from core.engines.ollama_engine import OllamaEngine
from utils.colors import colorize, RED
from utils.device import detect_device
from utils.loading import LoadingAnimation

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
MODELS_PATH = os.path.join(CONFIG_DIR, "models.json")

def load_json(path: str) -> dict:
    with open(path, "r") as file:
        return json.load(file)

def main() -> None:
    settings = load_json(SETTINGS_PATH)
    models_registry = load_json(MODELS_PATH)

    active_model = settings["active_model"]
    model_info = models_registry.get(active_model, {})
    cutoff_date = model_info.get("cutoff", "unknown")

    device_type = detect_device()
    engine = OllamaEngine(model_name=active_model)

    if not engine.is_available():
        print(colorize("Ollama is not running. Start it manually, then try again.", RED))
        print(colorize("Run: ollama serve > /dev/null 2>&1 &", RED))
        sys.exit(1)

    print_banner(cutoff_date)
    print(f"Device: {device_type}")
    print()

    while True:
        user_input = input(PROMPT_PREFIX)

        if user_input.strip().lower() in ("exit", "quit"):
            break
        if not user_input.strip():
            continue

        animation = LoadingAnimation()
        animation.start()
        result = engine.generate(user_input)
        animation.stop()
        confidence_percent = calculate_confidence(result["logprobs"])

        print_response(confidence_percent, result["text"])

if __name__ == "__main__":
    main()