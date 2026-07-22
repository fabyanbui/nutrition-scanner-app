from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time

try:
    from ai_agents.graph.workflow import NutritionScannerWorkflow
    from ai_agents.models.llm_provider import LlavaModel
except ImportError:
    pass  # We will handle missing path in docker container via proper pythonpath or setup.py

app = FastAPI(title="Nutrition Scanner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock models matching the frontend expectations
class ConfidenceValue(BaseModel):
    value: float
    confidence: float

class FoodItem(BaseModel):
    name: str
    confidence: float

class NutritionEstimate(BaseModel):
    calories: ConfidenceValue
    protein: ConfidenceValue
    carbs: ConfidenceValue
    fat: ConfidenceValue

class AnalysisResponse(BaseModel):
    foods: List[FoodItem]
    nutrition: NutritionEstimate
    quality_warning: Optional[str] = None
    processing_time_ms: int

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    start_time = time.time()
    content = await file.read()
    
    try:
        model = LlavaModel()
        workflow = NutritionScannerWorkflow(model)
        state = await workflow.run(image_bytes=content)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"AI Model service unavailable: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"AI Pipeline failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
    quality_warning = None
    if state.get("quality") and not state["quality"].valid:
        quality_warning = " | ".join(state["quality"].warnings)
        
    foods_res = [
        FoodItem(name=f.name, confidence=f.confidence) for f in state.get("foods", [])
    ]
    
    nutrition_res = state.get("nutrition")
    if nutrition_res:
        nutrition = NutritionEstimate(
            calories=ConfidenceValue(value=nutrition_res.calories.value, confidence=nutrition_res.calories.confidence),
            protein=ConfidenceValue(value=nutrition_res.protein.value, confidence=nutrition_res.protein.confidence),
            carbs=ConfidenceValue(value=nutrition_res.carbs.value, confidence=nutrition_res.carbs.confidence),
            fat=ConfidenceValue(value=nutrition_res.fat.value, confidence=nutrition_res.fat.confidence)
        )
    else:
        # Fallback if nutrition fails
        nutrition = NutritionEstimate(
            calories=ConfidenceValue(value=0, confidence=0),
            protein=ConfidenceValue(value=0, confidence=0),
            carbs=ConfidenceValue(value=0, confidence=0),
            fat=ConfidenceValue(value=0, confidence=0)
        )
        
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    response = AnalysisResponse(
        foods=foods_res,
        nutrition=nutrition,
        quality_warning=quality_warning,
        processing_time_ms=processing_time_ms
    )
    
    return response

@app.get("/health")
def health_check():
    return {"status": "healthy"}
