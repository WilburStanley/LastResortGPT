RESET = "\033[0m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GRAY = "\033[90m"
RED = "\033[31m"
PINK = "\033[35m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"