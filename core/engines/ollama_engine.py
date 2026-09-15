import json
import urllib.request
import urllib.error
import socket

from core.engines.base_engine import BaseEngine

OLLAMA_BASE_URL = "http://localhost:11434"
REQUEST_TIMEOUT_SECONDS = 180
MAX_RESPONSE_TOKENS = 400
KEEP_ALIVE_DURATION = "30m"

class OllamaEngine(BaseEngine):
    def __init__(self, model_name: str, context_window: int = 4096):
        self.model_name = model_name
        self.context_window = context_window

    def is_available(self) -> bool:
        try:
            request = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
            urllib.request.urlopen(request, timeout=3)
            return True
        except (urllib.error.URLError, TimeoutError):
            return False

    def generate(self, prompt: str, context: list = None) -> dict:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "logprobs": True,
            "top_logprobs": 1,
            "keep_alive": KEEP_ALIVE_DURATION,
            "options": {
                "num_ctx": self.context_window,
                "num_predict": MAX_RESPONSE_TOKENS,
            },
        }

        if context:
            payload["context"] = context

        encoded_payload = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=encoded_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                result = json.loads(response.read().decode("utf-8"))
        except socket.timeout:
            raise RuntimeError("The model took too long to respond. Try a shorter prompt or try again.")
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8")
            raise RuntimeError(f"Ollama returned an error: {error_body}")
        except urllib.error.URLError as error:
            raise RuntimeError(f"Could not reach Ollama: {error.reason}")

        text = result.get("response", "")
        logprobs_entries = result.get("logprobs", [])

        token_logprobs = []
        for entry in logprobs_entries:
            if isinstance(entry, dict) and "logprob" in entry:
                token_logprobs.append(entry["logprob"])

        return {
            "text": text.strip(),
            "logprobs": token_logprobs,
            "context": result.get("context", []),
        }