# SignalLens

**Evidence-Backed Customer Incident Intelligence — for Flipkart's Enterprise Catalog**

SignalLens turns a real marketplace's worth of product reviews into evidence-backed customer
incidents: what's wrong, how serious it is, which products are affected, what proves it, and
what to do next. See [`SignalLens_project_docs/ARCHITECTURE.md`](SignalLens_project_docs/ARCHITECTURE.md)
for the full architectural spec this build follows.

```
FACTS → ALGORITHMS → EVIDENCE → LLM EXPLANATION
```

Counts, growth %, impact scores, and confidence are always computed in Python/Postgres.
The LLM only labels, summarizes, and explains — it never invents a number.

## What this is

An enterprise seller/admin logs in and sees their **entire product catalog already analyzed**
— no upload step. Browse by category → product, and for any product see its real review
sentiment, rating distribution, and which cross-catalog issues (themes/incidents) it's caught
up in. The catalog is Flipkart's own: real reviews, real products, real ratings, sourced from
[Dataset-SA.csv on Kaggle](https://www.kaggle.com/datasets/niraliivaghani/flipkart-product-customer-reviews-dataset)
(205k rows; a 10,000-row stratified sample across ~940 products is what actually gets
processed, to keep the ML pipeline's runtime reasonable on CPU).

**Disclosed adaptations** (the source CSV has only 6 columns: product_name, product_price,
Rate, Review, Summary, Sentiment — no date, category, or seller column):
- `product_category` is derived from `product_name` via keyword heuristics
  (`backend/app/utils/product_category.py`) — not Flipkart's real taxonomy, which isn't in
  this dataset.
- `review_date` is synthetic (uniformly spread over the last 180 days) purely so the
  temporal-trend features (growth %, change-point detection) have something to compute over
  — the source has no date field at all.
- There's no seller/company column either; every review is of a Flipkart-sold product, so
  the demo persona represents Flipkart itself.

## Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind
- **Backend**: FastAPI + SQLAlchemy + Alembic
- **Database**: PostgreSQL + pgvector (384-dim embeddings, HNSW cosine index)
- **ML**: spaCy (sentence segmentation) · CardiffNLP RoBERTa (sentiment) ·
  `all-MiniLM-L6-v2` (embeddings) · UMAP + HDBSCAN (theme discovery) · Microsoft Presidio (PII redaction)
- **LLM**: pluggable — Gemini or Groq via `LLM_PROVIDER`, with a labeled mock fallback when no key is set

## Quickstart

1. Get `Dataset-SA.csv` and place it at `backend/data_seed/Dataset-SA.csv` (gitignored —
   not committed, ~33MB):
   ```bash
   pip install kaggle
   # username + key from kaggle.com → Settings → Create New API Token
   mkdir -p ~/.kaggle && echo '{"username":"...","key":"..."}' > ~/.kaggle/kaggle.json
   chmod 600 ~/.kaggle/kaggle.json
   kaggle datasets download -d niraliivaghani/flipkart-product-customer-reviews-dataset --unzip -p backend/data_seed
   ```
2. ```bash
   cp .env.example .env
   docker compose up --build
   ```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:3000

On first boot the backend runs migrations, seeds the demo login, ingests a 10,000-row
stratified sample of the catalog, and kicks off the full ML pipeline **in the background** —
the UI is usable immediately and fills in as processing completes (check
`GET /api/datasets/{id}/process-status`, or just watch the sidebar's dataset status badge).
If `backend/data_seed/Dataset-SA.csv` isn't present, the backend still starts normally — it
just logs a warning and skips auto-seeding (so `docker compose up` always works, even
before you've done step 1).

### Demo login

A single local demo account is seeded for you to sign in with — no real user data, no
financial data behind it:

- **Email**: `demo@signallens.app`
- **Password**: `SignalLens_Demo2026!`

Both are defined in `.env.example` (`DEMO_USER_EMAIL` / `DEMO_USER_PASSWORD`) — change them
in your own `.env` before deploying anywhere beyond your machine.

### LLM provider

`LLM_PROVIDER` in `.env` controls theme labeling, incident summaries, likely-driver
explanations, action reports, and the AI Investigator:

- `mock` (default) — no external calls; every LLM-origin field is clearly prefixed
  `[MOCK OUTPUT]` so it's never mistaken for a real model response. Everything else
  (counts, growth, impact scores, severity, likely-driver facts) is still real, since those
  are computed in Python, not by the LLM.
- `gemini` — set `GEMINI_API_KEY` (and optionally `GEMINI_MODEL` / `GEMINI_FALLBACK_MODEL`).
- `groq` — set `GROQ_API_KEY` (and optionally `GROQ_MODEL`).

### Alternate: synthetic demo dataset

Before the Flipkart pivot, this repo also shipped a synthetic-data generator
(`data/demo/generate_demo_dataset.py`) that engineers a specific "Payment Failure spike on
Android v4.8.1" incident story for architecture-style app reviews. It's no longer wired into
the default flow (the UI no longer exposes an upload step) but the script and the
`POST /api/datasets/upload` endpoint both still work if you want that scenario back — run the
script, then upload the resulting CSV via the API directly and call
`POST /api/datasets/{id}/process`.

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

Pure-logic tests (impact score, trend/change-point detection, severity rules, column
detection) run with no database. Tests touching the database (duplicate detection,
evidence collection, impact ranking) auto-skip if PostgreSQL isn't reachable and run for
real once you're on `docker compose` or have `DATABASE_URL` pointed at a live Postgres+pgvector instance.

## Evaluation notebook

`ml/evaluation/baseline_comparison.ipynb` compares VADER, DistilBERT-SST2, and the
production CardiffNLP-RoBERTa pipeline against a disclosed, template-derived labeled
sample — precision/recall/macro-F1/confusion matrix per model, never accuracy alone. See
the notebook's first cell for the ground-truth labeling disclosure.

## Project docs

- [`ARCHITECTURE.md`](SignalLens_project_docs/ARCHITECTURE.md) — architecture contract
- [`BUILD_PLAN.md`](SignalLens_project_docs/BUILD_PLAN.md) — phased build plan
- [`VIBE_CODING_RULES.md`](SignalLens_project_docs/VIBE_CODING_RULES.md) — rules for anyone (human or AI) touching this repo
