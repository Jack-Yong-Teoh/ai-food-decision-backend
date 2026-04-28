# fastapi-backend-base

# Run Fastapi Server

```
uv run uvicorn app.main:app --reload
```

## Development Setup

1. Create `.env` file by cloning from env.dist.

2. Fill in the environment variable in `.env`.

3. Migrate database by the migrate command in `Database Migration` section.

# Database Migration (Alembic)

```bash
# Make migration file
alembic revision --autogenerate -m "<action message>"

# Migrate to DB until latest migration
alembic upgrade head

# Rollback DB until previous migration
alembic downgrade head-1
```

# Table Partitioning Setup

- refer to [Table Partioning Guide](app/models/databases/orm/README.md)

## Squash Revisions per Version Release

1. Move all revisions that wanted to be squashed to archived folder

2. `alembic revision --autogenerate -m "<version num> YYYYMMDD"`

3. Update `version_num` in DB `alembic_version` table to new revision ID (ex.9c70c02b7404)

## Lint Code & Unit Test With Local Environment

Developers have to run the following commands and fix all the conflicts before submitting PR for review

```bash
# Format code
black .

# Lint code
pylint app tests

# Test cases
pytest -v
```

## Run the script

in terminal run the following command

```bash
# If script located in /scripts
python runner.py <yourscript>.py

or

python runner.py <file path>
```

## Start Celery

```bash
# Start worker
celery -A app.celery worker -c 4 -l DEBUG -n rsk-worker@%h -Q rsk.internal

# Start beat
celery -A app.celery beat -l INFO
```

# fastapi-backend-base# fastapi-backend-base
