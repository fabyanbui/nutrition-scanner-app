from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluation"])

class EvaluationSummary(BaseModel):
    model_name: str
    dataset_version: str
    average_accuracy: float
    average_latency_ms: float
    average_confidence: float
    worst_categories: List[str]

# Mock database of evaluation results for the developer dashboard
MOCK_EVALS = [
    {
        "model_name": "Llava-7b-v1.5",
        "dataset_version": "v1.0",
        "average_accuracy": 0.89,
        "average_latency_ms": 2800,
        "average_confidence": 0.85,
        "worst_categories": ["Fast food", "Blurry images"]
    },
    {
        "model_name": "Qwen-VL-Chat",
        "dataset_version": "v1.0",
        "average_accuracy": 0.92,
        "average_latency_ms": 3100,
        "average_confidence": 0.90,
        "worst_categories": ["Occlusion", "Multiple dishes"]
    }
]

@router.get("", response_model=List[EvaluationSummary])
async def list_evaluations():
    """
    Returns recent evaluation summaries for the developer dashboard.
    """
    return MOCK_EVALS

@router.get("/metrics/dashboard")
async def dashboard_metrics():
    """
    Aggregate metrics API for developer dashboard.
    """
    if not MOCK_EVALS:
        return {}
        
    latest = MOCK_EVALS[-1]
    return {
        "latest_model": latest["model_name"],
        "accuracy": latest["average_accuracy"],
        "latency": latest["average_latency_ms"],
        "confidence": latest["average_confidence"]
    }

@router.post("/feedback")
async def submit_human_feedback(data: Dict[str, Any]):
    """
    Accepts human corrections to predictions and stores them separately.
    Does NOT retrain automatically.
    """
    # In a real system, insert this into a `human_feedback` PostgreSQL table.
    return {"status": "success", "message": "Feedback saved for future benchmark integration."}
