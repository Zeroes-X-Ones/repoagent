import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from analytics.database import AnalyticsDatabase


class AnalyticsRepository:
    """Repository interface for analytics event persistence and reads."""

    def __init__(self, database: Optional[AnalyticsDatabase] = None):
        self.database = database or AnalyticsDatabase()

    def insert_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        with self.database._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analytics_events (
                    request_id,
                    timestamp,
                    repository,
                    user_prompt,
                    selected_files,
                    total_files,
                    original_token_count,
                    compressed_token_count,
                    tokens_saved,
                    compression_ratio,
                    latency_ms,
                    estimated_cost,
                    estimated_cost_saved,
                    model,
                    provider,
                    quality_score,
                    execution_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["request_id"],
                    event["timestamp"],
                    event["repository"],
                    event["user_prompt"],
                    json.dumps(event.get("selected_files", [])),
                    event.get("total_files", 0),
                    event.get("original_token_count", 0),
                    event.get("compressed_token_count", 0),
                    event.get("tokens_saved", 0),
                    event.get("compression_ratio", 0.0),
                    event.get("latency_ms", 0.0),
                    event.get("estimated_cost", 0.0),
                    event.get("estimated_cost_saved", 0.0),
                    event.get("model", "unknown"),
                    event.get("provider", "unknown"),
                    event.get("quality_score", 0.0),
                    event.get("execution_status", "success"),
                ),
            )
        return event

    def list_requests(
        self,
        limit: int = 100,
        repository: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM analytics_events WHERE 1=1"
        params: List[Any] = []

        if repository:
            query += " AND repository = ?"
            params.append(repository)
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self.database._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [self._row_to_dict(row) for row in rows]

    def get_overview(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        rows = self.list_requests(limit=10000, start_date=start_date, end_date=end_date)
        if not rows:
            return {
                "total_requests": 0,
                "total_cost": 0.0,
                "total_cost_saved": 0.0,
                "average_compression": 0.0,
                "average_latency_ms": 0.0,
                "average_quality": 0.0,
                "success_rate": 0.0,
            }

        total_requests = len(rows)
        successful = sum(1 for row in rows if row.get("execution_status") == "success")
        total_cost = round(sum(float(row.get("estimated_cost", 0.0)) for row in rows), 6)
        total_cost_saved = round(sum(float(row.get("estimated_cost_saved", 0.0)) for row in rows), 6)
        avg_compression = round(
            sum(float(row.get("compression_ratio", 0.0)) for row in rows) / total_requests,
            3,
        )
        avg_latency = round(
            sum(float(row.get("latency_ms", 0.0)) for row in rows) / total_requests,
            3,
        )
        avg_quality = round(
            sum(float(row.get("quality_score", 0.0)) for row in rows) / total_requests,
            3,
        )
        success_rate = round((successful / total_requests) * 100 if total_requests else 0.0, 1)

        return {
            "total_requests": total_requests,
            "total_cost": total_cost,
            "total_cost_saved": total_cost_saved,
            "average_compression": avg_compression,
            "average_latency_ms": avg_latency,
            "average_quality": avg_quality,
            "success_rate": success_rate,
        }

    def get_usage_series(self, granularity: str = "day", start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = self.list_requests(limit=10000, start_date=start_date, end_date=end_date)
        if not rows:
            return []

        if granularity == "hour":
            key_format = "%Y-%m-%d %H:00"
        elif granularity == "month":
            key_format = "%Y-%m"
        else:
            key_format = "%Y-%m-%d"

        buckets: Dict[str, int] = {}
        for row in rows:
            timestamp = row.get("timestamp", "")
            if not timestamp:
                continue
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                try:
                    dt = datetime.fromisoformat(timestamp)
                except ValueError:
                    continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            bucket = dt.astimezone(timezone.utc).strftime(key_format)
            buckets[bucket] = buckets.get(bucket, 0) + 1

        return [{"period": key, "count": value} for key, value in sorted(buckets.items())]

    def get_repository_analytics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = self.list_requests(limit=10000, start_date=start_date, end_date=end_date)
        grouped: Dict[str, Dict[str, Any]] = {}

        for row in rows:
            repository = row.get("repository", "unknown")
            bucket = grouped.setdefault(
                repository,
                {
                    "repository": repository,
                    "requests": 0,
                    "total_cost": 0.0,
                    "total_cost_saved": 0.0,
                    "average_latency_ms": 0.0,
                    "average_quality": 0.0,
                    "average_compression": 0.0,
                },
            )
            bucket["requests"] += 1
            bucket["total_cost"] += float(row.get("estimated_cost", 0.0))
            bucket["total_cost_saved"] += float(row.get("estimated_cost_saved", 0.0))
            bucket["average_latency_ms"] += float(row.get("latency_ms", 0.0))
            bucket["average_quality"] += float(row.get("quality_score", 0.0))
            bucket["average_compression"] += float(row.get("compression_ratio", 0.0))

        for bucket in grouped.values():
            total = max(1, bucket["requests"])
            bucket["total_cost"] = round(bucket["total_cost"], 6)
            bucket["total_cost_saved"] = round(bucket["total_cost_saved"], 6)
            bucket["average_latency_ms"] = round(bucket["average_latency_ms"] / total, 3)
            bucket["average_quality"] = round(bucket["average_quality"] / total, 3)
            bucket["average_compression"] = round(bucket["average_compression"] / total, 3)

        return sorted(grouped.values(), key=lambda item: item["requests"], reverse=True)

    def get_top_repositories(self, limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        analytics = self.get_repository_analytics(start_date=start_date, end_date=end_date)
        return analytics[:limit]

    def get_averages(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        overview = self.get_overview(start_date=start_date, end_date=end_date)
        return {
            "average_compression": overview.get("average_compression", 0.0),
            "average_latency_ms": overview.get("average_latency_ms", 0.0),
            "average_cost_saved": overview.get("total_cost_saved", 0.0),
            "average_quality": overview.get("average_quality", 0.0),
        }

    @staticmethod
    def _row_to_dict(row: Any) -> Dict[str, Any]:
        data = dict(row)
        try:
            data["selected_files"] = json.loads(data.get("selected_files", "[]"))
        except (TypeError, ValueError):
            data["selected_files"] = []
        return data
