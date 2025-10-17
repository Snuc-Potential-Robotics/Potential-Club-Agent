"""
Nemo AI Assistant - FastAPI Backend
Main application entry point with WebSocket and REST API endpoints.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import logging
import uuid
import asyncio
from datetime import datetime
import json

from config.settings import settings
from models.schemas import ChatRequest, ChatResponse, ChatMessage, MessageRole
from agents.nemo_agent import NemoAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Nemo Agent
nemo_agent: Optional[NemoAgent] = None

# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_times: Dict[str, datetime] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_times[session_id] = datetime.now()
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            del self.connection_times[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        """Send message to specific connection."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
    
    def is_connected(self, session_id: str) -> bool:
        """Check if session is connected."""
        return session_id in self.active_connections
    
    async def cleanup_inactive_connections(self):
        """Remove connections that have been idle for too long."""
        current_time = datetime.now()
        timeout_seconds = settings.ws_timeout
        
        sessions_to_remove = []
        for session_id, connect_time in self.connection_times.items():
            if (current_time - connect_time).total_seconds() > timeout_seconds:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            if session_id in self.active_connections:
                try:
                    await self.active_connections[session_id].close()
                except Exception as e:
                    logger.error(f"Error closing connection {session_id}: {e}")
            self.disconnect(session_id)
            logger.info(f"Cleaned up inactive connection: {session_id}")


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global nemo_agent
    
    try:
        logger.info("Starting Nemo AI Assistant API...")
        
        # Initialize Nemo Agent
        nemo_agent = NemoAgent()
        logger.info("Nemo Agent initialized successfully")
        
        # Start cleanup task
        asyncio.create_task(periodic_cleanup())
        
        logger.info("✅ API started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start API: {str(e)}")
        raise


async def periodic_cleanup():
    """Periodically clean up inactive connections."""
    while True:
        await asyncio.sleep(60)  # Check every minute
        await manager.cleanup_inactive_connections()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Nemo AI Assistant",
        "version": settings.api_version,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Nemo AI Assistant API",
        "version": settings.api_version,
        "endpoints": {
            "websocket": "/ws/chat/{session_id}",
            "rest": "/api/chat",
            "health": "/health"
        },
        "docs": "/docs"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    REST endpoint for chat messages.
    Fallback option if WebSocket is not available.
    """
    try:
        if not nemo_agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process message
        result = await nemo_agent.process_message(
            message=request.message,
            session_id=session_id
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            suggestions=result.get("suggestions"),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat.
    
    Message format:
    - Incoming: {"type": "message", "content": "user message"}
    - Outgoing: {"type": "response", "content": "assistant response", "suggestions": [...]}
    """
    await manager.connect(session_id, websocket)
    
    try:
        # Send welcome message
        if nemo_agent:
            welcome = nemo_agent.get_welcome_message()
            await manager.send_message(session_id, {
                "type": "response",
                "content": welcome["response"],
                "suggestions": welcome["suggestions"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                message_type = data.get("type")
                message_content = data.get("content")
                
                if message_type == "message" and message_content:
                    logger.info(f"Received message from {session_id}: {message_content}")
                    
                    # Send typing indicator
                    await manager.send_message(session_id, {
                        "type": "typing",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Process message with agent
                    if nemo_agent:
                        result = await nemo_agent.process_message(
                            message=message_content,
                            session_id=session_id
                        )
                        
                        # Send response
                        await manager.send_message(session_id, {
                            "type": "response",
                            "content": result["response"],
                            "suggestions": result.get("suggestions", []),
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "content": "Agent not available",
                            "timestamp": datetime.now().isoformat()
                        })
                
                elif message_type == "ping":
                    # Respond to heartbeat
                    await manager.send_message(session_id, {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Update connection time
                manager.connection_times[session_id] = datetime.now()
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from {session_id}")
                await manager.send_message(session_id, {
                    "type": "error",
                    "content": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
        manager.disconnect(session_id)
        
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {str(e)}")
        manager.disconnect(session_id)


@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    try:
        if not nemo_agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        history = nemo_agent.get_session_history(session_id)
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": history
        }
        
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear session data."""
    try:
        if not nemo_agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        nemo_agent.clear_session(session_id)
        
        return {
            "message": f"Session {session_id} cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.environment == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
