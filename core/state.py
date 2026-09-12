from dataclasses import dataclass

from core.engines.ollama_engine import OllamaEngine

@dataclass
class AppState:
    active_model: str
    is_uncensored: bool
    engine: OllamaEngine