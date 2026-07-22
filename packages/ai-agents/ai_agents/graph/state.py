from typing import TypedDict, List, Optional, Dict, Any
from ..schemas.nutrition import FoodItem, Ingredient, NutritionEstimate, QualityReport

class GraphState(TypedDict):
    image_bytes: bytes
    foods: List[FoodItem]
    ingredients: List[Ingredient]
    nutrition: Optional[NutritionEstimate]
    quality: Optional[QualityReport]
    metadata: Dict[str, Any]
