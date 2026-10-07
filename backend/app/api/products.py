from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import CategoryOut, ProductDetail, ProductSummary
from app.services.product_service import get_product_detail, list_categories, list_products

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/{dataset_id}/categories", response_model=list[CategoryOut])
def get_categories(dataset_id: int, db: Session = Depends(get_db)) -> list[CategoryOut]:
    return list_categories(db, dataset_id)


@router.get("/{dataset_id}", response_model=list[ProductSummary])
def get_products(
    dataset_id: int, category: str | None = Query(None), db: Session = Depends(get_db)
) -> list[ProductSummary]:
    return list_products(db, dataset_id, category)


@router.get("/{dataset_id}/detail", response_model=ProductDetail)
def get_product(
    dataset_id: int, product_name: str = Query(...), db: Session = Depends(get_db)
) -> ProductDetail:
    detail = get_product_detail(db, dataset_id, product_name)
    if not detail:
        raise HTTPException(404, "Product not found")
    return detail
