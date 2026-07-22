from typing import Dict, Any
from ..models.llm_provider import BaseVisionModel
from ..schemas.nutrition import QualityReport
from ..graph.state import GraphState
import time

class QualityControlAgent:
    def __init__(self, model: BaseVisionModel):
        self.model = model

    async def run(self, state: GraphState) -> Dict[str, Any]:
        start = time.time()
        
        # Simple programmatic validation rules before LLM validation
        warnings = []
        valid = True
        
        nutrition = state.get("nutrition")
        
        if nutrition and hasattr(nutrition, "protein") and hasattr(nutrition, "carbs") and hasattr(nutrition, "fat") and hasattr(nutrition, "calories"):
            protein_val = getattr(nutrition.protein, "value", 0) if nutrition.protein else 0
            carbs_val = getattr(nutrition.carbs, "value", 0) if nutrition.carbs else 0
            fat_val = getattr(nutrition.fat, "value", 0) if nutrition.fat else 0
            cal_val = getattr(nutrition.calories, "value", 0) if nutrition.calories else 0

            # Heuristic: 1g protein/carbs = 4 kcal, 1g fat = 9 kcal
            total_macros_kcal = (protein_val * 4) + (carbs_val * 4) + (fat_val * 9)
            
            if cal_val > 0 and abs(total_macros_kcal - cal_val) > (0.3 * cal_val):
                warnings.append("Macro values do not align with total calories.")
                valid = False
                
        # Call LLM for deeper validation if needed (optional, keeping it simple for now)
        report = QualityReport(
            valid=valid,
            warnings=warnings,
            adjusted_confidence={}
        )

        latency = int((time.time() - start) * 1000)
        metadata = state.get("metadata", {})
        metadata["quality_control"] = {"latency_ms": latency}

        return {"quality": report, "metadata": metadata}
