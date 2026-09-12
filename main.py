import os
import sys

from config.loader import load_json
from core.commands import switch_to_main, switch_to_uncensored, switch_via_menu
from core.confidence import calculate_confidence
from core.display import print_banner, print_response, build_prompt_prefix, print_help, print_error
from core.engines.ollama_engine import OllamaEngine
from core.state import AppState
from utils.colors import colorize, GREEN, VIOLET, YELLOW, BLUE
from utils.device import detect_device
from utils.loading import LoadingAnimation
from utils.process import kill_ollama_process, get_manual_kill_command, get_manual_kill_hint

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
MODELS_PATH = os.path.join(CONFIG_DIR, "models.json")

def print_current_banner(state: AppState, models_registry: dict, device_type: str) -> None:
    model_info = models_registry.get(state.active_model, {})
    cutoff_date = model_info.get("cutoff", "unknown")
    engine_name = model_info.get("engine", "unknown")

    print_banner(cutoff_date, state.is_uncensored)
    print(f"Device: {device_type}")

    agent_label = colorize("AI Agent: ", VIOLET)
    agent_value = colorize(state.active_model, YELLOW)
    engine_label = colorize("Engine: ", VIOLET)
    engine_value = colorize(engine_name, YELLOW)
    print(f"{agent_label} {agent_value}\t{engine_label} {engine_value}")

    print()
    print_help()


def main() -> None:
    settings = load_json(SETTINGS_PATH)
    models_registry = load_json(MODELS_PATH)

    default_model = settings["active_model"]
    device_type = detect_device()

    state = AppState(
        active_model=default_model,
        is_uncensored=False,
        engine=OllamaEngine(model_name=default_model),
    )

    if not state.engine.is_available():
        print_error("Ollama is not running. Start it manually, then try again.")
        print(colorize("Run: ollama serve > /dev/null 2>&1 &", BLUE))
        sys.exit(1)

    print_current_banner(state, models_registry, device_type)

    while True:
        prompt_prefix = build_prompt_prefix(state.is_uncensored)
        user_input = input(prompt_prefix)
        stripped_input = user_input.strip().lower()

        if stripped_input in ("exit", "quit", "/exit"):
            stopped_successfully = kill_ollama_process()
            if stopped_successfully:
                print("Ollama server stopped. Goodbye.")
            else:
                print_error("Could not stop the Ollama server. It may need to be closed manually.")
                print(f"Run this yourself: {get_manual_kill_command()}")
                hint = get_manual_kill_hint()
                if hint:
                    print(f"({hint})")
            break

        if stripped_input == "/help":
            print_help()
            continue

        previous_model = state.active_model

        if stripped_input == "/main":
            state = switch_to_main(state, models_registry)
        elif stripped_input == "/uncensored":
            state = switch_to_uncensored(state, models_registry)
        elif stripped_input == "/models":
            state = switch_via_menu(state, models_registry)

        if stripped_input in ("/main", "/uncensored", "/models"):
            if state.active_model != previous_model:
                print_current_banner(state, models_registry, device_type)
            continue

        if not user_input.strip():
            continue

        animation = LoadingAnimation()
        animation.start()

        try:
            result = state.engine.generate(user_input)
        except RuntimeError as error:
            animation.stop()
            print_error(f"{error}")
            print()
            continue

        animation.stop()
        confidence_percent = calculate_confidence(result["logprobs"])
        print_response(confidence_percent, result["text"])

if __name__ == "__main__":
    main()