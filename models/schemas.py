"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Show me upcoming events",
                "timestamp": "2025-10-04T10:30:00Z"
            }
        }


class ChatRequest(BaseModel):
    """Chat request from client."""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to register for the robotics workshop",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ChatResponse(BaseModel):
    """Chat response to client."""
    response: str
    session_id: str
    suggestions: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I found 3 upcoming events. Would you like to see them?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "suggestions": ["Show events", "Register for event", "Submit feedback"],
                "timestamp": "2025-10-04T10:30:00Z"
            }
        }


class Event(BaseModel):
    """Event model."""
    id: str
    name: str
    description: Optional[str] = None
    date: datetime
    location: Optional[str] = None
    total_slots: int
    available_slots: int
    is_active: bool = True
    is_full: bool = False
    created_at: datetime
    updated_at: datetime
    
    @field_validator('is_full', mode='before')
    @classmethod
    def calculate_is_full(cls, v, info):
        """Calculate if event is full."""
        if 'available_slots' in info.data:
            return info.data['available_slots'] <= 0
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Robotics Workshop",
                "description": "Learn robotics basics",
                "date": "2025-10-15T14:00:00Z",
                "location": "Lab A",
                "total_slots": 30,
                "available_slots": 15,
                "is_active": True,
                "is_full": False,
                "created_at": "2025-10-01T10:00:00Z",
                "updated_at": "2025-10-01T10:00:00Z"
            }
        }


class RegistrationStatus(str, Enum):
    """Registration status enum."""
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLIST = "waitlist"


class RegistrationRequest(BaseModel):
    """Registration request model."""
    event_id: str
    user_name: str = Field(..., min_length=2, max_length=100)
    user_email: EmailStr
    user_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_name": "John Doe",
                "user_email": "john@example.com",
                "user_phone": "+1234567890"
            }
        }


class Registration(BaseModel):
    """Registration model."""
    id: str
    event_id: str
    user_name: str
    user_email: EmailStr
    user_phone: Optional[str] = None
    registration_date: datetime
    status: RegistrationStatus = RegistrationStatus.CONFIRMED
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_name": "John Doe",
                "user_email": "john@example.com",
                "user_phone": "+1234567890",
                "registration_date": "2025-10-04T10:30:00Z",
                "status": "confirmed"
            }
        }


class FeedbackRequest(BaseModel):
    """Feedback request model."""
    event_id: str
    user_email: EmailStr
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_email": "john@example.com",
                "rating": 5,
                "comments": "Great event! Learned a lot."
            }
        }


class Feedback(BaseModel):
    """Feedback model."""
    id: str
    event_id: str
    user_email: EmailStr
    rating: int
    comments: Optional[str] = None
    submitted_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_email": "john@example.com",
                "rating": 5,
                "comments": "Great event!",
                "submitted_at": "2025-10-04T10:30:00Z"
            }
        }
