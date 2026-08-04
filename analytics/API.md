# Analytics API

## Request payload recorded per AI request

The analytics service records the following fields:

- request_id
- timestamp
- repository
- user prompt
- selected files
- total files
- original token count
- compressed token count
- tokens saved
- compression ratio
- latency
- estimated cost
- estimated cost saved
- model
- provider
- quality score
- execution status

## Endpoints

### GET /api/analytics/requests
Returns recent request records.

### GET /api/analytics/overview
Returns summary metrics for the current dataset.

### GET /api/analytics/usage/today
Returns hourly usage counts for today.

### GET /api/analytics/usage/weekly
Returns daily usage counts for the current week.

### GET /api/analytics/usage/monthly
Returns monthly usage counts for the current month.

### GET /api/analytics/repositories
Returns repository-level analytics.

### GET /api/analytics/top-repositories
Returns the most active repositories.

### GET /api/analytics/averages
Returns average compression, latency, cost saved, and quality metrics.
