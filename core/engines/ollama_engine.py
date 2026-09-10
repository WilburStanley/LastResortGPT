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
            "logprobs": 1,
            "max_tokens": 512,
        }
        encoded_payload = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/v1/completions",
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

        choice = result["choices"][0]
        text = choice.get("text", "")
        token_logprobs = choice.get("logprobs", {}).get("token_logprobs", [])

        return {
            "text": text.strip(),
            "logprobs": token_logprobs,
        }