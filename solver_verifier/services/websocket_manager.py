"""WebSocket connection manager for real-time progress updates."""

import json
import asyncio
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from ..models.progress import ProgressUpdate


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # session_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        async with self._lock:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)
        
        print(f"✅ WebSocket connected for session: {session_id}")
    
    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            if session_id in self.active_connections:
                self.active_connections[session_id].discard(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
        
        print(f"❌ WebSocket disconnected for session: {session_id}")
    
    async def send_update(self, session_id: str, update: ProgressUpdate):
        """Send an update to all connections for a session."""
        if session_id not in self.active_connections:
            return
        
        # Convert update to JSON
        message = update.model_dump_json()
        
        # Send to all active connections for this session
        connections_to_remove = set()
        
        for websocket in self.active_connections[session_id].copy():
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"⚠️  Failed to send WebSocket message: {e}")
                connections_to_remove.add(websocket)
        
        # Clean up failed connections
        async with self._lock:
            for websocket in connections_to_remove:
                self.active_connections[session_id].discard(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_to_session(self, session_id: str, message_type: str, data: dict):
        """Send a custom message to all connections for a session."""
        update = ProgressUpdate(
            type=message_type,
            session_id=session_id,
            timestamp=datetime.now(),
            data=data
        )
        await self.send_update(session_id, update)
    
    def get_connection_count(self, session_id: str) -> int:
        """Get the number of active connections for a session."""
        return len(self.active_connections.get(session_id, set()))
    
    async def broadcast_to_all(self, update: ProgressUpdate):
        """Broadcast an update to all active sessions."""
        for session_id in list(self.active_connections.keys()):
            await self.send_update(session_id, update)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()