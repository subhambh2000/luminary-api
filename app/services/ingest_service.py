import asyncio
import logging

import time
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.chunker import chunk_folder
from app.core.embedder import embed
from app.utils.errors import IngestException

BATCH_SIZE = 100


async def ingest(
        notes_folder: str,
        qdrant_client: QdrantClient,
        model: SentenceTransformer,
        recreate_collection: bool = False
) -> tuple[int, float]:
    start = time.perf_counter()

    try:
        chunks = await asyncio.to_thread(chunk_folder, notes_folder)
    except Exception as e:
        raise IngestException(f"Failed to chunk, {str(e)}")

    contents = [chunk["content"] for chunk in chunks]

    vectors = await asyncio.to_thread(embed, contents, model)

    collection_name = settings.collection_name
    vector_params = VectorParams(
        size=settings.vector_size,
        distance=Distance.COSINE
    )

    if recreate_collection:
        logging.info(f"Recreating collection: {collection_name}")
        qdrant_client.delete_collection(collection_name)
        qdrant_client.create_collection(collection_name, vectors_config=vector_params)
    else:
        if not qdrant_client.collection_exists(collection_name):
            logging.info(f"Collection: {collection_name} does not exist, creating collection")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=vector_params
            )

    points = [
        PointStruct(
            id=chunk["chunk_id"],
            vector=vector,
            payload={
                "content": chunk["content"],
                "source_file": chunk["source_file"],
                "folder": chunk["folder"],
                "header_path": chunk["header_path"],
                "char_count": chunk["char_count"]
            }
        ) for chunk, vector in zip(chunks, vectors)]

    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i: i + BATCH_SIZE]
        await asyncio.to_thread(qdrant_client.upsert, collection_name=collection_name, points=batch)
        logging.debug(f"Upserted batch: {i // BATCH_SIZE + 1} ({len(batch)} points)")

    duration = time.perf_counter() - start
    return len(chunks), duration
