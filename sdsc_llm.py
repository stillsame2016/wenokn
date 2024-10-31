from pydantic import BaseModel
from langchain_core.language_models import LLM
from typing import Optional, List, Any
import requests

class CustomSDSCLLM(LLM):
    api_key: str
    model: str
    base_url: str

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, api_key: str, model: str,
                 base_url: str = "https://sdsc-llm-openwebui.nrp-nautilus.io/api/chat/completions"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.strip()  # Ensure no extra whitespace

    @property
    def _llm_type(self) -> str:
        return "custom_sdsc_llm"

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[Any] = None,
            **kwargs: Any,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        response = requests.post(self.base_url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"Request failed with status {response.status_code}: {response.text}")
