import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import redis.asyncio as redis
from app.core.config import settings

router = APIRouter()

async def log_generator(channel: str) -> AsyncGenerator[str, None]:
    """
    Generator for Server-Sent Events (SSE).
    Subscribes to a Redis channel and yields messages.
    """
    redis_client = redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}", encoding="utf-8", decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield f"data: {message['data']}\n\n"
    except asyncio.CancelledError:
        # Client disconnected
        await pubsub.unsubscribe(channel)
    finally:
        await redis_client.close()

@router.get("/stream/{task_id}")
async def stream_logs(task_id: str, request: Request):
    """
    Stream real-time logs for a specific task using SSE.
    """
    channel = f"task_logs:{task_id}"
    return EventSourceResponse(log_generator(channel))

