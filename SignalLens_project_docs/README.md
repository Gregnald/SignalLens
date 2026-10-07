# SignalLens

## Evidence-Backed Customer Incident Intelligence

SignalLens turns large volumes of customer feedback into actionable product incidents.

### Core question

> What changed, how serious is it, who is affected, what evidence proves it, and what should we do?

## Stack

- Next.js + TypeScript
- FastAPI + Python
- PostgreSQL + pgvector
- spaCy
- CardiffNLP RoBERTa sentiment
- Sentence Transformers `all-MiniLM-L6-v2`
- UMAP + HDBSCAN/BERTopic-style discovery
- Microsoft Presidio
- Gemini Flash
- Docker

## Run

Copy:

```bash
cp .env.example .env
```

Fill the required variables.

Then:

```bash
docker compose up --build
```

Backend:
`http://localhost:8000`

Frontend:
`http://localhost:3000`

## Architecture contract

Read `ARCHITECTURE.md` before making architectural changes.

## AI coding contract

Read `VIBE_CODING_RULES.md` before asking an AI coding agent to modify the project.

## Build sequence

Read `BUILD_PLAN.md`.

## Golden principle

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
