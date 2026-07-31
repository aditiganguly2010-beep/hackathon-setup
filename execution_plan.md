Here is the updated blueprint for the project, incorporating the requirements analysis, architectural modifications for ETL, synthetic data generation, dashboard design, and future improvements based on the problem statement.

# Hackathon Project Blueprint: AI-Driven Legacy System Health Monitor

## 1. Project Description and Scope

* **Vision:** To provide maintenance teams with an interactive, AI-driven health monitor that aggregates fragmented legacy system data, highlights anomalies, and suggests maintenance priorities, thereby improving operational reliability and reducing service disruptions.


* **Functional Requirements (In-Scope):**
* **Data Integration:** Ingest legacy system logs (text/JSON), performance metrics, and historical incident records.


* **Data Preprocessing:** Parse, normalize, and filter noise from fragmented data streams.


* **AI Anomaly Detection:** Detect system degradation and anomalies using AI models.


* **Dashboard & Aggregation:** Provide an interactive web UI that aggregates data and highlights system health scores.


* **GenAI Summaries:** Synthesize disparate data into natural language summaries of system status.


* **Actionable Insights:** Generate prioritized maintenance actions.


* **Reporting:** Support exportable maintenance reports.




* **Out-of-Scope:** Automated remediation or execution of maintenance scripts; direct modification of legacy system configurations.
* **Expected Outcomes:** Improved operational reliability, reduced service disruptions, and actionable decision support for maintenance teams.


* **Key Performance Indicators (KPIs):**
* 85% anomaly detection accuracy.


* 30% reduction in issue identification time.




* **Non-Functional Requirements (NFRs):**
* **Privacy:** Secure sensitive system data and utilize anonymized or synthetic data where appropriate.


* **Performance:** Acceptable latency for LLM inference (e.g., < 2s for first token).




* **Security:** Strict enforcement of zero PII (Personally Identifiable Information) in raw external LLM API payloads and local logs.



## 2. Project Constraints

* Setup and Use **LangTrace** and **Langfuse** for LLM traceability and cost monitoring.


* Implement structured JSON logging for all core actions to allow traceability across services.



## 3. Data Entities and Database

* **Entities:** `SystemLogs`, `PerformanceMetrics`, `IncidentRecords`, `Anomalies`, `MaintenanceActions`, `HealthScores`.
* **Database:** Use **PostgreSQL** as the primary structured data store.


* **ORM & Migrations:** Use SQLAlchemy and Alembic for schema versioning. Avoid manual DDL scripts.


* **Connection Pooling:** Implement connection pooling (via SQLAlchemy or PgBouncer).


* **Auditability:** Mandate `created_at`, `updated_at`, and `created_by` audit fields on all core tables.



## 4. Architecture and System Design

* **Data Ingestion & ETL Pipeline (New Addition):** Because legacy data is fragmented and requires parsing, normalization, and noise filtering, a dedicated ETL service (e.g., using Python Pandas or a lightweight scheduler like Celery/APScheduler) will be plugged in. This layer will normalize text/JSON logs and write structured entities to PostgreSQL.


* **Design Principles:** Apply SOLID principles and Dependency Inversion.


* **API Contracts:** Adopt an API-first approach using OpenAPI/Swagger. Agree on JSON schemas before backend/frontend implementation begins.


* **Resilience & Rate Limiting:** Add rate limiting, particularly for outbound LLM calls.


* **Caching:** Implement an in-memory cache (e.g. local memory) for repeated LLM queries to reduce latency and cost.


* **Asynchronous Processing:** Offload heavy AI generation tasks to background workers (e.g., FastAPI BackgroundTasks, Celery) to avoid blocking main HTTP threads.


* **Error Handling:** Enforce a unified global exception handling structure across the API.



## 5. Backend

* **Stack:** Python 3.x, FastAPI.


* **Hosting/Execution:** Use **Gunicorn with Uvicorn workers (ASGI)** for production-grade async request handling.


* **Dependency Management:** Use `requirements.txt` for deterministic builds.


* **Health Checks:** Expose a `/health` endpoint validating DB connectivity and LLM API status.



## 6. Frontend

* **Stack:** ReactJS, Tailwind CSS, TypeScript, Vite.


* **State & Data Fetching:** Use a UI state management framework alongside a robust data-fetching library (e.g., React Query, SWR).



## 7. AI, LLM and Agent Setup

* **Agent Framework:** Use **Google ADK** for Agent setup and orchestration.


* **GenAI Role:** Synthesize preprocessed log/metric data into natural language summaries and prioritize maintenance actions.


* **Structured Outputs:** Mandate strict JSON schema validation for all LLM responses to ensure predictable backend parsing.


* **Streaming:** Utilize Server-Sent Events (SSE) or WebSockets to stream LLM responses to the frontend.


* **Prompt Management:** Store prompts externally. Add Guardrails to prevent ambiguous inferences.


* **RAG:** Use Retrieval-Augmented Generation only if strictly necessary.



## 8. Synthetic Data Generation (New Section)

To effectively test and demo the application without exposing real sensitive data, a synthetic data generation script will be implemented.

* **Scope:** Generate realistic legacy system logs (JSON and raw text formats), simulated CPU/Memory/Disk performance metrics, and historical incident records.
* **Patterns & Anomalies:** The script will simulate both "normal operation patterns" and "legacy system anomalies" (e.g., sudden spikes in error logs, sustained high memory usage).


* **Tools:** Use Python libraries like `Faker` to generate varied log formats, and inject statistical outliers into time-series metric generation to simulate incidents that the AI must detect.

## 9. Dashboard Layout and Observability (New Section)

The UI must be an interactive dashboard aggregating legacy data and facilitating decision support.

* **Global Header:** Displays the overall aggregated **System Health Score** (e.g., 0-100 gauge) and a button to "Export Maintenance Report".


* **Left Panel (Data & Metrics):** Real-time multi-source data visualization (charts for memory/CPU) and a normalized feed of recent critical logs.
* **Center Panel (Anomalies & AI Summaries):**
* A timeline or list highlighting **Detected Anomalies**.


* A dedicated section for the **GenAI Natural Language Summary** of the current system status.




* **Right Panel (Actionable Insights):** A checklist of **Prioritized Maintenance Actions** generated by the AI.


* **Bottom Panel (KPI Tracker):** Real-time tracking of hackathon problem KPIs:
* Current Anomaly Detection Accuracy (Target: 85%).


* Reduction in Issue Identification Time (Target: 30%).





## 10. Future Improvements (Out of Scope for Base Implementation)

*This section outlines enhancements to be explored only after core requirements are met.*

* **Predictive Maintenance:** Moving beyond anomaly *detection* to forecasting system degradation before it happens based on historical trends.
* **Auto-Remediation:** Integrating webhooks to automatically trigger safe, predefined restart or cleanup scripts on the legacy servers.
* **ITSM Integration:** Automatic ticket creation in tools like Jira or ServiceNow when critical anomalies are detected and prioritized.
* **Chatbot Interface:** Expanding the GenAI summary into a fully interactive chatbot where maintenance teams can query specific logs or ask for troubleshooting steps.

## 11. Monitoring, Observability, and Setup

* **Metrics & Dashboards:** Track critical business metrics and per-call LLM costs. Expose these in an admin dashboard.


* **Database Bootstrap:** Create a script for bootstrapping the database - DB, Tables, Schema creation.


* **Configuration:** Use environment variables (`.env` files) for all credentials.


* **Logging & Metrics:** Logs should be written into a local file for the hackathon.


* **Execution Commands:** Create a `.execution` file to store the commands.


* **Bootstrap Script:** Create a parameterized script file to initialize/bootstrap the Database and start services.