FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# CPU-only torch build — avoids pulling ~3GB of unused CUDA runtime libraries that the
# default PyPI wheel depends on; this backend never does GPU inference.
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

# Migrations must succeed (schema correctness is non-negotiable), but a seed-data bug
# must never take the whole API down — seed steps are best-effort.
CMD ["sh", "-c", "alembic upgrade head && (python -m app.seed || true) && (python -m app.seed_flipkart || true) && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
