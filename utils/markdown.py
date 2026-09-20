import re
from pylatexenc.latex2text import LatexNodes2Text

from utils.colors import colorize, CYAN, YELLOW, AMBER

_latex_converter = LatexNodes2Text(math_mode="text")


def convert_latex(text: str) -> str:
    def replace_math(match) -> str:
        latex_code = match.group(1)
        try:
            return _latex_converter.latex_to_text(latex_code)
        except Exception:
            return latex_code

    text = re.sub(r"\$\$(.*?)\$\$", replace_math, text, flags=re.DOTALL)
    text = re.sub(r"\\\[(.*?)\\\]", replace_math, text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", replace_math, text, flags=re.DOTALL)
    text = re.sub(r"\$(.*?)\$", replace_math, text)

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
    text = convert_inline_code(text)
    return text