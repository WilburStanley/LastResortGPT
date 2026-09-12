import sys
import threading
import time
from utils.colors import colorize, PINK, RESET

class LoadingAnimation:
    def __init__(self, message: str = colorize("LastResortGPT is thinking", PINK)):
        self.message = message
        self._stop_event = threading.Event()
        self._thread = None

    def _animate(self):
        dot_count = 0

        while not self._stop_event.is_set():
            dot_count %= 4

            dots = "." * dot_count
            colored_dots = f"{PINK}{dots}{RESET}"
            padding = " " * (3 - len(dots))

            sys.stdout.write(f"\r{self.message}{colored_dots}{padding}")
            sys.stdout.flush()

            dot_count += 1
            time.sleep(0.4)

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()