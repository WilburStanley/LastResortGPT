import re

from utils.colors import colorize, CYAN, GRAY, YELLOW, AMBER

ITALIC = "\033[3m"
RESET = "\033[0m"

SUPERSCRIPT_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "n": "ⁿ", "i": "ⁱ",
}

SUBSCRIPT_MAP = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
}

LATEX_SYMBOLS = {
    r"\pi": "π", r"\infty": "∞", r"\sum": "∑", r"\int": "∫",
    r"\sqrt": "√", r"\times": "×", r"\cdot": "·", r"\div": "÷",
    r"\le": "≤", r"\leq": "≤", r"\ge": "≥", r"\geq": "≥",
    r"\neq": "≠", r"\approx": "≈", r"\pm": "±", r"\alpha": "α",
    r"\beta": "β", r"\gamma": "γ", r"\theta": "θ", r"\lambda": "λ",
    r"\mu": "μ", r"\sigma": "σ", r"\phi": "φ", r"\omega": "ω",
    r"\Delta": "Δ", r"\partial": "∂", r"\to": "→", r"\rightarrow": "→",
    r"\in": "∈", r"\forall": "∀", r"\exists": "∃",
}

def _convert_superscript(match) -> str:
    content = match.group(1)
    converted = "".join(SUPERSCRIPT_MAP.get(char, char) for char in content)
    return converted

def _convert_subscript(match) -> str:
    content = match.group(1)
    converted = "".join(SUBSCRIPT_MAP.get(char, char) for char in content)
    return converted

def _convert_fraction(match) -> str:
    numerator = match.group(1)
    denominator = match.group(2)
    return f"({numerator})/({denominator})"

def convert_latex(text: str) -> str:
    text = re.sub(r"\$\$(.*?)\$\$", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\$(.*?)\$", r"\1", text)

    text = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", _convert_fraction, text)
    text = re.sub(r"\\sqrt\{([^{}]*)\}", r"√(\1)", text)

    text = re.sub(r"\^\{([^{}]*)\}", _convert_superscript, text)
    text = re.sub(r"\^(\w)", lambda m: SUPERSCRIPT_MAP.get(m.group(1), "^" + m.group(1)), text)

    text = re.sub(r"_\{([^{}]*)\}", _convert_subscript, text)
    text = re.sub(r"_(\w)", lambda m: SUBSCRIPT_MAP.get(m.group(1), "_" + m.group(1)), text)

    for latex_symbol, unicode_symbol in LATEX_SYMBOLS.items():
        text = text.replace(latex_symbol, unicode_symbol)

    text = text.replace("\\left", "").replace("\\right", "")
    text = re.sub(r"\\text\{([^{}]*)\}", r"\1", text)

    return text

def convert_code_blocks(text: str) -> str:
    def replace_block(match):
        code = match.group(2).strip("\n")
        lines = code.split("\n")
        colored_lines = [colorize(line, CYAN) for line in lines]
        return "\n" + "\n".join(colored_lines) + "\n"

    return re.sub(r"```(\w*)\n(.*?)```", replace_block, text, flags=re.DOTALL)

def convert_inline_code(text: str) -> str:
    return re.sub(r"`([^`]+)`", lambda m: colorize(m.group(1), CYAN), text)

def convert_bold(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", lambda m: colorize(m.group(1), AMBER), text)

def convert_italic(text: str) -> str:
    return re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", rf"{ITALIC}\1{RESET}", text)

def convert_headers(text: str) -> str:
    def replace_header(match):
        header_text = match.group(2)
        return colorize(header_text.upper(), YELLOW)

    return re.sub(r"^(#{1,6})\s+(.+)$", replace_header, text, flags=re.MULTILINE)

def convert_bullet_lists(text: str) -> str:
    def replace_bullet(match):
        return "  • " + match.group(1)

    return re.sub(r"^[-*]\s+(.+)$", replace_bullet, text, flags=re.MULTILINE)

def render_markdown(text: str) -> str:
    text = convert_code_blocks(text)
    text = convert_latex(text)
    text = convert_headers(text)
    text = convert_bullet_lists(text)
    text = convert_bold(text)
    text = convert_italic(text)
    text = convert_inline_code(text)
    return text