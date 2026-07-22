import base64
import json
import os
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseVisionModel(ABC):
    @abstractmethod
    async def analyze_image(self, image_bytes: bytes, prompt: str, schema: Type[T] = None) -> Any:
        pass

    @abstractmethod
    async def analyze_text(self, prompt: str, schema: Type[T] = None) -> Any:
        pass


class GeminiVisionModel(BaseVisionModel):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

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
            raise ValueError(f"Failed to parse structured output from Gemini API: {e}\nRaw output: {content}")

    async def analyze_image(self, image_bytes: bytes, prompt: str, schema: Type[T] = None) -> Any:
        api_key = self.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing. Please provide a Google AI Studio API key.")

        if schema:
            prompt += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"

        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        parts = [
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_b64
                }
            },
            {"text": prompt}
        ]

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"User-Agent": "aistudio-build"}
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            res_data = res.json()
            candidates = res_data.get("candidates", [])
            if not candidates:
                raise RuntimeError("No candidate response returned from Gemini API.")

            content_parts = candidates[0].get("content", {}).get("parts", [])
            content = "".join([p.get("text", "") for p in content_parts])

            if schema:
                return self._parse_schema(content, schema)
            return content

    async def analyze_text(self, prompt: str, schema: Type[T] = None) -> Any:
        api_key = self.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing. Please provide a Google AI Studio API key.")

        if schema:
            prompt += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"User-Agent": "aistudio-build"}
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            res_data = res.json()
            candidates = res_data.get("candidates", [])
            if not candidates:
                raise RuntimeError("No candidate response returned from Gemini API.")

            content_parts = candidates[0].get("content", {}).get("parts", [])
            content = "".join([p.get("text", "") for p in content_parts])

            if schema:
                return self._parse_schema(content, schema)
            return content


class InferenceServiceClient(BaseVisionModel):
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("INFERENCE_SERVICE_URL", "http://inference:8001")
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        self._gemini_fallback = GeminiVisionModel()

    def _extract_json(self, text: str) -> str:
        return self._gemini_fallback._extract_json(text)

    def _parse_schema(self, content: str, schema: Type[T]) -> Any:
        return self._gemini_fallback._parse_schema(content, schema)

    async def analyze_image(self, image_bytes: bytes, prompt: str, schema: Type[T] = None) -> Any:
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        async with httpx.AsyncClient() as client:
            try:
                prompt_with_schema = prompt
                if schema:
                    prompt_with_schema += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"

                response = await client.post(
                    f"{self.base_url}/infer",
                    json={
                        "prompt": prompt_with_schema,
                        "image_base64": image_b64,
                        "temperature": 0.2
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("text", "{}")
                self.model_name = data.get("metadata", {}).get("model", self.model_name)
                
                if schema:
                    return self._parse_schema(content, schema)
                return content
            except Exception as e:
                # If connecting to local inference service fails, fallback directly to Gemini API
                if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                    return await self._gemini_fallback.analyze_image(image_bytes, prompt, schema)
                raise ConnectionError(f"Failed to perform image analysis via Inference Service or Gemini API: {e}")

    async def analyze_text(self, prompt: str, schema: Type[T] = None) -> Any:
        async with httpx.AsyncClient() as client:
            try:
                prompt_with_schema = prompt
                if schema:
                    prompt_with_schema += f"\n\nYou must return the result strictly as a JSON object matching this schema:\n{schema.model_json_schema()}"

                response = await client.post(
                    f"{self.base_url}/infer",
                    json={
                        "prompt": prompt_with_schema,
                        "temperature": 0.2
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("text", "{}")
                self.model_name = data.get("metadata", {}).get("model", self.model_name)
                
                if schema:
                    return self._parse_schema(content, schema)
                return content
            except Exception as e:
                if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                    return await self._gemini_fallback.analyze_text(prompt, schema)
                raise ConnectionError(f"Failed to perform text analysis via Inference Service or Gemini API: {e}")
