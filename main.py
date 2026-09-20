import os
import sys
import time
from config.loader import load_json, find_model_by_role
from core.commands import switch_to_main, switch_to_uncensored, switch_via_menu
from core.confidence import calculate_confidence
from core.display import print_banner, print_response, build_prompt_prefix, print_help, print_error, print_time_taken
from core.engines.ollama_engine import OllamaEngine
from core.state import AppState
from utils.colors import colorize, VIOLET, YELLOW, BLUE, GRAY
from utils.device import detect_device, get_device_display
from utils.loading import LoadingAnimation
from utils.process import kill_ollama_process, get_manual_kill_command, get_manual_kill_hint, clear_terminal
from utils.validators import is_unrecognized_command, validate_prompt

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
MODELS_PATH = os.path.join(CONFIG_DIR, "models.json")

def print_current_banner(state: AppState, models_registry: dict, device_type: str) -> None:
    model_info = models_registry.get(state.active_model, {})
    cutoff_date = model_info.get("cutoff", "unknown")
    engine_name = model_info.get("engine", "unknown")

    print_banner(cutoff_date, state.is_uncensored)
    print(f"Device: {get_device_display(device_type)}")

    agent_label = colorize("AI Agent: ", VIOLET)
    agent_value = colorize(state.active_model, YELLOW)
    engine_label = colorize("Engine: ", VIOLET)
    engine_value = colorize(engine_name, YELLOW)
    print(f"{agent_label} {agent_value}\t{engine_label} {engine_value}")
    
    context_label = colorize("Context Window: ", VIOLET)
    context_value = colorize(f"{state.engine.context_window:,} tokens", YELLOW)
    print(f"{context_label}{context_value}")

    print()
    print_help()

def build_engine(model_name: str, models_registry: dict, device_type: str) -> OllamaEngine:
    model_info = models_registry.get(model_name, {})
    if device_type == "phone":
        context_window = model_info.get("context_window_phone", 4096)
        num_predict = model_info.get("num_predict_phone", 1024)
    else:
        context_window = model_info.get("context_window_pc", 4096)
        num_predict = model_info.get("num_predict_pc", 1024)
    return OllamaEngine(model_name=model_name, context_window=context_window, num_predict=num_predict)

def main() -> None:
    models_registry = load_json(MODELS_PATH)
    device_type = detect_device()

    default_model = find_model_by_role(models_registry, "main", device_type)
    if not default_model:
        print_error("No 'main' model found for this device in models.json")
        sys.exit(1)

    state = AppState(
        active_model=default_model,
        is_uncensored=False,
        engine=build_engine(default_model, models_registry, device_type),
    )
    
    conversation_contexts = {}

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
                command_label = colorize("Command: ", BLUE)
                command_value = colorize(get_manual_kill_command(), BLUE)
                print(f"{command_label}{command_value}")

                hint = get_manual_kill_hint()
                if hint:
                    hint_label = colorize("Hint: ", YELLOW)
                    hint_value = colorize(hint, GRAY)
                    print(f"{hint_label}{hint_value}")
            break

        if stripped_input == "/help":
            print_help()
            continue
        if stripped_input == "/clear":
            clear_terminal()
            print_current_banner(state, models_registry, device_type)
            continue

        previous_model = state.active_model

        if stripped_input == "/main":
            state = switch_to_main(state, models_registry, device_type, build_engine)
        elif stripped_input == "/uncensored":
            state = switch_to_uncensored(state, models_registry, device_type, build_engine)
        elif stripped_input == "/models":
            state = switch_via_menu(state, models_registry, device_type, build_engine)

        if stripped_input in ("/main", "/uncensored", "/models"):
            if state.active_model != previous_model:
                print_current_banner(state, models_registry, device_type)
            continue

        if is_unrecognized_command(stripped_input):
            print_error(f"Unknown command '{stripped_input}'. Type /help to see available commands.")
            continue

        is_valid, cleaned_input = validate_prompt(user_input)
        if not is_valid:
            continue

        animation = LoadingAnimation()
        animation.start()

        def handle_retry():
            animation.notify_retry()

        existing_context = conversation_contexts.get(state.active_model)

        start_time = time.time()

        try:
            result = state.engine.generate(
                cleaned_input,
                context=existing_context,
                on_retry=handle_retry,
            )
        except RuntimeError as error:
            animation.stop()
            print_error(f"{error}")
            if "not found" in str(error).lower():
                command_label = colorize("Command: ", BLUE)
                command_value = colorize(f"ollama pull {state.active_model}", GRAY)
                print(f"{command_label}{command_value}")
            print()
            continue

        animation.stop()
        elapsed_seconds = time.time() - start_time

        conversation_contexts[state.active_model] = result["context"]

        confidence_percent = calculate_confidence(result["logprobs"])
        print_response(confidence_percent, result["text"])

        if elapsed_seconds > 30:
            print_time_taken(elapsed_seconds)

if __name__ == "__main__":
    main()