import logging
from pathlib import Path

import groq
from starlette.responses import JSONResponse

from app.api.routes.ingest import router as ingest_router
from app.api.routes.chat import router as chat_router
from app.api.routes.session import router as session_router
from app.config import settings

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from qdrant_client import QdrantClient

from app.core.embedder import load_model
from app.utils.errors import LuminaryException
from app.utils.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup - runs once before first request
    logger.info(f"Starting {settings.app_name}...")
    app.state.model = load_model(settings.embedding_model)
    app.state.qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    app.state.llm_client = groq.AsyncGroq(api_key=settings.api_key)
    logger.info(f"Qdrant connected at {settings.qdrant_host}:{settings.qdrant_port}")

    yield

    # shutdown - runs on Ctrl+C
    app.state.qdrant.close()
    logger.info(f"Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    description="A Retrieval-Augmented generation framework for you personal knowledge base.",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router=ingest_router, prefix="/api")
app.include_router(router=chat_router, prefix="/api")
app.include_router(router=session_router, prefix="/api")


@app.get("/")
async def chat_ui():
    return FileResponse("app/static/chat.html")


@app.exception_handler(LuminaryException)
async def luminary_exception_handler(request, exception):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.error_type, "detail": str(exception)}
    )


# noinspection PyBroadException
@app.get("/health")
async def health(request: Request):
    qdrant_ok = False
    try:
        request.app.state.qdrant.get_collections()
        qdrant_ok = True
    except Exception:
        pass

    return {
        "status": "ok" if qdrant_ok else "degraded",
        "app": settings.app_name,
        "model": settings.embedding_model,
        "qdrant": "connected" if qdrant_ok else "unreachable"
    }
