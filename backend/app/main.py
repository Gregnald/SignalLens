import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, dashboard, datasets, incidents, integrity, products, reviews, themes
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title="SignalLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(dashboard.router)
app.include_router(themes.router)
app.include_router(incidents.evidence_router)  # GET /{incident_id}/evidence
# Must come after evidence_router: GET /{dataset_id}/{incident_id} below is also a
# 2-segment pattern, so if it's checked first, a request to /{id}/evidence matches it
# too (dataset_id=id, incident_id="evidence") and fails type-converting "evidence" to
# int — Starlette doesn't backtrack to try the next route once one has matched.
app.include_router(incidents.router)
app.include_router(reviews.router)
app.include_router(chat.router)
app.include_router(integrity.router)
app.include_router(products.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
