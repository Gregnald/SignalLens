from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetOut, DatasetUploadResponse, ProcessStatus
from app.services import ingestion_service
from app.services.pipeline_service import process_dataset

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile, db: Session = Depends(get_db)) -> DatasetUploadResponse:
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(400, "Only .csv and .xlsx files are supported.")

    content = await file.read()
    try:
        df = ingestion_service.parse_upload(file.filename, content)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"Could not parse file: {exc}") from exc

    if df.empty:
        raise HTTPException(400, "Uploaded file has no rows.")

    dataset = Dataset(name=file.filename, source="upload", file_name=file.filename)
    db.add(dataset)
    db.flush()

    try:
        rows_ingested, rows_skipped, warnings, columns = ingestion_service.ingest_dataframe(
            db, dataset, df
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(400, str(exc)) from exc

    return DatasetUploadResponse(
        dataset=DatasetOut.model_validate(dataset),
        columns_detected=columns,
        rows_ingested=rows_ingested,
        rows_skipped=rows_skipped,
        warnings=warnings,
    )


@router.get("", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db)) -> list[DatasetOut]:
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).all()
    return [DatasetOut.model_validate(d) for d in datasets]


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)) -> DatasetOut:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    return DatasetOut.model_validate(dataset)


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)) -> dict:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    db.delete(dataset)
    db.commit()
    return {"deleted": True}


@router.post("/{dataset_id}/process", response_model=ProcessStatus)
def start_processing(
    dataset_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> ProcessStatus:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    if dataset.status == "processing":
        raise HTTPException(409, "Dataset is already processing")

    dataset.status = "processing"
    dataset.processing_stage = "queued"
    dataset.processing_progress = 0.0
    dataset.processing_error = None
    db.commit()

    background_tasks.add_task(process_dataset, dataset_id)

    return ProcessStatus(dataset_id=dataset_id, status="processing", stage="queued", progress_percent=0.0)


@router.get("/{dataset_id}/process-status", response_model=ProcessStatus)
def get_process_status(dataset_id: int, db: Session = Depends(get_db)) -> ProcessStatus:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    return ProcessStatus(
        dataset_id=dataset_id,
        status=dataset.status,
        stage=dataset.processing_stage,
        progress_percent=dataset.processing_progress or 0.0,
        error=dataset.processing_error,
    )
