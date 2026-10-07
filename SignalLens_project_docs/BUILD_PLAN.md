# SignalLens — Build Plan

## Phase 0 — Repository setup

Create:

```text
backend/
frontend/
data/
ml/
docker-compose.yml
ARCHITECTURE.md
VIBE_CODING_RULES.md
```

Deliverable:
- repository runs
- frontend opens
- backend health endpoint works
- PostgreSQL connects

---

## Phase 1 — Database

Implement:
- datasets
- reviews
- feedback_units
- themes
- incidents
- evidence
- human_feedback

Add Alembic migrations.

Deliverable:

```text
POST /api/datasets/upload
GET /api/datasets
```

---

## Phase 2 — Ingestion

Support:
- CSV
- XLSX

Automatically detect likely columns:
- review/text
- rating
- date
- version
- platform
- device
- country

Validate schema.

Deliverable:
uploaded reviews appear in PostgreSQL.

---

## Phase 3 — Cleaning + PII

Implement:
- whitespace normalization
- Unicode normalization
- empty-review filtering
- duplicate detection
- Presidio PII redaction

Deliverable:
raw and cleaned review counts visible.

---

## Phase 4 — Feedback Units

Use spaCy sentence segmentation.

Each sentence becomes a candidate feedback unit.

Deliverable:
review detail page shows sentence-level units.

---

## Phase 5 — Sentiment

Load:

```text
cardiffnlp/twitter-roberta-base-sentiment-latest
```

Store:
- sentiment
- confidence

Deliverable:
sentiment distribution and sentence-level sentiment.

---

## Phase 6 — Embeddings

Load:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Generate 384-dimensional embeddings.

Store in pgvector.

Create cosine HNSW index when appropriate.

Deliverable:
semantic search works.

---

## Phase 7 — Issue discovery

Implement:
- UMAP
- HDBSCAN
- representative samples
- cluster statistics

Deliverable:
candidate clusters appear.

---

## Phase 8 — Theme labeling

Use Gemini structured output.

Input:
- cluster examples
- cluster size
- sentiment
- representative phrases

Output:
- theme name
- category
- description
- severity suggestion

Deliverable:
human-readable themes.

---

## Phase 9 — Temporal intelligence

Calculate:
- volume by day
- baseline
- growth
- z-score
- rating trend
- change point

Deliverable:
theme trend chart.

---

## Phase 10 — Emerging issues

Detect:
- new clusters
- low similarity to existing themes
- increasing frequency

Deliverable:

```text
NEW ISSUE DETECTED
```

---

## Phase 11 — Impact engine

Implement:

```text
0.25 Volume
0.20 Growth
0.25 Severity
0.10 Negative Sentiment
0.10 Reach
0.10 Confidence
```

Deliverable:
ranked incident candidates.

---

## Phase 12 — Incident engine

Generate incident objects from high-impact themes.

Add:
- severity
- title
- summary
- first detected
- likely driver
- confidence
- affected segments

Deliverable:
Incident Radar.

---

## Phase 13 — Evidence engine

For each incident retrieve:
- representative reviews
- supporting review count
- strongest semantic examples
- temporal evidence
- affected segments

Deliverable:
Incident Detail page.

---

## Phase 14 — Feedback integrity

Implement:
- near duplicates
- burst detection
- rating/text contradiction

Deliverable:
Integrity Monitor.

---

## Phase 15 — Action generator

Use Gemini to produce:

```text
problem
impact
affected users
likely driver
evidence
recommended owner
priority
next steps
```

Deliverable:
engineering report.

---

## Phase 16 — AI Investigator

Implement grounded retrieval:

```text
question
 ↓
intent detection
 ↓
database metrics
 ↓
relevant incidents
 ↓
evidence retrieval
 ↓
Gemini
 ↓
answer + citations/evidence IDs
```

Deliverable:
working investigator.

---

## Phase 17 — Evaluation

Create a manually labeled sample of 300–500 reviews.

Measure:
- sentiment macro F1
- precision
- recall
- confusion matrix
- theme agreement
- severity agreement

Compare with:
- VADER
- RoBERTa
- our pipeline

Deliverable:
Evaluation page for the presentation.

---

## Phase 18 — Demo dataset

Create a controlled demo scenario containing:
- 10,000 reviews
- several normal issues
- one major payment regression
- release metadata
- platform metadata
- device metadata
- suspicious feedback burst

The demo must reliably produce:

```text
Payment Failure
+327%
Android
v4.8.1
Critical
Impact ≈ 94
```

If synthetic metadata is used, disclose it.

---

## Phase 19 — Final UI

Polish:
- dark/light visual consistency
- responsive cards
- animations only where useful
- skeleton loaders
- empty states
- error states
- filters
- evidence drill-down

Do not sacrifice correctness for animation.

---

## Phase 20 — Final presentation

Demo sequence:

1. Upload 10,000 reviews.
2. Show processing.
3. Open Executive Dashboard.
4. Click "What Changed?"
5. Show Payment Failure +327%.
6. Open Incident.
7. Show likely driver: Android v4.8.1.
8. Show supporting reviews.
9. Open Feedback Integrity.
10. Show suspicious burst.
11. Generate engineering report.
12. Ask AI Investigator:
   "What should engineering fix first?"
13. Show evidence-backed answer.
14. Show evaluation metrics.

End with:

> "We don't summarize feedback. We detect customer incidents and provide the evidence needed to act."

---

## Minimum viable hackathon build

If time collapses, finish these first:

1. ingestion
2. PII
3. sentiment
4. embeddings
5. clustering
6. themes
7. trends
8. impact
9. incidents
10. evidence
11. dashboard

Then add:
12. integrity
13. action generator
14. investigator

Never skip evidence.
