from config.loader import find_model_by_role
from core.display import print_error, print_models_menu
from core.state import AppState

def switch_to_main(state: AppState, models_registry: dict, device_type: str, build_engine) -> AppState:
    main_model = find_model_by_role(models_registry, "main", device_type)
    if not main_model:
        print_error("No model with role 'main' found for this device in models.json")
        return state
    engine = build_engine(main_model, models_registry, device_type)
    return AppState(active_model=main_model, is_uncensored=False, engine=engine)

def switch_to_uncensored(state: AppState, models_registry: dict, device_type: str, build_engine) -> AppState:
    uncensored_model = find_model_by_role(models_registry, "uncensored", device_type)
    if not uncensored_model:
        print_error("No model with role 'uncensored' found for this device in models.json")
        return state
    engine = build_engine(uncensored_model, models_registry, device_type)
    return AppState(active_model=uncensored_model, is_uncensored=True, engine=engine)

def switch_via_menu(state: AppState, models_registry: dict, device_type: str, build_engine) -> AppState:
    selected_model = print_models_menu(models_registry)
    if not selected_model:
        return state
    is_uncensored = models_registry[selected_model].get("role") == "uncensored"
    engine = build_engine(selected_model, models_registry, device_type)
    return AppState(active_model=selected_model, is_uncensored=is_uncensored, engine=engine)