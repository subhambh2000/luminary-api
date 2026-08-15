from typing import AsyncGenerator

from groq import AsyncGroq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.generator import generate
from app.core.retriever import retrieve
from app.services.session_store import get_history, append

NO_MATCH_RESPONSE = (
    "I couldn't find anything in my knowledge base that matches your question.\n\n"
    "I can help with topics from a personal investment knowledge base, including:\n\n"
    "- **Mutual Funds** — types, analysis, and how to invest\n"
    "- **Stocks** — how to analyse and select individual stocks\n"
    "- **Gold ETFs** — comparison and role in a portfolio\n"
    "- **General investing concepts** — portfolio construction, risk-return tradeoffs\n\n"
    "Try rephrasing your question, or ask about one of the above areas."
)


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
    if not chunks:
        complete_response += NO_MATCH_RESPONSE
        yield NO_MATCH_RESPONSE
        yield "[DONE]"
    else:
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
