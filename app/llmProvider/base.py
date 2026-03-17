from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMClient(ABC):
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Returns litellm_params for this provider."""
        pass
