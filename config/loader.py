import json


def load_json(path: str) -> dict:
    with open(path, "r") as file:
        return json.load(file)

def find_model_by_role(models_registry: dict, role: str, device_type: str):
    for model_name, model_info in models_registry.items():
        if model_info.get("role") != role:
            continue
        model_device = model_info.get("device", "both")
        if model_device == device_type or model_device == "both":
            return model_name
    return None