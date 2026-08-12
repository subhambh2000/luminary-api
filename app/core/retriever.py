import asyncio

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.embedder import embed_one
from app.utils.errors import RetrievalException, CollectionNotFoundException


async def retrieve(
        query: str,
        model: SentenceTransformer,
        client: QdrantClient,
        top_k: int,
        threshold: float
) -> list[dict]:
    if not client.collection_exists(settings.collection_name):
        raise CollectionNotFoundException(
            f"Collection '{settings.collection_name}' not found. Run /api/ingest first."
        )

    embedded_query = await asyncio.to_thread(embed_one, query, model, "query")

    try:
        response = await asyncio.to_thread(client.query_points,
                                           collection_name=settings.collection_name,
                                           query=embedded_query,  # type: ignore
                                           limit=top_k,
                                           score_threshold=threshold,
                                           with_payload=True
                                           )
    except Exception as e:
        raise RetrievalException(f"Query error: {str(e)}")

    query_results = [
        {
            "content": point.payload["content"],
            "source_file": point.payload["source_file"],
            "header_path": point.payload["header_path"],
            "folder": point.payload["folder"],
            "score": point.score
        }
        for point in response.points
    ]

    seen = set()
    deduplicated: list[dict] = []

    for result in query_results:
        key = result["header_path"] + result["source_file"]
        if key not in seen:
            seen.add(key)
            deduplicated.append(result)

    return deduplicated
