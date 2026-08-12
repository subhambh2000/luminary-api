from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Request

from app.api.models.chat import ChatRequest
from app.services.chat_service import stream_chat

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(payload: ChatRequest, request: Request):
    qdrant_client = request.app.state.qdrant
    model = request.app.state.model
    llm_client = request.app.state.llm_client

    return StreamingResponse(
        stream_chat(
            question=payload.question,
            session_id=payload.session_id,
            qdrant_client=qdrant_client,
            model=model,
            llm_client=llm_client
        ),
        media_type="text/event-stream"
    )