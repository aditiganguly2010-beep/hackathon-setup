## System Architecture Overview

The **AI-Driven Legacy System Health Monitor** utilizes a decoupled, event-driven architecture designed to process fragmented legacy telemetry, normalize data streams, detect anomalies, and leverage Generative AI for operational decision support.

```
+-----------------------------------------------------------------------------------+
|                               DATA INGESTION & ETL                                |
|  +--------------------+    +----------------------+    +-----------------------+  |
|  | Legacy Text Logs   |    | JSON Logs / Metrics  |    | Incident Records      |  |
|  +---------+----------+    +----------+-----------+    +-----------+-----------+  |
+------------|--------------------------|----------------------------|--------------+
             |                          |                            |
             +------------------+-------+-------+--------------------+
                                |
                                v
+-----------------------------------------------------------------------------------+
|                            ETL & DATA PROCESSING LAYER                            |
|  +-----------------------------------------------------------------------------+  |
|  |  Parser & Normalizer (FastAPI / Celery Background Workers)                   |  |
|  |  - Parsing unstructured text logs into JSON                                 |  |
|  |  - Anonymization / PII scrubbing                                            |  |
|  |  - Noise filtering & Metric Aggregation                                     |  |
|  +-------------------------------------+---------------------------------------+  |
+----------------------------------------|------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            STORAGE & AI AGENT CORE                                |
|  +---------------------------+            +------------------------------------+  |
|  | PostgreSQL Database       |            | Google ADK Agent Core              |  |
|  | - SystemLogs              |            | - Anomaly Summarizer               |  |
|  | - PerformanceMetrics      |<---------->| - Prioritization Engine            |  |
|  | - Anomalies & HealthScore |            | - Structured JSON Guardrails       |  |
|  +---------------------------+            +-----------------+------------------+  |
|                                                             |                     |
|                                                             v                     |
|                                           +------------------------------------+  |
|                                           | Observability & Tracing            |  |
|                                           | - LangTrace / Langfuse             |  |
|                                           +------------------------------------+  |
+-----------------------------------------------------|-----------------------------+
                                                      |
                                                      v
+-----------------------------------------------------------------------------------+
|                            API & FRONTEND DASHBOARD                               |
|  +-----------------------------------------------------------------------------+  |
|  | FastAPI REST API / SSE (Server-Sent Events) Streaming                        |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  | ReactJS + TypeScript + Tailwind CSS Frontend                                |  |
|  | - Global Command Center  | Diagnostics  | Maintenance  | KPI Realization   |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+

```

---

## Detailed System Design & Core Data Flow

### 1. Data Ingestion & ETL Layer

* **Multi-Source Ingestion:** Receives raw legacy logs (unstructured text or JSON), time-series performance metrics (CPU, Memory, Disk I/O), and historical incident reports.
* **Preprocessing Pipeline:** Ingested streams pass through a lightweight Python ETL worker that:
* Scraps or masks PII/sensitive system parameters.
* Parses raw text logs into standardized JSON models.
* Filters out routine operational noise to focus on warnings, exceptions, and metric outliers.
* Tags time-series telemetry with standard correlation IDs.



### 2. Primary Persistence Layer

* **PostgreSQL Store:** Houses all normalized logs, time-series metrics, anomaly flags, generated health scores, and maintenance action items.
* **Data Access & Schema Versioning:** Managed using **SQLAlchemy ORM** with **Alembic** for automated migration tracking. Connection pooling is enforced using PgBouncer/SQLAlchemy pooling.
* **Audit Enforcement:** Every primary table includes mandatory audit fields (`created_at`, `updated_at`, `created_by`).

### 3. AI & Orchestration Layer

* **Agent Framework:** Built using **Google ADK** for configuring agent logic, task execution, and system state evaluation.
* **Health Scoring & Anomaly Detection:** Combines statistical metric analysis with LLM inference to compute system-wide health scores (0–100 scale).
* **Natural Language Summarization:** Generates actionable, plain-English summaries of system status and anomaly root causes.
* **Structured Output Enforcement:** Pydantic schemas enforce strict JSON responses from LLMs to prevent downstream parsing failures.
* **Fallback Strategy:** Implements automated fallback routing if the primary LLM endpoint encounters rate limits or errors.

### 4. LLM Observability & Traceability

* **Traceability Integration:** **LangTrace** and **Langfuse** track prompt executions, token usage, latency distribution, and step-by-step agent reasoning.
* **Structured Local Logging:** Application logs write to local JSON log files tracking request execution paths, DB transactions, and API calls.

### 5. API & Frontend Layer

* **Async FastAPI Server:** Exposes RESTful endpoints for telemetry queries, CRUD operations on maintenance tasks, and KPI metrics.
* **Real-time Streaming:** Uses Server-Sent Events (SSE) to stream live GenAI summaries and real-time health score updates directly to the browser UI.
* **Frontend SPA:** Single Page Application rendering four distinct operational views: Command Center, Diagnostics, Maintenance Center, and KPI Realization.

---

## Backend Systems

* **API Application Gateway (`FastAPI + Gunicorn/Uvicorn`):** Manages HTTP request processing, SSE streaming, authentication, and request validation.
* **ETL Background Worker Engine:** Async processing service executing log parsing, noise reduction, and metric aggregation prior to storage.
* **AI Agent Controller (`Google ADK`):** Manages prompt context, guardrails, fallback routes, and structured output parsing.
* **Database Management System (`PostgreSQL`):** Relational store for structured logs, time-series metrics, anomaly logs, and system audit trails.
* **LLM Telemetry Collector (`Langfuse / LangTrace`):** Intercepts outbound and inbound AI calls to record token consumption, cost metrics, and execution latency.

---

## Frontend System

* **Framework & Build:** **ReactJS** with **TypeScript** initialized using **Vite** for rapid bundling and hot module replacement.
* **Styling & Theme:** **Tailwind CSS** styled with a modern dark-mode palette optimized for SRE/Observability environments.
* **Data Fetching & State Management:** **React Query (TanStack Query)** handling client-side caching, optimistic UI updates, background polling, and automated retries.
* **Visualizations & Telemetry Charts:** **Recharts** / **Chart.js** rendering multi-metric time-series graphs, system health radial gauges, and KPI progression charts.

---

## Technology Stack Summary

| Layer | Technology | Purpose / Role |
| --- | --- | --- |
| **Frontend Framework** | ReactJS + TypeScript | Component-driven, type-safe user interface |
| **Frontend Build Tool** | Vite | Lightning-fast development server & production bundler |
| **UI Styling** | Tailwind CSS | Dark-mode design system tailored for observability dashboards |
| **State & Data Fetching** | React Query | API state caching, polling, and data synchronization |
| **Data Visualization** | Recharts / Chart.js | Interactive time-series charts, progress gauges, and KPI plots |
| **Backend Framework** | Python 3.x + FastAPI | High-performance asynchronous REST API server |
| **ASGI / Web Server** | Gunicorn with Uvicorn workers | Production-grade async request execution |
| **AI Agent Framework** | Google ADK | Orchestrating AI agents, prompt flows, and system analysis |
| **LLM Tracing & Costs** | LangTrace / Langfuse | Monitoring token usage, latency, and AI execution trees |
| **Primary Database** | PostgreSQL | Relational storage for logs, metrics, anomalies, and tasks |
| **ORM & Migrations** | SQLAlchemy + Alembic | Object-relational mapping and schema version management |
| **Data Preprocessing** | Python Pandas / Pydantic | Log parsing, data normalization, and PII anonymization |