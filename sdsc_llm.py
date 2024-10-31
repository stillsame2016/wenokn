from pydantic import BaseModel, Field
from langchain_core.language_models import LLM
from typing import Optional, List, Any
import requests

class CustomSDSCLLM(LLM, BaseModel):
    api_key: str = Field(..., description="API key for authentication")
    model: str = Field(..., description="Model identifier")
    base_url: str = Field(
        default="https://sdsc-llm-openwebui.nrp-nautilus.io/api/chat/completions",
        description="Base URL for the API"
    )

    class Config:
        arbitrary_types_allowed = True

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

        response = requests.post(self.base_url.strip(), headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"Request failed with status {response.status_code}: {response.text}")
