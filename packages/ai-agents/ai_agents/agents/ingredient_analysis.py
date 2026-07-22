from typing import Dict, Any, List
from pydantic import BaseModel
from ..models.llm_provider import BaseVisionModel
from ..schemas.nutrition import Ingredient
from ..graph.state import GraphState
import time

class IngredientAnalysisResponse(BaseModel):
    ingredients: List[Ingredient]

class IngredientAnalysisAgent:
    def __init__(self, model: BaseVisionModel):
        self.model = model

    async def run(self, state: GraphState) -> Dict[str, Any]:
        start = time.time()
        
        food_names = [f.name for f in state.get("foods", [])]
        if not food_names:
            return {"ingredients": []}
            
        prompt = (
            f"Given these food items identified in the image: {', '.join(food_names)}. "
            "List the probable ingredients. For each ingredient, estimate the amount "
            "(e.g., '100g', '1 cup') and your confidence (0.0 to 1.0). "
            "Do not invent ingredients with high confidence if you are unsure."
        )
        
        try:
            response = await self.model.analyze_text(
                prompt=prompt,
                schema=IngredientAnalysisResponse
            )
            ingredients = response.ingredients
        except Exception as e:
            raise RuntimeError(f"Ingredient Analysis Failed: {str(e)}")

        latency = int((time.time() - start) * 1000)
        metadata = state.get("metadata", {})
        metadata["ingredient_analysis"] = {"latency_ms": latency}

        return {"ingredients": ingredients, "metadata": metadata}
