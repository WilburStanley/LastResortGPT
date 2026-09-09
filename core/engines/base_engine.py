from abc import ABC, abstractmethod

class BaseEngine(ABC):
    """Shared interface every AI engine must implement."""
    @abstractmethod
    def generate(self, prompt: str) -> dict:
        """Returns {"text": str, "logprobs": list[float]}."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the engine is reachable and ready to generate."""
        raise NotImplementedError