from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time

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
    
    # Read file content just to simulate processing
    content = await file.read()
    
    # Simulate processing delay
    time.sleep(1.5)
    
    # Mock AI pipeline output
    # This will be replaced by the actual LangGraph implementation
    response = AnalysisResponse(
        foods=[
            FoodItem(name="Pho", confidence=0.85),
            FoodItem(name="Egg", confidence=0.92)
        ],
        nutrition=NutritionEstimate(
            calories=ConfidenceValue(value=450.0, confidence=0.75),
            protein=ConfidenceValue(value=25.0, confidence=0.80),
            carbs=ConfidenceValue(value=60.0, confidence=0.70),
            fat=ConfidenceValue(value=12.0, confidence=0.85)
        ),
        quality_warning="Image is slightly blurry, confidence scores may be affected.",
        processing_time_ms=int((time.time() - start_time) * 1000)
    )
    
    return response

@app.get("/health")
def health_check():
    return {"status": "healthy"}
