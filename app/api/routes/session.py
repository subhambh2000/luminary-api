from fastapi import APIRouter, Response, HTTPException
from app.api.models.session import SessionResponse

from app.services import session_store

router = APIRouter()


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    session_store.clear(session_id)
    return Response(status_code=204)


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    session = session_store.get_history(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session: {session_id} not found")

    messages = [dict(message) for message in session]
    message_count = len(session)

    return SessionResponse(
        session_id=session_id,
        messages=messages,
        message_count=message_count
    )
