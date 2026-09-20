import json
import urllib.request
import urllib.error
import socket

from core.engines.base_engine import BaseEngine

OLLAMA_BASE_URL = "http://localhost:11434"
REQUEST_TIMEOUT_SECONDS = 180
KEEP_ALIVE_DURATION = "30m"

class OllamaEngine(BaseEngine):
    def __init__(self, model_name: str, context_window: int = 4096, num_predict: int = 512):
        self.model_name = model_name
        self.context_window = context_window
        self.num_predict = num_predict

    def is_available(self) -> bool:
        try:
            request = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
            urllib.request.urlopen(request, timeout=3)
            return True
        except (urllib.error.URLError, TimeoutError):
            return False

    def generate(self, prompt: str, context: list = None, on_retry=None) -> dict:
        result = self._call_ollama(prompt, context, think=False, num_predict=self.num_predict)
        answer_text = result.get("response", "").strip()

        if not answer_text:
            if on_retry:
                on_retry()
            escalated_num_predict = self.num_predict * 2
            result = self._call_ollama(prompt, context, think=True, num_predict=escalated_num_predict)
            answer_text = result.get("response", "").strip()

        thinking_text = result.get("thinking", "").strip()
        logprobs_entries = result.get("logprobs", [])
        response_logprobs = self._filter_response_logprobs(logprobs_entries, thinking_text)

        return {
            "text": answer_text,
            "thinking": thinking_text,
            "logprobs": response_logprobs,
            "context": result.get("context", []),
        }

    def _call_ollama(self, prompt: str, context: list, think: bool, num_predict: int) -> dict:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "logprobs": True,
            "top_logprobs": 1,
            "keep_alive": KEEP_ALIVE_DURATION,
            "think": think,
            "options": {
                "num_ctx": self.context_window,
                "num_predict": num_predict,
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
                return json.loads(response.read().decode("utf-8"))
        except socket.timeout:
            raise RuntimeError("The model took too long to respond. Try a shorter prompt or try again.")
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8")
            raise RuntimeError(f"Ollama returned an error: {error_body}")
        except urllib.error.URLError as error:
            raise RuntimeError(f"Could not reach Ollama: {error.reason}")

    def _filter_response_logprobs(self, logprobs_entries: list, thinking_text: str) -> list:
        if not thinking_text:
            token_logprobs = []
            for entry in logprobs_entries:
                if isinstance(entry, dict) and "logprob" in entry:
                    token_logprobs.append(entry["logprob"])
            return token_logprobs

        accumulated_text = ""
        thinking_length = len(thinking_text)
        response_logprobs = []
        past_thinking = False

        for entry in logprobs_entries:
            if not isinstance(entry, dict) or "logprob" not in entry:
                continue

            token_string = entry.get("token", "")

            if not past_thinking:
                accumulated_text += token_string
                if len(accumulated_text) >= thinking_length:
                    past_thinking = True
                continue

            response_logprobs.append(entry["logprob"])

        return response_logprobs