import os
import sys
import threading
from utils.colors import colorize, PINK, YELLOW


def _supports_inline_updates() -> bool:
    """Git Bash's winpty wrapper can't reliably overwrite terminal lines."""
    if not sys.stdout.isatty():
        return False
    if os.environ.get("MSYSTEM"):
        return False
    return True


class LoadingAnimation:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        self._retry_triggered = threading.Event()
        self._inline_supported = _supports_inline_updates()

    def notify_retry(self) -> None:
        self._retry_triggered.set()

    def _get_current_text(self, dot_count: int) -> tuple:
        dots = "." * (dot_count % 4)
        if self._retry_triggered.is_set():
            return f"Still thinking, needs more room{dots}", YELLOW
        return f"LastResortGPT is thinking{dots}", PINK

    def _animate_inline(self):
        dot_count = 0
        while not self._stop_event.is_set():
            text, color = self._get_current_text(dot_count)
            colored_line = colorize(text, color)
            sys.stdout.write(f"\r\033[K{colored_line}")
            sys.stdout.flush()

            self._stop_event.wait(timeout=0.4)
            dot_count += 1

        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def _animate_static(self):
        print(colorize("LastResortGPT is thinking...", PINK))
        retry_shown = False

        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=1)
            if self._retry_triggered.is_set() and not retry_shown:
                print(colorize("Still thinking, needs more room...", YELLOW))
                retry_shown = True

    def start(self):
        self._stop_event.clear()
        self._retry_triggered.clear()
        target = self._animate_inline if self._inline_supported else self._animate_static
        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()