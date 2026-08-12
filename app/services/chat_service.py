from typing import AsyncGenerator

from groq import AsyncGroq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.generator import generate
from app.core.retriever import retrieve
from app.services.session_store import get_history, append


async def stream_chat(
        question: str,
        session_id: str,
        qdrant_client: QdrantClient,
        model: SentenceTransformer,
        llm_client: AsyncGroq
) -> AsyncGenerator[str, None]:
    history = get_history(session_id)
    chunks = await retrieve(question, model, qdrant_client, settings.top_k, settings.score_threshold)

    complete_response = ""
    async for token in generate(
            client=llm_client,
            model=settings.generative_model,
            question=question,
            chunks=chunks,
            history=history
    ):
        complete_response += token
        yield token

    append(session_id=session_id, role="user", content=question)
    append(session_id=session_id, role="assistant", content=complete_response)

    yield "[DONE]"
