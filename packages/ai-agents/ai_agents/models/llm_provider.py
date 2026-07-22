import base64
import json
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseVisionModel(ABC):
    @abstractmethod
    async def analyze_image(self, image_bytes: bytes, prompt: str, schema: Type[T] = None) -> Any:
        pass

    @abstractmethod
    async def analyze_text(self, prompt: str, schema: Type[T] = None) -> Any:
        pass


class LlavaModel(BaseVisionModel):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "llava:7b"

    def _extract_json(self, text: str) -> str:
        # Simple heuristic to extract JSON from markdown output
        text = text.strip()
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.rfind("```")
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            return text[start:end].strip()
        return text

    async def analyze_image(self, image_bytes: bytes, prompt: str, schema: Type[T] = None) -> Any:
        # Provide schema format in prompt if schema is given
        if schema:
            prompt += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"
        
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "images": [image_b64],
                        "stream": False,
                        "format": "json" if schema else ""
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("response", "")
                
                if schema:
                    try:
                        # Extract and parse JSON
                        json_str = self._extract_json(content)
                        parsed = json.loads(json_str)
                        return schema(**parsed)
                    except Exception as e:
                        raise ValueError(f"Failed to parse structured output from model: {e}\nRaw output: {content}")
                return content
            except httpx.RequestError as e:
                raise ConnectionError(f"Failed to connect to LLM provider at {self.base_url}: {e}")

    async def analyze_text(self, prompt: str, schema: Type[T] = None) -> Any:
        if schema:
            prompt += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json" if schema else ""
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("response", "")
                
                if schema:
                    try:
                        json_str = self._extract_json(content)
                        parsed = json.loads(json_str)
                        return schema(**parsed)
                    except Exception as e:
                        raise ValueError(f"Failed to parse structured output from model: {e}\nRaw output: {content}")
                return content
            except httpx.RequestError as e:
                raise ConnectionError(f"Failed to connect to LLM provider at {self.base_url}: {e}")
