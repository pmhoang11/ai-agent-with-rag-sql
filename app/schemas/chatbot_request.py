from typing import Optional

from pydantic import BaseModel



class ChatRequest(BaseModel):
    """ChatbotRequest request schema."""
    question: str
    user_id: int
    space_id: int
    thread_id: str
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Which workspace did I update most recently?",
                "user_id": 1,
                "space_id": 1,
                "thread_id": "abc678"
            }
        }

