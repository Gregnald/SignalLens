# The pgvector/pgvector:pg16 image resolved to a broken/mismatched manifest on this
# registry mirror (exec format error on every binary in the image, even the shell).
# Building pgvector on top of the official postgres:16 image is more robust and uses
# the already-configured PGDG apt repo.
FROM postgres:16

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-16-pgvector \
    && rm -rf /var/lib/apt/lists/*
