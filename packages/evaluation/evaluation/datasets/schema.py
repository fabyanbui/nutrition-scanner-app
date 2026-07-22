from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class NutritionData(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float

class FoodItem(BaseModel):
    name: str
    ingredients: List[str]
    nutrition: NutritionData

class Annotation(BaseModel):
    image_id: str
    image_path: str
    foods: List[FoodItem]
    metadata: Optional[Dict[str, Any]] = None

class Dataset(BaseModel):
    name: str
    version: str
    samples: List[Annotation]
