from pydantic import BaseModel

from app.config import settings


class ChatRequest(BaseModel):
    question: str
    session_id: str
    top_k: int = settings.top_k

class ChatResponse(BaseModel):
    session_id: str
    answer: str
