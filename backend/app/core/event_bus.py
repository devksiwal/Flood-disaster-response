import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Callable, Any, Set
from fastapi import WebSocket
from app.core.logger import logger


class EventBus:
    """Central Async Pub/Sub Event Bus for Multi-Agent coordination and real-time frontend streaming."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}
        self._active_websockets: Set[WebSocket] = set()
        self._event_history: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], Any]):
        """Subscribe a backend callback to a specific event type or '*' for all."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def register_websocket(self, websocket: WebSocket):
        """Register a new WebSocket client for live event push."""
        await self._lock.acquire()
        try:
            self._active_websockets.add(websocket)
            logger.info(f"WebSocket client connected. Total active clients: {len(self._active_websockets)}")
        finally:
            self._lock.release()

    async def unregister_websocket(self, websocket: WebSocket):
        """Remove a disconnected WebSocket client."""
        await self._lock.acquire()
        try:
            self._active_websockets.discard(websocket)
            logger.info(f"WebSocket client disconnected. Total active clients: {len(self._active_websockets)}")
        finally:
            self._lock.release()

    async def publish(self, event_type: str, data: Dict[str, Any]):
        """Publish an event to local listeners and all connected WebSocket clients."""
        event = {
            "id": f"evt-{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Keep last 100 events in history
        self._event_history.append(event)
        if len(self._event_history) > 100:
            self._event_history.pop(0)

        # Notify local handlers
        handlers = self._subscribers.get(event_type, []) + self._subscribers.get("*", [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(event))
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error executing event handler for '{event_type}': {e}")

        # Broadcast to WebSocket clients
        await self._broadcast_to_websockets(event)

    async def _broadcast_to_websockets(self, event: Dict[str, Any]):
        if not self._active_websockets:
            return

        message = json.dumps(event)
        dead_clients = []
        
        for ws in list(self._active_websockets):
            try:
                await ws.send_text(message)
            except Exception:
                dead_clients.append(ws)

        if dead_clients:
            async with self._lock:
                for ws in dead_clients:
                    self._active_websockets.discard(ws)

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._event_history[-limit:]


# Global EventBus instance
event_bus = EventBus()
