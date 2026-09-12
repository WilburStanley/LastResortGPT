from utils.colors import colorize, GREEN, CYAN, YELLOW, GRAY, RED

LOGO = r"""
██╗     ██████╗        ██████╗ ██████╗ ████████╗
██║     ██╔══██╗      ██╔════╝ ██╔══██╗╚══██╔══╝
██║     ██████╔╝█████╗██║  ███╗██████╔╝   ██║   
██║     ██╔══██╗╚════╝██║   ██║██╔═══╝    ██║   
███████╗██║  ██║      ╚██████╔╝██║        ██║   
╚══════╝╚═╝  ╚═╝       ╚═════╝ ╚═╝        ╚═╝
"""

PROMPT_PREFIX = colorize("commandline", YELLOW) + colorize(":~", GRAY) + colorize("$ ", GREEN)

def get_confidence_color(confidence_percent: float) -> str:
    if confidence_percent > 50:
        return GREEN
    elif confidence_percent == 50:
        return YELLOW
    else:
        return RED

def print_banner(cutoff_date: str) -> None:
    print(colorize(LOGO, GREEN))
    print(colorize(f"Knowledge Cutoff: {cutoff_date}", CYAN))
    print(colorize("Note: LastResortGPT is a fallback tool. You are responsible for verifying any output before relying on it.", GRAY))
    print()

def print_response(confidence_percent: float, response_text: str) -> None:
    confidence_color = get_confidence_color(confidence_percent)
    print(colorize(f"[ Confidence Level: {confidence_percent}% ]", confidence_color))
    print(response_text)
    print()