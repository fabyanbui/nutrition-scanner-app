from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid
import asyncio
import json
from sse_starlette.sse import EventSourceResponse

from .config import settings
from .logger import logger
from .storage import get_storage
from .cache import get_cache
from .evaluation_api import router as eval_router
from .image_quality import analyze_image_quality

NutritionScannerWorkflow = None
InferenceServiceClient = None

try:
    from ai_agents.graph.workflow import NutritionScannerWorkflow
    from ai_agents.models.llm_provider import InferenceServiceClient
except ImportError as e:
    logger.warning(f"Failed to import ai_agents: {e}")

from .db.database import get_db, engine, async_session
from .db.models import Job, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

app = FastAPI(title="Nutrition Scanner API", version="1.0.0")

@app.on_event("startup")
async def on_startup():
    logger.info("Initializing database schema")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(eval_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_queues: Dict[str, asyncio.Queue] = {}

class JobCreateResponse(BaseModel):
    job_id: str

async def process_analysis_job(job_id: str, image_bytes: bytes, storage_id: str):
    start_time = time.time()
    queue = job_queues.get(job_id)
    
    agent_metadata = []
    
    async def emit(data: dict):
        if queue:
            await queue.put(data)
            
    try:
        if InferenceServiceClient is None or NutritionScannerWorkflow is None:
            raise RuntimeError("ai_agents library is not loaded. Please verify installation.")

        model = InferenceServiceClient(base_url=settings.INFERENCE_SERVICE_URL)
        workflow = NutritionScannerWorkflow(model)
        
        initial_state = {
            "image_bytes": image_bytes,
            "foods": [],
            "ingredients": [],
            "nutrition": None,
            "quality": None,
            "metadata": {"model_name": getattr(model, "model_name", "unknown")}
        }

        # Quality check
        warnings = analyze_image_quality(image_bytes)
        if warnings:
            await emit({"agent": "quality_heuristic", "status": "completed", "warning": " | ".join(warnings)})
        else:
            await emit({"agent": "quality_heuristic", "status": "completed"})
            
        node_start_times = {}
        last_node = None
        accumulated_state = dict(initial_state)
        
        async for output in workflow.app.astream(initial_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                accumulated_state.update(state_update)
                if last_node:
                    latency = int((time.time() - node_start_times[last_node]) * 1000)
                    agent_metadata.append({"agent": last_node, "latency_ms": latency})
                    await emit({
                        "agent": last_node,
                        "status": "completed",
                        "latency_ms": latency
                    })
                
                await emit({
                    "agent": node_name,
                    "status": "running"
                })
                
                node_start_times[node_name] = time.time()
                last_node = node_name
                
                if node_name == "recognize_food" and "foods" in state_update:
                    await emit({"agent": node_name, "data": {"foods": [f.model_dump() for f in state_update["foods"]]}})
                elif node_name == "analyze_ingredients" and "ingredients" in state_update:
                    await emit({"agent": node_name, "data": {"ingredients": [i.model_dump() for i in state_update["ingredients"]]}})
                elif node_name == "estimate_nutrition" and "nutrition" in state_update and state_update["nutrition"]:
                    await emit({"agent": node_name, "data": {"nutrition": state_update["nutrition"].model_dump()}})
                elif node_name == "check_quality" and "quality" in state_update and state_update["quality"]:
                    await emit({"agent": node_name, "data": {"quality": state_update["quality"].model_dump()}})

        if last_node:
            latency = int((time.time() - node_start_times[last_node]) * 1000)
            agent_metadata.append({"agent": last_node, "latency_ms": latency})
            await emit({"agent": last_node, "status": "completed", "latency_ms": latency})

        total_latency = int((time.time() - start_time) * 1000)
        
        result_payload = {
            "foods": [f.model_dump() for f in accumulated_state.get("foods", [])],
            "ingredients": [i.model_dump() for i in accumulated_state.get("ingredients", [])],
            "nutrition": accumulated_state.get("nutrition").model_dump() if accumulated_state.get("nutrition") else None,
            "quality": accumulated_state.get("quality").model_dump() if accumulated_state.get("quality") else None,
            "processing_time_ms": total_latency
        }

        async with async_session() as db:
            stmt = select(Job).where(Job.id == job_id)
            res = await db.execute(stmt)
            job = res.scalar_one_or_none()
            if job:
                job.status = "completed"
                job.progress = 1.0
                job.result_json = result_payload
                job.agent_metadata = agent_metadata
                job.completed_at = time.strftime('%Y-%m-%d %H:%M:%S')
                await db.commit()

        logger.info(f"Job {job_id} completed successfully in {total_latency}ms")
        await emit({"status": "finished", "result": result_payload})
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
        async with async_session() as db:
            stmt = select(Job).where(Job.id == job_id)
            res = await db.execute(stmt)
            job = res.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = time.strftime('%Y-%m-%d %H:%M:%S')
                await db.commit()
            
        await emit({"status": "error", "message": f"Processing failed: {str(e)}"})

    finally:
        await asyncio.sleep(2)
        if job_id in job_queues:
            await queue.put({"_type": "close"})

@app.post("/api/v1/analyze", response_model=JobCreateResponse)
async def analyze_image_job(
    request: Request,
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.info(f"Received request {request_id}")
    
    if not file.content_type.startswith("image/"):
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be an image")
    
    content = await file.read()
    
    # Size validation
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        logger.warning(f"File too large: {size_mb}MB")
        raise HTTPException(status_code=400, detail=f"Image size exceeds {settings.MAX_IMAGE_SIZE_MB}MB limit")
        
    job_id = str(uuid.uuid4())
    
    storage = get_storage()
    storage_id = await storage.upload(content, file.content_type)
    
    new_job = Job(
        id=job_id, 
        status="queue",
        image_id=storage_id,
        image_metadata={"size_bytes": len(content), "content_type": file.content_type}
    )
    db.add(new_job)
    await db.commit()
    
    job_queues[job_id] = asyncio.Queue()
    background_tasks.add_task(process_analysis_job, job_id, content, storage_id)
    
    return JobCreateResponse(job_id=job_id)

@app.get("/api/v1/analyze/{job_id}/stream")
async def stream_analysis(job_id: str):
    queue = job_queues.get(job_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Job not found or stream expired")
        
    async def event_generator():
        try:
            while True:
                data = await queue.get()
                if data.get("_type") == "close":
                    break
                yield {
                    "event": "message",
                    "data": json.dumps(data)
                }
        except asyncio.CancelledError:
            pass
            
    return EventSourceResponse(event_generator())

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/ready")
def ready_check():
    return {"status": "ready"}

@app.get("/status")
def status_check():
    return {"environment": settings.ENV, "version": "1.0.0"}

@app.get("/metrics")
def metrics():
    # To be extended with Prometheus or similar later
    return {"status": "ok"}
