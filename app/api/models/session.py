from pydantic import BaseModel

class SessionResponse(BaseModel):
    session_id: str
    messages: list
    message_count: int