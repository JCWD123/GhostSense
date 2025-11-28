from app.core.celery_app import celery_app
from app.tasks.engine_wrapper import run_insight_engine_logic
from loguru import logger
import time

@celery_app.task(bind=True)
def run_insight_analysis(self, query: str):
    """
    Celery task to run Insight Engine analysis with real-time logging via Redis.
    """
    task_id = self.request.id
    
    # Run the actual engine logic
    try:
        report_content = run_insight_engine_logic(task_id, query)
        
        result = {
            "report_content": report_content,
            "generated_at": str(time.time()),
            "status": "success"
        }
        return result
        
    except Exception as e:
        logger.exception(f"Task {task_id} failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }
