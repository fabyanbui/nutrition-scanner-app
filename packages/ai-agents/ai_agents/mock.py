from typing import Dict, Any, List

class FoodRecognitionAgent:
    def __init__(self):
        self.version = "mock-1.0"
        
    def analyze(self, image_data: bytes) -> List[Dict[str, Any]]:
        # Mock recognition
        return [
            {"name": "Pho", "confidence": 0.85},
            {"name": "Egg", "confidence": 0.92}
        ]

class IngredientAgent:
    def analyze(self, foods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Mock ingredients
        return [
            {"name": "beef", "confidence": 0.75},
            {"name": "rice noodles", "confidence": 0.90},
            {"name": "egg", "confidence": 0.95}
        ]

class NutritionAgent:
    def analyze(self, ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "calories": {"value": 450.0, "confidence": 0.75},
            "protein": {"value": 25.0, "confidence": 0.80},
            "carbs": {"value": 60.0, "confidence": 0.70},
            "fat": {"value": 12.0, "confidence": 0.85}
        }

class QualityAgent:
    def check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "warning",
            "message": "Image is slightly blurry, confidence scores may be affected."
        }

def run_mock_pipeline(image_data: bytes) -> Dict[str, Any]:
    food_agent = FoodRecognitionAgent()
    ingredient_agent = IngredientAgent()
    nutrition_agent = NutritionAgent()
    quality_agent = QualityAgent()
    
    foods = food_agent.analyze(image_data)
    ingredients = ingredient_agent.analyze(foods)
    nutrition = nutrition_agent.analyze(ingredients)
    quality = quality_agent.check({"foods": foods, "nutrition": nutrition})
    
    return {
        "foods": foods,
        "ingredients": ingredients,
        "nutrition": nutrition,
        "quality_warning": quality.get("message")
    }
