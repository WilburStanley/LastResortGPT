from config.loader import find_model_by_role
from core.display import print_error, print_models_menu
from core.engines.ollama_engine import OllamaEngine
from core.state import AppState

def switch_to_main(state: AppState, models_registry: dict) -> AppState:
    main_model = find_model_by_role(models_registry, "main")
    if not main_model:
        print_error("No model with role 'main' found in models.json")
        return state
    return AppState(active_model=main_model, is_uncensored=False, engine=OllamaEngine(model_name=main_model))

def switch_to_uncensored(state: AppState, models_registry: dict) -> AppState:
    uncensored_model = find_model_by_role(models_registry, "uncensored")
    if not uncensored_model:
        print_error("No model with role 'uncensored' found in models.json")
        return state
    return AppState(active_model=uncensored_model, is_uncensored=True, engine=OllamaEngine(model_name=uncensored_model))

def switch_via_menu(state: AppState, models_registry: dict) -> AppState:
    selected_model = print_models_menu(models_registry)
    if not selected_model:
        return state
    is_uncensored = models_registry[selected_model].get("role") == "uncensored"
    return AppState(active_model=selected_model, is_uncensored=is_uncensored, engine=OllamaEngine(model_name=selected_model))