from pydantic import BaseModel, Field
from typing import Optional, List

class RetrievedChunk(BaseModel):
    text: str
    source_document: str
    section: str
    page_number: int
    relevance_score: float