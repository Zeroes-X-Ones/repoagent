# Explainability and Benchmark Engine

## Overview

This module adds explainability reports for retrieval decisions and benchmark reports for comparing multiple execution pipelines.

## APIs

- POST /api/explainability/report
- POST /api/explainability/benchmark
- GET /api/explainability/benchmark/history
- GET /api/explainability/benchmark/compare

## Output shape

Explainability reports include kept and removed file entries with importance, confidence, reason, dependencies, related symbols, retrieval score, semantic similarity, and natural-language explanations.

Benchmark reports compare pipeline metrics such as tokens, latency, cost, quality, context size, and execution success.
