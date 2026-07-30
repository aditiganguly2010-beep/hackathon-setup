# Hackathon Project Blueprint

## 1. Project Description and Scope
- **Vision:** [Insert High-Level Vision]
- **In-Scope:** [List core functionalities]
- **Out-of-Scope:** Explicitly define what will *not* be built to prevent scope creep.
- **Non-Functional Requirements (NFRs):** Define acceptable latency for LLM inference (e.g., < 2s for first token), concurrent user handling, and failure tolerances.
- **Security:** Strict enforcement of zero PII (Personally Identifiable Information) in raw external LLM API payloads and local logs.

## 2. Project Constraints
- Setup and Use **LangTrace** and **Langfuse** for LLM traceability and cost monitoring.
- Implement structured JSON logging for all core actions to allow traceability across services.

## 3. Data Entities and Database
- **Entities:** First, identify the core domain entities necessary for the application.
- **Database:** Use **PostgreSQL** as the primary structured data store.
- **ORM & Migrations:** Use an ORM (e.g., SQLAlchemy) for data access and a migration tool (e.g., Alembic) for schema versioning. Avoid manual DDL scripts.
- **Connection Pooling:** Implement connection pooling (via SQLAlchemy or PgBouncer) to prevent connection exhaustion.
- **Auditability:** Mandate `created_at`, `updated_at`, and `created_by` audit fields on all core tables.
- Create synthetic data for demonstrating the use cases

## 4. Architecture and System Design
- **Design Principles:** Apply SOLID principles and Dependency Inversion.
- **API Contracts:** Adopt an API-first approach using OpenAPI/Swagger. Agree on JSON schemas before backend/frontend implementation begins.
- **Resilience & Rate Limiting:** Add rate limiting, particularly for outbound LLM calls.
- **Caching:** Implement an in-memory cache (e.g. local memory) for repeated LLM queries to reduce latency and cost.
- **Asynchronous Processing:** Offload heavy AI generation tasks to background workers (e.g., FastAPI BackgroundTasks, Celery) to avoid blocking main HTTP threads.
- **Error Handling:** Enforce a unified global exception handling structure across the API so the frontend predictably parses failures.
- **Architecture Diagram:** Generate and include a system architecture diagram in the `README.md`.

## 5. Backend
- **Stack:** Python 3.x, FastAPI.
- **Hosting/Execution:** Use **Gunicorn with Uvicorn workers (ASGI)** for production-grade async request handling.
- **Dependency Management:** Use `requirements.txt` for deterministic builds and dependency locking.
- **Health Checks:** Expose a `/health` endpoint validating DB connectivity and LLM API status.

## 6. Frontend
- **Stack:** ReactJS, Tailwind CSS, TypeScript, Vite.
- **State & Data Fetching:** Use a UI state management framework alongside a robust data-fetching library (e.g., React Query, SWR) to handle API caching, loading states, and retries.


## 7. AI, LLM and Agent Setup
- **Agent Framework:** Use **Google ADK** for Agent setup, configuration, and orchestration of complex workflows.
- **LLM Selection & Fallbacks:** Use appropriate models for specific tasks (e.g., audio-optimized for voice). Implement a routing/fallback strategy if the primary model fails or rate-limits.
- **Structured Outputs:** Mandate strict JSON schema validation for all LLM responses to ensure predictable backend parsing.
- **Streaming:** Utilize Server-Sent Events (SSE) or WebSockets to stream LLM responses to the frontend for improved UX.
- **Prompt Management:** Store prompts externally (e.g., configuration files or database), separating them from execution logic. Add Guardrails to prevent ambiguous inferences.
- **RAG:** Use Retrieval-Augmented Generation only if strictly necessary; try to avoid over-complicating if zero-shot or few-shot prompting suffices.
- **Extensions:** Use Hooks and MCP if necessary. Document the architectural justification in `README.md`.
- Consider the input Rulebook for LLM if provided




## Monitoring and Observability and Setup
- **Metrics & Dashboards:** Track critical business metrics and per-call LLM costs. Expose these in an admin dashboard.
- **Database Bootstrap:** Create a script for bootstrapping the database - DB, Tables, Schema creation. Also add a parameter to the script to reset the database for testing.
- **Configuration:** Use environment variables (`.env` files) for all credentials, endpoints, and environment configurations.
- **Logging & Metrics:** Add logging and metrics emission. For the purpose of the hackathon logs should be written into a local file.
- **Execution Commands:** Create a `.execution` file to store the commands for running individual stack components.
- **Bootstrap Script:** Create a parameterized script file to initialize/bootstrap the Database and start the frontend and backend services while writing logs to a local file.


