# SignalLens — Vibe Coding Rules

This file is mandatory for every human developer and every AI coding agent working on SignalLens.

## 1. Mission

Build one coherent customer-incident intelligence platform.

The product must answer:

> What changed, how serious is it, who is affected, what evidence proves it, and what should we do?

Do not turn the repository into a collection of unrelated AI demos.

---

## 2. Architecture is a contract

Before changing architecture:
1. Read `ARCHITECTURE.md`.
2. Check whether the proposed change already fits the architecture.
3. Prefer the existing stack.
4. Do not introduce a new framework/library/database just because it is convenient.

### Prohibited without explicit approval

- MongoDB
- Qdrant
- Pinecone
- Chroma
- separate Node/Express backend
- arbitrary LLM frameworks
- microservices
- custom transformer training
- blockchain
- Kafka
- Kubernetes
- unnecessary cloud infrastructure

---

## 3. AI coding agents must work incrementally

Never generate the whole application in one shot.

Implement in this order:

1. repository skeleton
2. Docker + PostgreSQL
3. database models + migrations
4. ingestion
5. processing pipeline
6. APIs
7. frontend shell
8. dashboard
9. incident detail
10. evidence
11. integrity
12. investigator
13. polish

After each milestone:
- run tests
- run the application
- inspect the API
- inspect the UI
- fix errors before continuing

---

## 4. Never invent APIs

Before using a library:
- inspect its installed version
- use its current documented API
- do not hallucinate methods or parameters

If uncertain, check official documentation.

---

## 5. Never invent data

The LLM must not invent:
- review counts
- percentages
- dates
- ratings
- growth
- severity metrics
- confidence values

All quantitative values come from Python/PostgreSQL.

---

## 6. LLM output rules

Every important LLM operation must use structured output.

Preferred pattern:

```text
input facts
+
explicit task
+
JSON schema
→
validated Pydantic object
```

Never parse fragile natural-language output with string splitting.

If LLM output fails validation:
- retry once with the validation error
- otherwise mark the operation as failed
- never silently fabricate a fallback

---

## 7. Evidence requirement

Every AI-generated conclusion must be traceable.

Required:

```text
claim
evidence IDs
metrics
confidence
```

If evidence is insufficient:

> Insufficient evidence.

Do not hallucinate.

---

## 8. Root-cause language

Never say:

> confirmed root cause

unless ground truth exists.

Use:

> likely driver

or:

> likely contributing factor

---

## 9. Feedback integrity language

Never say:

> fake review

unless a verified external label exists.

Use:

> anomalous feedback pattern

or:

> feedback integrity risk

---

## 10. Database rules

Use SQLAlchemy models and Alembic migrations.

Never manually modify production schema without a migration.

Use PostgreSQL + pgvector.

Embedding dimension is 384 for `all-MiniLM-L6-v2`.

Use cosine similarity.

---

## 11. Backend rules

FastAPI route handlers should be thin.

Bad:

```text
route → 400 lines of ML logic
```

Good:

```text
route
  ↓
service
  ↓
repository/database
```

Business logic belongs in services.

---

## 12. Frontend rules

Do not hardcode analytics in React components.

Bad:

```text
const complaints = 487;
```

Good:

```text
GET /api/incidents
```

Use typed API responses.

Every screen needs:
- loading state
- empty state
- error state
- success state

---

## 13. UI rules

The UI should communicate decisions, not just data.

Prefer:

> Payment Failure — Impact 94 — +327%

over:

> Theme 17 — 487 reviews

Prefer:

> Likely driver: Android v4.8.1

over:

> Cluster 3

Prefer:

> What Changed?

over:

> Analytics

---

## 14. Demo-first rule

Every major feature must have a visible UI representation.

ML code that cannot be demonstrated is lower priority than a working end-to-end feature.

---

## 15. No premature optimization

Do not optimize:
- distributed processing
- GPU inference
- vector sharding
- caching layers
- Kubernetes

until the end-to-end demo works.

10,000 reviews is small enough for a single-machine hackathon architecture.

---

## 16. Secrets

Never commit:
- `.env`
- API keys
- database passwords
- private credentials

Maintain `.env.example`.

---

## 17. Git rules

Branches:

```text
main
develop
feature/<name>
fix/<name>
```

Commit messages:

```text
feat: add review ingestion
feat: add sentiment pipeline
feat: add incident API
fix: handle empty theme clusters
```

Never commit broken code to `main`.

---

## 18. Testing priorities

Highest priority:
1. impact score
2. trend detection
3. severity
4. duplicate detection
5. evidence retrieval
6. API contracts
7. data validation

ML evaluation must include:
- precision
- recall
- macro F1
- confusion matrix

Do not use accuracy alone.

---

## 19. Human-in-the-loop

Human corrections must be stored.

Actions:

```text
correct
merge
split
ignore
approve
reject
```

Do not make irreversible automatic changes to feedback.

---

## 20. Error handling

Every external dependency can fail:
- Gemini
- model download
- database
- uploaded dataset
- malformed CSV

Handle failures explicitly.

Never show a blank dashboard because one model failed.

---

## 21. Performance

For the hackathon:
- process datasets asynchronously if necessary
- batch embeddings
- cache model loading
- bulk insert into PostgreSQL
- avoid one database query per review

Do not build distributed infrastructure.

---

## 22. AI agent workflow

Every coding agent should follow:

```text
READ
 ↓
UNDERSTAND
 ↓
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
RUN
 ↓
INSPECT
 ↓
FIX
```

Before editing:
- inspect relevant files
- understand existing abstractions
- reuse existing utilities

Do not overwrite working code blindly.

---

## 23. When an AI agent proposes a new technology

It must answer:

1. What problem does it solve?
2. Why can't our existing stack solve it?
3. What new complexity does it introduce?
4. Does it affect deployment?
5. Does it affect the demo timeline?

If the answer is weak, reject the technology.

---

## 24. Product priority

When forced to choose:

```text
Correctness
>
Evidence
>
End-to-end functionality
>
UX
>
Performance
>
Fancy ML
```

A boring feature that works end-to-end beats an impressive model nobody can demonstrate.

---

## 25. Golden rule

Never build:

```text
AI that generates impressive answers.
```

Build:

```text
SYSTEM THAT GENERATES DEFENSIBLE ANSWERS FROM EVIDENCE.
```
