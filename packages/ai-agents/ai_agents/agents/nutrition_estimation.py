from typing import Dict, Any
from ..models.llm_provider import BaseVisionModel
from ..schemas.nutrition import NutritionEstimate
from ..graph.state import GraphState
import time

class NutritionEstimationAgent:
    def __init__(self, model: BaseVisionModel):
        self.model = model

    async def run(self, state: GraphState) -> Dict[str, Any]:
        start = time.time()
        
        ingredients = state.get("ingredients", [])
        if not ingredients:
            return {}
            
        ingredients_text = "\n".join([f"- {i.name}: {i.estimated_amount}" for i in ingredients])
        prompt = (
            f"Based on the following ingredients and amounts:\n{ingredients_text}\n"
            "Estimate the total nutritional values. "
            "Include calories, protein, carbs, fat, fiber, sugar, and sodium. "
            "For each, provide the value (in grams or kcal or mg as appropriate) and your confidence score (0.0 to 1.0)."
        )
        
        try:
            nutrition = await self.model.analyze_text(
                prompt=prompt,
                schema=NutritionEstimate
            )
        except Exception as e:
            raise RuntimeError(f"Nutrition Estimation Failed: {str(e)}")

        latency = int((time.time() - start) * 1000)
        metadata = state.get("metadata", {})
        metadata["nutrition_estimation"] = {"latency_ms": latency}

        return {"nutrition": nutrition, "metadata": metadata}
