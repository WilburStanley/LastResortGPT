import re


def strip_control_characters(text: str) -> str:
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
    cleaned = ansi_escape.sub('', text)
    cleaned = ''.join(char for char in cleaned if char == '\n' or char == '\t' or not (0 <= ord(char) < 32))
    return cleaned


def validate_prompt(raw_input: str):
    cleaned = strip_control_characters(raw_input).strip()

    if not cleaned:
        return False, None

    return True, cleaned


KNOWN_COMMANDS = ("/help", "/main", "/uncensored", "/models", "/exit")

def is_unrecognized_command(stripped_input: str) -> bool:
    return stripped_input.startswith("/") and stripped_input not in KNOWN_COMMANDS