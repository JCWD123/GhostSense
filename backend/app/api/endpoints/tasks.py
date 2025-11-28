from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.tasks.insight_tasks import run_insight_analysis
from celery.result import AsyncResult

router = APIRouter()

@router.post("/submit", response_model=Dict[str, Any])
async def submit_task(query: str):
    """
    Submit an analysis task to the Celery queue.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Submit task to Celery
    task = run_insight_analysis.delay(query)
    
    return {
        "task_id": task.id,
        "status": "submitted",
        "message": "Task successfully submitted to queue"
    }

@router.get("/status/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """
    Check the status of a specific task.
    """
    task_result = AsyncResult(task_id)
    
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    
    return result

