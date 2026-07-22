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


class InferenceServiceClient(BaseVisionModel):
    def __init__(self, base_url: str = None):
        import os
        self.base_url = base_url or os.getenv("INFERENCE_SERVICE_URL", "http://inference:8001")
        self.model_name = "inference-service"

    def _extract_json(self, text: str) -> str:
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

    def _parse_schema(self, content: str, schema: Type[T]) -> Any:
        try:
            json_str = self._extract_json(content)
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                if "foods" in parsed and "items" not in parsed:
                    parsed["items"] = parsed.pop("foods")
                if "ingredients" in parsed and isinstance(parsed["ingredients"], list):
                    for ing in parsed["ingredients"]:
                        if isinstance(ing, dict) and "portion_size" in ing and "estimated_amount" not in ing:
                            ing["estimated_amount"] = ing.pop("portion_size")
                if "is_valid_food_image" in parsed and "valid" not in parsed:
                    parsed["valid"] = parsed.pop("is_valid_food_image")
            return schema(**parsed)
        except Exception as e:
            raise ValueError(f"Failed to parse structured output from model: {e}\nRaw output: {content}")

    async def analyze_image(self, image_bytes: bytes, prompt: str, schema: Type[T] = None) -> Any:
        if schema:
            prompt += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"
        
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/infer",
                    json={
                        "prompt": prompt,
                        "image_base64": image_b64,
                        "temperature": 0.2
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("text", "{}")
                self.model_name = data.get("metadata", {}).get("model", "unknown")
                
                if schema:
                    return self._parse_schema(content, schema)
                return content
            except httpx.RequestError as e:
                raise ConnectionError(f"Failed to connect to Inference Service at {self.base_url}: {e}")

    async def analyze_text(self, prompt: str, schema: Type[T] = None) -> Any:
        if schema:
            prompt += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/infer",
                    json={
                        "prompt": prompt,
                        "temperature": 0.2
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("text", "{}")
                self.model_name = data.get("metadata", {}).get("model", "unknown")
                
                if schema:
                    return self._parse_schema(content, schema)
                return content
            except httpx.RequestError as e:
                raise ConnectionError(f"Failed to connect to Inference Service at {self.base_url}: {e}")
