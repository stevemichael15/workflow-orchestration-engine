# Workflow Orchestration Engine

This project implements a **template-driven workflow orchestration engine** designed to simulate government-style decision systems.
The engine supports **multi-step workflows**, **parallel execution**, **immutable audit logs**, and **appeal processing**, all exposed through a FastAPI service.

The problem domain (government benefits) is fictional. The focus of this project is **systems design, correctness, and auditability**, not domain complexity.

---

## Key Features

- Workflow definitions using JSON templates (no hardcoded logic)
- Sequential and parallel workflow execution
- Immutable, append-only audit trail for every step
- Appeal processing with strict immutability guarantees
- REST APIs built using FastAPI
- PostgreSQL-backed persistence with JSONB support

---

## High-Level Architecture

```
Client
↓
FastAPI (API Layer)
↓
Workflow Executor (Engine)
↓
Task Registry → Task Functions
↓
PostgreSQL (workflow_instances, audit_trail, appeals)
```

### Design Principles

- **Template-driven execution**: Adding a new workflow requires only a new JSON template.
- **Separation of concerns**:
  - Engine coordinates execution
  - Tasks perform business logic
  - API layer handles requests and responses
- **Fail-fast behavior**: Any step failure halts the workflow and is logged.
- **Audit-first design**: Every step is logged immutably for traceability.

---

## Workflow Templates Implemented

### 1. Eligibility Check Workflow

Sequential workflow that:
1. Fetches citizen data (mock)
2. Fetches scheme rules
3. Evaluates eligibility rules
4. Makes a decision:
   - `ELIGIBLE`
   - `NOT_ELIGIBLE`
   - `NEEDS_REVIEW` (if income is within 10% of limit)
5. Logs final outcome

---

### 2. Parallel Impact Analysis Workflow

Used when policy rules change.

Steps:
1. Load 500 mock beneficiaries
2. Re-evaluate eligibility **in parallel**
3. Count beneficiaries by eligibility status:
   - `ELIGIBLE`
   - `NOT_ELIGIBLE`
   - `NEEDS_REVIEW` (if income is within 10% of limit)
4. Generate a summary report with totals

Performance requirement:
- 500 evaluations must complete under 30 seconds on a standard laptop.

---

### 3. Appeal Processing

Handles re-evaluation requests after rejection by re-running the eligibility check workflow with new data.

The appeal processing uses a dedicated template (`appeal_processing.json`) that mirrors the eligibility check steps:

1. Fetches citizen data (with corrected evidence)
2. Fetches scheme rules
3. Evaluates eligibility rules
4. Makes a decision:
   - `ELIGIBLE`
   - `NOT_ELIGIBLE`
   - `NEEDS_REVIEW`

Key guarantees:
- Original workflow instance is **never modified**
- A new workflow instance is created using the appeal processing template
- Both decisions are linked via the `appeals` table

---

## Database Schema

### Tables

- `workflow_instances` — Tracks each workflow execution
- `audit_trail` — Append-only log of every workflow step
- `appeals` — Links original decisions to appeal re-evaluations

### Immutability Enforcement

The `audit_trail` table is **append-only**:

```sql
REVOKE UPDATE, DELETE ON audit_trail FROM PUBLIC;
```

This ensures audit records cannot be modified or deleted.

---

## API Endpoints

| Method | Endpoint                          | Description                     |
|--------|-----------------------------------|---------------------------------|
| POST   | `/workflows/execute`              | Execute a workflow template     |
| GET    | `/workflows/{instance_id}`        | Get workflow status and outputs |
| GET    | `/workflows/{instance_id}/audit`  | Retrieve full audit trail       |
| POST   | `/workflows/appeal`               | Submit an appeal                |
| GET    | `/workflows/report/{instance_id}` | Fetch impact analysis report    |

Interactive API docs available at: http://localhost:8000/docs

---

## Project Structure

```
workflow-engine/
├── main.py                    # FastAPI entry point
├── engine/                    # Core workflow engine
│   ├── executor.py           # Runs workflows step by step
│   ├── registry.py           # Task type → function mapping
│   └── parallel.py           # Parallel execution logic
├── tasks/                     # Business logic implementations
│   ├── mock_data.py          # Mock citizens & schemes data
│   ├── eligibility.py        # Rule evaluation logic
│   ├── decision.py           # Final decision logic
│   └── report_builder.py     # Impact analysis reports
├── templates/                 # JSON workflow definitions
│   ├── eligibility_check.json
│   └── impact_analysis.json
├── db/                        # Database layer
│   ├── connection.py         # DB connection management
│   └── queries.py            # SQL query helpers
├── api/                       # REST API layer
│   └── routes.py              # All API endpoints
├── schema.sql                 # Database schema
├── requirements.txt           # Python dependencies
├── answer.md                  # Design documentation
└── README.md                  # Project documentation
```

---

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL
- pip
- Docker (optional, for containerized setup)

### Steps

#### Local Development Setup

```bash
git clone https://github.com/stevemichael15/workflow-orchestration-engine.git
cd workflow-engine
pip install -r requirements.txt
psql -f schema.sql
uvicorn main:app --reload
```

#### Docker Setup

For a containerized environment:

```bash
git clone https://github.com/stevemichael15/workflow-orchestration-engine.git
cd workflow-engine
docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- FastAPI application on port 8000

The database schema is automatically initialized via the init script in `schema.sql`.

Then open: http://localhost:8000/docs

---

## Design Decisions & Trade-offs

- **ThreadPoolExecutor** used for parallel execution instead of Celery for simplicity and reliability.
- **JSON templates** chosen for flexibility and ease of extension.
- **PostgreSQL JSONB** used to store full input/output snapshots for auditing.
- Workflow execution halts on first failure to preserve correctness over partial success.

---

## Known Limitations

- No retry mechanism for failed steps (by design for clarity)
- No authentication/authorization layer
- Parallel execution limited to single-machine concurrency

---

## Design Reflections

For detailed answers to design questions and architectural decisions, see [answer.md](answer.md). This document covers topics such as:

- Handling partial failures in parallel execution
- Managing long-running external API calls
- Audit trail tamper-proofing
- JSON template limitations at scale
- Scalability considerations for large datasets
