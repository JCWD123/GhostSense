import sys
import os
from pathlib import Path

# Add project root to sys.path to ensure imports work correctly
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.core.insight_engine.agent import DeepSearchAgent as InsightAgent
from app.core.media_engine.agent import DeepSearchAgent as MediaAgent
from app.core.config import settings
from loguru import logger
import time
import redis
import json

# Initialize Redis client for publishing logs
redis_client = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB,
    decode_responses=True
)

def publish_log(task_id: str, message: str):
    """Publish log message to Redis channel"""
    channel = f"task_logs:{task_id}"
    redis_client.publish(channel, message)

class CeleryLogger:
    """Redirects Loguru logs to Redis Pub/Sub for a specific task."""
    def __init__(self, task_id):
        self.task_id = task_id

    def write(self, message):
        if message.strip():
             publish_log(self.task_id, message.strip())
             
    def flush(self):
        pass

def run_insight_engine_logic(task_id: str, query: str):
    """
    Wrapper to run Insight Engine logic within Celery.
    Interceds logger to capture output.
    """
    publish_log(task_id, f"Initializing Insight Engine for query: {query}")
    
    # Configure custom sink for this task
    logger.remove()
    logger.add(CeleryLogger(task_id).write, format="{message}")
    
    try:
        # Initialize Agent
        # Note: We might need to adjust Config passing here if InsightEngine relies on global settings
        # For now, assuming it reads from env or we can mock it
        
        agent = InsightAgent() 
        publish_log(task_id, "Agent initialized. Starting research...")
        
        report = agent.research(query)
        publish_log(task_id, "Research completed.")
        
        return report
        
    except Exception as e:
        error_msg = f"Error in Insight Engine: {str(e)}"
        logger.error(error_msg)
        publish_log(task_id, error_msg)
        raise e

