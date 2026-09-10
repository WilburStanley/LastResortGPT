import json
import os
import sys

from core.confidence import calculate_confidence
from core.display import print_banner, print_prompt_line, print_response
from core.engines.ollama_engine import OllamaEngine
from utils.device import detect_device

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
        print("Ollama is not running. Start it manually, then try again.")
        print("Run: ollama serve")
        sys.exit(1)

    print_banner(cutoff_date)
    print(f"Device: {device_type}")
    print()

    while True:
        user_input = input("commandline$ ")

        if user_input.strip().lower() in ("exit", "quit"):
            break
        if not user_input.strip():
            continue

        result = engine.generate(user_input)
        confidence_percent = calculate_confidence(result["logprobs"])

        print_response(confidence_percent, result["text"])

if __name__ == "__main__":
    main()