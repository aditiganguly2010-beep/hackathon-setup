# Legacy System Health Monitor - Backend

FastAPI backend for AI-driven legacy system health monitoring.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
python scripts/bootstrap_database.py
```

5. Run migrations:
```bash
alembic upgrade head
```

6. Generate synthetic data:
```bash
python scripts/generate_synthetic_data.py
```

7. Start server:
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core configuration and utilities
│   ├── db/               # Database session and models
│   ├── etl/              # ETL pipeline
│   ├── ai/               # AI/LLM services
│   ├── models/           # SQLAlchemy models
│   └── schemas/          # Pydantic schemas
├── alembic/              # Database migrations
├── scripts/              # Utility scripts
└── tests/                # Test files
```
