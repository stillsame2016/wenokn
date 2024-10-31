import requests
from typing import Any, Optional, List, Mapping
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic.v1 import Field


class CustomSDSCLLM(LLM):
    api_key: str = Field(..., description="API key for authentication")
    model: str = Field(..., description="Model identifier")
    base_url: str = Field(
        default="https://sdsc-llm-openwebui.nrp-nautilus.io/api/chat/completions",
        description="Base URL for the API"
    )

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure base_url is stripped of any leading/trailing whitespace
        self.base_url = self.base_url.strip()
    
    @property
    def _llm_type(self) -> str:
        return "custom_sdsc_llm"

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
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

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model": self.model, "base_url": self.base_url}
