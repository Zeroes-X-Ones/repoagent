# Explainability and Benchmark Architecture

```mermaid
flowchart TD
    A[API Controller] --> B[Explainability Service]
    B --> C[Structured Report JSON]

    D[Benchmark API] --> E[Benchmark Service]
    E --> F[Benchmark History JSON]
```

## Responsibilities

- Explainability Service converts retrieval decisions into structured, human-readable reports.
- Benchmark Service stores comparable metrics across execution pipelines and supports future model expansion.
- Controllers expose stable JSON endpoints without touching the UI.
