from utils.colors import colorize, GREEN, CYAN, YELLOW, GRAY, RED, BLUE

LOGO = r"""
██╗     ██████╗        ██████╗ ██████╗ ████████╗
██║     ██╔══██╗      ██╔════╝ ██╔══██╗╚══██╔══╝
██║     ██████╔╝█████╗██║  ███╗██████╔╝   ██║   
██║     ██╔══██╗╚════╝██║   ██║██╔═══╝    ██║   
███████╗██║  ██║      ╚██████╔╝██║        ██║   
╚══════╝╚═╝  ╚═╝       ╚═════╝ ╚═╝        ╚═╝
"""

DEFAULT_NOTE = "Note: LastResortGPT is a fallback tool. You are responsible for verifying any output before relying on it."
UNCENSORED_NOTE = "Note: Uncensored mode is active. Content may include no ethical/moral filtering. You are fully responsible for anything generated and how you use it."

HELP_COMMANDS = [
    ("/help", "Show this list of commands"),
    ("/main", "Switch to the default model"),
    ("/uncensored", "Switch to the uncensored model"),
    ("/models", "List & choose available models"),
    ("/exit", "Quit & shut down Ollama server"),
]

def print_banner(cutoff_date: str, is_uncensored: bool = False) -> None:
    logo_color = RED if is_uncensored else GREEN
    note_color = RED if is_uncensored else GRAY
    note_text = UNCENSORED_NOTE if is_uncensored else DEFAULT_NOTE

    print(colorize(LOGO, logo_color))
    print(colorize(f"Knowledge Cutoff: {cutoff_date}", CYAN))
    print(colorize(note_text, note_color))
    print()

def print_help() -> None:
    print(colorize("Available commands:", BLUE))
    for command, description in HELP_COMMANDS:
        command_text = colorize(f"  {command}".ljust(16), GREEN)
        description_text = colorize(description, GRAY)
        print(f"{command_text}{description_text}")
    print()
    
def print_models_menu(models_registry: dict):
    model_names = list(models_registry.keys())
    print()
    print(colorize("Available models:", BLUE))

    for index, name in enumerate(model_names, start=1):
        model_info = models_registry[name]
        cutoff = model_info.get("cutoff", "unknown")
        role = model_info.get("role", "")

        if role == "main":
            name_color = GREEN
        elif role == "uncensored":
            name_color = RED
        else:
            name_color = GRAY

        index_text = f"  {index}."
        name_text = colorize(name, name_color)
        cutoff_text = colorize(f"(cutoff: {cutoff})", GRAY)

        print(f"{index_text} {name_text} {cutoff_text}")

    print()
    choice = input(colorize("Pick a number: ", YELLOW)).strip()
    
    if not choice.isdigit():
        print_error("Invalid selection")
        return None

    choice_index = int(choice) - 1
    if choice_index < 0 or choice_index >= len(model_names):
        print_error("Invalid selection")
        return None

    return model_names[choice_index]
    
def print_error(message: str) -> None:
    print(colorize(f"[ ERROR: {message} ]", RED))

def build_prompt_prefix(is_uncensored: bool) -> str:
    mode_name = "uncensored" if is_uncensored else "main"
    mode_color = RED if is_uncensored else CYAN

    return (
        colorize("LastResortGPT", YELLOW)
        + colorize(f" ({mode_name})", mode_color)
        + colorize(":~", GRAY)
        + colorize("$ ", GREEN)
    )

def get_confidence_color(confidence_percent: float) -> str:
    if confidence_percent > 50:
        return GREEN
    elif confidence_percent == 50:
        return YELLOW
    else:
        return RED

def print_response(confidence_percent: float, response_text: str) -> None:
    confidence_color = get_confidence_color(confidence_percent)
    print(colorize(f"[ Confidence Level: {confidence_percent}% ]", confidence_color))
    print(response_text)
    print()