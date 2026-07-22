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
        
        if nutrition:
            # Heuristic: 1g protein/carbs = 4 kcal, 1g fat = 9 kcal
            total_macros_kcal = (
                nutrition.protein.value * 4 +
                nutrition.carbs.value * 4 +
                nutrition.fat.value * 9
            )
            
            if nutrition.calories.value > 0 and abs(total_macros_kcal - nutrition.calories.value) > (0.3 * nutrition.calories.value):
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
