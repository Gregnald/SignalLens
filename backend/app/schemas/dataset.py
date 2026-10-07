from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source: Optional[str] = None
    file_name: Optional[str] = None
    total_reviews: int
    status: str
    processing_error: Optional[str] = None
    created_at: datetime


class DatasetUploadResponse(BaseModel):
    dataset: DatasetOut
    columns_detected: dict[str, Optional[str]]
    rows_ingested: int
    rows_skipped: int
    warnings: list[str] = []


class ProcessStatus(BaseModel):
    dataset_id: int
    status: str
    stage: Optional[str] = None
    progress_percent: float = 0.0
    error: Optional[str] = None
