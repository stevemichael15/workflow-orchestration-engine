# Reflection & Design Answers

This document answers the reflection questions provided in the assignment.
All responses are based strictly on the **current implementation** of the workflow engine.

---

## 1. Your parallel_execution step runs 500 workers. If 12 of them fail mid-run, what does your engine do?

### Current behavior (exact implementation)

The `parallel_execution` step uses a `ThreadPoolExecutor`. Each citizen evaluation is submitted as an independent future.

If **any of the futures raises an exception**:

1. The exception is raised when `future.result()` is accessed
2. The `parallel_execution` task raises an error
3. The workflow executor:
   - Marks the step as `failed`
   - Records the error and partial context in the audit trail
   - Immediately halts workflow execution
4. No report is generated
5. The workflow status is marked as `failed`

The engine does **not** attempt partial aggregation of successful results.

### Design rationale

Partial population results can be misleading in policy analysis.
The engine intentionally follows a **fail-fast** approach to preserve correctness and audit clarity.

### Possible evolution

A future version could support a configuration flag such as `tolerate_failures`
to allow partial success reporting, but this is not implemented by design.

---

## 2. A new template needs a step type that calls an external API that sometimes takes 30 seconds. How does your engine handle this?

### Current behavior

Workflow execution is synchronous **per workflow instance**.

- A long-running step blocks only that specific workflow execution
- Other workflows continue to run concurrently via FastAPI’s request handling
- The system does **not** block globally

This is acceptable within the current single-node scope.

### Future evolution

To support long-running external calls properly, the system would evolve to:

- Asynchronous execution or background jobs
- Workflow state persistence between steps
- Retry and timeout handling
- External task queues (e.g., Celery, SQS)

The current architecture does not prevent this evolution.

---

## 3. An auditor asks: “Prove to me that audit_trail row 45821 has not been tampered with.”

### Guarantees in the current system

- The `audit_trail` table is enforced as append-only:
  ```sql
  REVOKE UPDATE, DELETE ON audit_trail FROM PUBLIC;
  ```

---

## 4. Templates are defined as JSON. What are the top 3 limitations at scale?

### Limitation 1: Weak schema enforcement

JSON does not enforce strong typing or structure validation.
Errors are detected at runtime.

### Evolution

Introduce JSON Schema validation at template load time.

### Limitation 2: Lack of versioning

Templates do not currently support versioning, making historical replay harder.

### Evolution

Add template versioning and persist the version per workflow instance.

### Limitation 3: Limited expressiveness

JSON lacks support for:
- Conditional branching
- Loops
- Dynamic execution paths

### Evolution

Compile templates into an internal execution graph or introduce a lightweight DSL.

---

## 5. If the engine had to process 50,000 citizens instead of 500, what would break first?

### What breaks first

- ThreadPoolExecutor saturation due to excessive threading
- Increased memory usage holding large result sets
- Single-process CPU limitations (Python GIL)

### Migration plan

#### Batching
Process citizens in chunks (e.g., 1,000 at a time)

#### Streaming aggregation
Aggregate counts incrementally instead of storing all results

#### Distributed execution
Offload evaluations to worker queues

#### Horizontal scaling
Multiple worker processes or nodes

The current design is intentionally single-node, but architecturally extensible.
