import shutil

LOGO = r"""
██╗     ██████╗        ██████╗ ██████╗ ████████╗
██║     ██╔══██╗      ██╔════╝ ██╔══██╗╚══██╔══╝
██║     ██████╔╝█████╗██║  ███╗██████╔╝   ██║   
██║     ██╔══██╗╚════╝██║   ██║██╔═══╝    ██║   
███████╗██║  ██║      ╚██████╔╝██║        ██║   
╚══════╝╚═╝  ╚═╝       ╚═════╝ ╚═╝        ╚═╝
"""


def print_banner(cutoff_date: str) -> None:
    print(LOGO)
    print(f"Knowledge Cutoff: {cutoff_date}")
    print("Note: LastResortGPT is a fallback tool. You are responsible for verifying any output before relying on it.")
    print()


def print_prompt_line(prompt_text: str) -> None:
    print(f"commandline$ {prompt_text}")
    print()


def print_response(confidence_percent: float, response_text: str) -> None:
    print(f"[ Confidence Level: {confidence_percent}% ]")
    print(response_text)
    print()