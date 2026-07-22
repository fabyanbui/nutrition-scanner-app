from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ConfidenceValue(BaseModel):
    value: float
    confidence: float

class FoodItem(BaseModel):
    name: str
    confidence: float

class Ingredient(BaseModel):
    name: str
    estimated_amount: str
    confidence: float

class NutritionEstimate(BaseModel):
    calories: ConfidenceValue
    protein: ConfidenceValue
    carbs: ConfidenceValue  # frontend expects 'carbs'
    fat: ConfidenceValue
    fiber: ConfidenceValue
    sugar: ConfidenceValue
    sodium: ConfidenceValue

class QualityReport(BaseModel):
    valid: bool
    warnings: List[str]
    adjusted_confidence: Dict[str, Any] = Field(default_factory=dict)
