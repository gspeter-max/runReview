from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import SecretStr

class BaseLLMClient(ABC):
    def __init__(self, model: str, api_key: Optional[SecretStr]):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Returns litellm_params for this provider."""
        pass
