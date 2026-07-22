from typing import Dict, Any, List
from pydantic import BaseModel
from ..models.llm_provider import BaseVisionModel
from ..schemas.nutrition import FoodItem
from ..graph.state import GraphState
import time

class FoodRecognitionResponse(BaseModel):
    items: List[FoodItem]

class FoodRecognitionAgent:
    def __init__(self, model: BaseVisionModel):
        self.model = model

    async def run(self, state: GraphState) -> Dict[str, Any]:
        start = time.time()
        
        prompt = (
            "Analyze this image and identify the food items or dishes present. "
            "For each item, provide the name and your confidence score (0.0 to 1.0) "
            "based on how clearly you can see it."
        )
        
        try:
            response = await self.model.analyze_image(
                image_bytes=state["image_bytes"],
                prompt=prompt,
                schema=FoodRecognitionResponse
            )
            foods = response.items
        except Exception as e:
            # Propagate the error up
            raise RuntimeError(f"Food Recognition Failed: {str(e)}")

        latency = int((time.time() - start) * 1000)
        metadata = state.get("metadata", {})
        metadata["food_recognition"] = {"latency_ms": latency}

        return {"foods": foods, "metadata": metadata}
