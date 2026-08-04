# Analytics Engine

## Overview

The analytics engine records agent requests and exposes summarised metrics for dashboards without changing the existing workflow.

## API endpoints

- GET /api/analytics/requests
- GET /api/analytics/overview
- GET /api/analytics/usage/today
- GET /api/analytics/usage/weekly
- GET /api/analytics/usage/monthly
- GET /api/analytics/repositories
- GET /api/analytics/top-repositories
- GET /api/analytics/averages

## Storage

Data is stored in SQLite by default via analytics.sqlite3 and is isolated behind the repository/service layer so a future database backend can be swapped in.
