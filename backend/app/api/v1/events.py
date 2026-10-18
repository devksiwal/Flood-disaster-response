import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.event_bus import event_bus
from app.core.logger import logger

router = APIRouter(prefix="/events", tags=["Real-time Event Streaming"])


@router.get("/recent")
async def get_recent_events(limit: int = 30):
    """Retrieve recent event history for dashboard activity feeds."""
    return event_bus.get_recent_events(limit=limit)


@router.websocket("/ws")
async def websocket_event_stream(websocket: WebSocket):
    """WebSocket endpoint broadcasting real-time multi-agent thoughts, team dispatches, and telemetry."""
    await websocket.accept()
    await event_bus.register_websocket(websocket)
    try:
        # Send initial welcome and state sync
        await websocket.send_text(json.dumps({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to National Flood Disaster Response Event Bus",
            "recent_events": event_bus.get_recent_events(limit=10)
        }))
        while True:
            # Keep socket alive and accept ping/pong or client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "PONG"}))
    except WebSocketDisconnect:
        await event_bus.unregister_websocket(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await event_bus.unregister_websocket(websocket)


# Direct WebSocket router supporting /ws/events and /ws to match frontend and reverse proxy configurations
ws_router = APIRouter(tags=["Real-time WebSockets"])


@ws_router.websocket("/ws/events")
@ws_router.websocket("/ws")
async def websocket_ws_events(websocket: WebSocket):
    await websocket_event_stream(websocket)

