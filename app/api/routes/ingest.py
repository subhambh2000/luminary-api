import logging
from http import HTTPStatus

from fastapi import APIRouter, Request

from app.api.models.ingest import IngestRequest, IngestResponse
from app.services.ingest_service import ingest

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse, status_code=HTTPStatus.OK)
async def ingest_endpoint(
        payload: IngestRequest,
        request: Request
):
    qdrant_client = request.app.state.qdrant
    model = request.app.state.model

    logging.info("Ingesting notes...")
    chunks_size, duration = await ingest(
        notes_folder=payload.notes_folder,
        model=model,
        qdrant_client=qdrant_client,
        recreate_collection=payload.recreate_collection
    )

    logging.info("Ingestion complete...")
    return IngestResponse(
        status="success",
        chunks_ingested=chunks_size,
        duration_seconds=duration
    )
