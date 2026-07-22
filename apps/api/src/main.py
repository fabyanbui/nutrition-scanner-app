from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid
import asyncio
import json
from sse_starlette.sse import EventSourceResponse
from .evaluation_api import router as eval_router
from .image_quality import analyze_image_quality

# We will handle missing path in docker container via proper pythonpath or setup.py
try:
    from ai_agents.graph.workflow import NutritionScannerWorkflow
    from ai_agents.models.llm_provider import LlavaModel
except ImportError:
    pass

from .db.database import get_db
from .db.models import Job, Base
from .db.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

app = FastAPI(title="Nutrition Scanner API", version="1.0.0")

@app.on_event("startup")
async def on_startup():
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

# Global queue registry for SSE
job_queues: Dict[str, asyncio.Queue] = {}

class JobCreateResponse(BaseModel):
    job_id: str

async def process_analysis_job(job_id: str, image_bytes: bytes, db: AsyncSession):
    start_time = time.time()
    queue = job_queues.get(job_id)
    
    async def emit(data: dict):
        if queue:
            await queue.put(data)
            
    try:
        model = LlavaModel()
        workflow = NutritionScannerWorkflow(model)
        
        initial_state = {
            "image_bytes": image_bytes,
            "foods": [],
            "ingredients": [],
            "nutrition": None,
            "quality": None,
            "metadata": {"model_name": getattr(model, "model_name", "unknown")}
        }

        # Run heuristic quality check before ML graph
        warnings = analyze_image_quality(image_bytes)
        if warnings:
            await emit({"agent": "quality_heuristic", "status": "completed", "warning": " | ".join(warnings)})
        else:
            await emit({"agent": "quality_heuristic", "status": "completed"})
        
        # Stream from langgraph
        node_start_times = {}
        last_node = None
        
        async for output in workflow.app.astream(initial_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                if last_node:
                    latency = int((time.time() - node_start_times[last_node]) * 1000)
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
                
                # We can also yield intermediate data if we want
                # Let's emit the updated state for the frontend to consume
                if node_name == "recognize_food" and "foods" in state_update:
                    await emit({"agent": node_name, "data": {"foods": [f.model_dump() for f in state_update["foods"]]}})
                elif node_name == "analyze_ingredients" and "ingredients" in state_update:
                    await emit({"agent": node_name, "data": {"ingredients": [i.model_dump() for i in state_update["ingredients"]]}})
                elif node_name == "estimate_nutrition" and "nutrition" in state_update and state_update["nutrition"]:
                    await emit({"agent": node_name, "data": {"nutrition": state_update["nutrition"].model_dump()}})
                elif node_name == "check_quality" and "quality" in state_update and state_update["quality"]:
                    await emit({"agent": node_name, "data": {"quality": state_update["quality"].model_dump()}})

        # Finish the last node
        if last_node:
            latency = int((time.time() - node_start_times[last_node]) * 1000)
            await emit({"agent": last_node, "status": "completed", "latency_ms": latency})

        # Fetch final state to get the full result
        final_state = await workflow.app.ainvoke(initial_state)

        total_latency = int((time.time() - start_time) * 1000)
        
        # Format the result nicely
        result_payload = {
            "foods": [f.model_dump() for f in final_state.get("foods", [])],
            "ingredients": [i.model_dump() for i in final_state.get("ingredients", [])],
            "nutrition": final_state.get("nutrition").model_dump() if final_state.get("nutrition") else None,
            "quality": final_state.get("quality").model_dump() if final_state.get("quality") else None,
            "processing_time_ms": total_latency
        }

        # Update DB
        stmt = select(Job).where(Job.id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if job:
            job.status = "completed"
            job.progress = 1.0
            job.result_json = result_payload
            job.completed_at = time.strftime('%Y-%m-%d %H:%M:%S')
            await db.commit()

        await emit({"status": "finished", "result": result_payload})
        
    except Exception as e:
        stmt = select(Job).where(Job.id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = time.strftime('%Y-%m-%d %H:%M:%S')
            await db.commit()
            
        await emit({"status": "error", "message": str(e)})

    finally:
        # Give clients time to receive the last event before closing queue
        await asyncio.sleep(2)
        if job_id in job_queues:
            # We don't remove it immediately, just put a close marker
            await queue.put({"_type": "close"})

@app.post("/api/v1/analyze", response_model=JobCreateResponse)
async def analyze_image_job(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    content = await file.read()
    job_id = str(uuid.uuid4())
    
    # Create DB Record
    new_job = Job(id=job_id, status="queue")
    db.add(new_job)
    await db.commit()
    
    # Initialize Queue
    job_queues[job_id] = asyncio.Queue()
    
    background_tasks.add_task(process_analysis_job, job_id, content, db)
    
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
