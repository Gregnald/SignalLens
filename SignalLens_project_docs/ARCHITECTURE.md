# SignalLens — Architecture Specification

## 1. Product

**SignalLens — Evidence-Backed Customer Incident Intelligence**

### One-line pitch
SignalLens does not merely summarize customer reviews. It detects emerging customer problems, measures their impact, explains what changed, provides evidence, and recommends what the product team should do next.

### Core loop

Reviews → Clean/PII → Atomic Feedback Units → Sentiment + Embeddings → Issue Discovery → Theme Labeling → Temporal Intelligence → Segment Analysis → Impact Scoring → Evidence → Incident → Action → Human Feedback

---

## 2. Non-negotiable architecture

```text
CSV/XLSX/API
    ↓
Ingestion + validation
    ↓
Cleaning + normalization
    ↓
Microsoft Presidio PII redaction
    ↓
Atomic feedback-unit extraction
    ↓
 ┌───────────────────────┬─────────────────────────┐
 │ Sentiment             │ Embeddings              │
 │ CardiffNLP RoBERTa    │ all-MiniLM-L6-v2        │
 └───────────┬───────────┴────────────┬────────────┘
             ↓                        ↓
              Semantic issue discovery
              UMAP + HDBSCAN/BERTopic
                         ↓
                 Gemini theme labeling
                         ↓
                 Temporal intelligence
                         ↓
                  Segment analysis
                         ↓
                   Impact scoring
                         ↓
                Incident generation
                         ↓
                  Evidence engine
                         ↓
             Likely-driver hypothesis
                         ↓
                    FastAPI API
                         ↓
                  Next.js dashboard
```

---

## 3. Exact stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts
- Lucide

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database
- PostgreSQL
- pgvector

### NLP/ML
- spaCy for sentence segmentation
- `cardiffnlp/twitter-roberta-base-sentiment-latest` for sentiment baseline
- `sentence-transformers/all-MiniLM-L6-v2` for 384-dimensional embeddings
- UMAP + HDBSCAN / BERTopic-style discovery

### PII
- Microsoft Presidio

### Generative AI
- Gemini Flash model configured through `GEMINI_MODEL`
- Default value must be configurable in `.env`
- All structured LLM tasks use JSON/Pydantic schemas

### Deployment
- Docker
- docker-compose

Do not add a second database, vector database, Node backend, or microservice unless the architecture owner explicitly approves it.

---

## 4. Responsibilities

### Python/ML
Responsible for:
- ingestion
- validation
- cleaning
- PII redaction
- sentence splitting
- feedback-unit extraction
- sentiment
- embeddings
- clustering
- theme discovery
- anomaly detection
- temporal metrics
- impact scoring

### PostgreSQL
Responsible for:
- persistent data
- relationships
- aggregation
- filtering
- time-series queries
- vector search

### Gemini
Responsible only for:
- theme naming
- theme descriptions
- incident explanations
- likely-driver hypotheses
- recommendations
- engineering reports
- grounded investigator answers

Gemini must never be the source of truth for counts, percentages, dates, ratings, growth, or statistical metrics.

### Next.js
Responsible for:
- dashboard
- incident radar
- issue explorer
- evidence explorer
- integrity monitor
- AI investigator
- action report UI

---

## 5. Fundamental data object: Feedback Unit

A review may contain multiple independent observations.

Example:

> "The new UI is beautiful but payment keeps failing and support doesn't answer."

Must become:

1. UI → positive
2. Payment failure → negative
3. Support response → negative

A feedback unit contains:
- review_id
- text
- offsets
- sentiment
- sentiment_score
- embedding
- theme_id
- confidence

This is preferred over assigning one sentiment to the entire review.

---

## 6. Processing pipeline

```python
def process_dataset(dataset_id):
    reviews = ingest_dataset(dataset_id)
    reviews = clean_reviews(reviews)
    reviews = redact_pii(reviews)
    reviews = detect_duplicates(reviews)

    units = create_feedback_units(reviews)
    units = run_sentiment(units)
    units = generate_embeddings(units)

    themes = discover_themes(units)
    themes = label_themes(themes)
    themes = calculate_temporal_metrics(themes)
    themes = detect_emerging_issues(themes)
    themes = calculate_impact_scores(themes)

    incidents = generate_incidents(themes)
    evidence = collect_evidence(incidents)
    incidents = generate_likely_driver_hypotheses(
        incidents, evidence
    )

    save_results()
    return results
```

---

## 7. Issue discovery

Use embeddings → UMAP → HDBSCAN/BERTopic-style clustering.

Clusters are candidate themes, not final truth.

Gemini may label a cluster only after representative examples and computed cluster statistics are supplied.

Example:

```json
{
  "theme_name": "Payment Failure",
  "category": "Payments",
  "description": "Customers report failed or incomplete payment transactions.",
  "severity": "high"
}
```

The LLM must not receive authority to invent quantitative metrics.

---

## 8. Temporal intelligence

For each theme calculate:
- baseline volume
- current volume
- growth %
- rolling average
- z-score
- change point
- rating change

Preferred initial detector:
- rolling baseline + z-score

If enough history exists:
- 28-day rolling baseline

For short demo datasets:
- 7-day baseline

---

## 9. Emerging issue detector

An issue becomes emerging when:

```text
new semantic cluster
+
low similarity to existing themes
+
increasing frequency
```

Output:

```text
NEW ISSUE DETECTED
Theme
Mentions
Growth
Confidence
Representative evidence
```

---

## 10. Feedback integrity

Never claim that a review is definitively fake.

Call the output:

**Feedback Integrity Risk** or **Anomalous Feedback Pattern**.

Signals:
- semantic near-duplicates
- review bursts
- repeated wording
- unusual timing
- rating/text contradiction
- repeated templates

Flag, do not silently delete.

---

## 11. Severity

Initial severity taxonomy:

### CRITICAL
- financial loss
- security/privacy
- data loss
- account inaccessible
- duplicate charge
- payment failure
- major outage

### HIGH
- crash
- feature unusable
- login failure
- major performance degradation

### MEDIUM
- slow performance
- UI/UX functional issues
- incorrect results
- minor functional bugs

### LOW
- cosmetic issues
- preferences
- feature requests

Severity can be overridden by a human.

---

## 12. Impact score

Normalize components to 0–100.

```text
Impact =
0.25 × Volume
+ 0.20 × Growth
+ 0.25 × Severity
+ 0.10 × Negative Sentiment
+ 0.10 × Reach
+ 0.10 × Confidence
```

Final range: 0–100.

The score ranks incidents; it is not presented as an objective business truth.

---

## 13. Likely-driver analysis

Never claim causal certainty from review data alone.

Use:

**Likely driver**

not:

**Confirmed root cause**

Signals:
- temporal alignment with release
- platform concentration
- device concentration
- version concentration
- geographic concentration
- sudden change

Example:

```text
Payment complaints +327%
Android = 87%
v4.8.1 = 79%
v4.8.1 released immediately before spike

Likely driver:
Android v4.8.1

Confidence:
88%
```

---

## 14. Evidence-first AI

Every generated conclusion must map to:

```text
claim
evidence
metric
confidence
```

Example:

```text
Claim:
Payment failures are the primary emerging problem.

Evidence:
487 supporting reviews.

Metric:
+327% growth.

Affected segment:
Android / v4.8.1.

Confidence:
94%.
```

---

## 15. Database schema

### datasets
- id
- name
- source
- file_name
- total_reviews
- created_at
- status

### reviews
- id
- dataset_id
- external_review_id
- raw_text
- clean_text
- rating
- review_date
- app_version
- platform
- device
- country
- language
- source
- is_duplicate
- duplicate_group_id
- integrity_risk
- rating_text_conflict
- created_at

### feedback_units
- id
- review_id
- text
- start_offset
- end_offset
- sentiment
- sentiment_score
- embedding vector(384)
- theme_id
- confidence
- created_at

### themes
- id
- dataset_id
- name
- category
- description
- cluster_id
- volume
- growth_percent
- avg_sentiment
- negative_percent
- severity
- impact_score
- confidence
- is_emerging
- created_at
- updated_at

### incidents
- id
- dataset_id
- theme_id
- title
- summary
- severity
- impact_score
- first_detected_at
- last_detected_at
- growth_percent
- likely_driver
- root_cause_confidence
- affected_platforms
- affected_versions
- affected_devices
- recommended_owner
- recommended_priority
- status
- created_at

### evidence
- id
- incident_id
- review_id
- feedback_unit_id
- evidence_type
- evidence_text
- relevance_score

### human_feedback
- id
- theme_id
- feedback_unit_id
- old_label
- new_label
- user_action
- created_at

---

## 16. API

### Dataset
- POST `/api/datasets/upload`
- GET `/api/datasets`
- GET `/api/datasets/{id}`
- DELETE `/api/datasets/{id}`

### Processing
- POST `/api/datasets/{id}/process`
- GET `/api/datasets/{id}/process-status`

### Dashboard
- GET `/api/dashboard/{dataset_id}`

### Themes
- GET `/api/themes/{dataset_id}`
- GET `/api/themes/{dataset_id}/{theme_id}`

### Incidents
- GET `/api/incidents/{dataset_id}`
- GET `/api/incidents/{dataset_id}/{incident_id}`
- POST `/api/incidents/{incident_id}/generate-action`

### Reviews
- GET `/api/reviews/{dataset_id}`
- GET `/api/reviews/{dataset_id}/{review_id}`

### Evidence
- GET `/api/incidents/{incident_id}/evidence`

### Investigator
- POST `/api/chat`

---

## 17. Frontend screens

### Executive Overview
Show:
- total reviews
- average rating
- negative %
- critical incidents
- emerging issues
- What Changed?
- top issues by impact

### Incident Radar
Show:
- incident
- impact
- severity
- growth
- likely driver
- confidence

### Issue Explorer
Filters:
- date
- platform
- version
- device
- country
- rating
- severity

### Incident Detail
Show:
- impact
- severity
- growth
- mentions
- rating impact
- first detected
- likely driver
- affected segments
- evidence
- recommended action

### Feedback Integrity
Show:
- suspicious bursts
- duplicate groups
- rating/text conflicts
- flagged %

### AI Investigator
Questions:
- Why did ratings fall?
- What changed after the latest release?
- Which issue affects Android users most?
- Show evidence for the top incident.
- What should engineering fix first?

---

## 18. Project structure

```text
signallens/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── prompts/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── raw/
│   ├── processed/
│   └── demo/
├── ml/
│   ├── notebooks/
│   ├── evaluation/
│   └── models/
├── docker-compose.yml
├── .env.example
├── ARCHITECTURE.md
├── VIBE_CODING_RULES.md
└── BUILD_PLAN.md
```

---

## 19. Definition of Done

A feature is not complete until:
1. backend endpoint works
2. database schema is updated if required
3. frontend consumes the real API
4. loading/error/empty states exist
5. representative data is displayed
6. tests exist for critical logic
7. no secrets are committed
8. README/architecture remains accurate

---

## 20. Golden principle

```text
FACTS
  ↓
ALGORITHMS
  ↓
EVIDENCE
  ↓
LLM EXPLANATION
```

Never:

```text
REVIEWS
  ↓
LLM
  ↓
UNVERIFIED ANSWER
```
