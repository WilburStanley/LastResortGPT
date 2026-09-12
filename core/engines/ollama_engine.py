import json
import urllib.request
import urllib.error

from core.engines.base_engine import BaseEngine

OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaEngine(BaseEngine):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def is_available(self) -> bool:
        try:
            request = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
            urllib.request.urlopen(request, timeout=3)
            return True
        except (urllib.error.URLError, TimeoutError):
            return False

    def generate(self, prompt: str) -> dict:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "logprobs": True,
            "top_logprobs": 1,
        }
        encoded_payload = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=encoded_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8")
            raise RuntimeError(f"Ollama returned an error: {error_body}") from error

        text = result.get("response", "")
        logprobs_entries = result.get("logprobs", [])

        token_logprobs = []
        for entry in logprobs_entries:
            if isinstance(entry, dict) and "logprob" in entry:
                token_logprobs.append(entry["logprob"])

        return {
            "text": text.strip(),
            "logprobs": token_logprobs,
        }