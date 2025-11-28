from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/data", response_model=List[Dict[str, Any]])
async def sync_data(last_sync_time: datetime = None):
    """
    Sync data API for mobile clients.
    Returns records updated after last_sync_time.
    """
    # Placeholder for database logic
    # In real implementation:
    # 1. Query database for records where updated_at > last_sync_time
    # 2. Return list of records
    
    mock_data = [
        {
            "id": 1,
            "title": "Example Report 1",
            "summary": "This is a summary...",
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 2,
            "title": "Example Report 2",
            "summary": "Another summary...",
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    if last_sync_time:
        # Filter logic here
        pass
        
    return mock_data

