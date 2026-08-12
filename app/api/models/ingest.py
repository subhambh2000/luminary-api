from pydantic import BaseModel

class IngestRequest(BaseModel):
    notes_folder: str = ""
    recreate_collection: bool = False

class IngestResponse(BaseModel):
    status: str = ""
    chunks_ingested: int
    duration_seconds: float
