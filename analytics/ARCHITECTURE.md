# Analytics Engine Architecture

```mermaid
flowchart TD
    A[Controller / API] --> B[Analytics Service]
    B --> C[Analytics Repository]
    C --> D[Database Adapter]
    D --> E[(SQLite)]

    F[AI Agent Workflow] --> B
```

## Responsibilities

- Controllers expose stable REST endpoints for dashboards.
- Analytics Service transforms request context into normalized event payloads.
- Repository abstracts persistence so the same service works with SQLite today and another database later.
- Database adapter owns schema and storage-specific logic.
