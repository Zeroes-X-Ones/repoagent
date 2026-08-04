import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from analytics.repository import AnalyticsRepository


class AnalyticsService:
    """Service layer for analytics event recording and aggregation."""

    def __init__(self, repository: Optional[AnalyticsRepository] = None):
        self.repository = repository or AnalyticsRepository()

    def record_request(self, *,
                       repository: str,
                       user_prompt: str,
                       selected_files: Optional[List[str]] = None,
                       total_files: Optional[int] = None,
                       model: str,
                       provider: str,
                       quality_score: Optional[float] = None,
                       execution_status: str = "success",
                       latency_ms: Optional[float] = None,
                       request_id: Optional[str] = None,
                       timestamp: Optional[str] = None,
                       original_token_count: Optional[int] = None,
                       compressed_token_count: Optional[int] = None,
                       estimated_cost: Optional[float] = None,
                       estimated_cost_saved: Optional[float] = None,
                       ) -> Dict[str, Any]:
        try:
            normalized_repository = repository or os.getenv("REPO_NAME", "unknown")
            normalized_prompt = user_prompt or ""
            selected = selected_files or []
            total = total_files if total_files is not None else max(1, len(selected))
            event_time = timestamp or datetime.now(timezone.utc).isoformat()
            request_uuid = request_id or str(uuid.uuid4())

            original_tokens = original_token_count if original_token_count is not None else self._estimate_tokens(normalized_prompt)
            compressed_tokens = compressed_token_count if compressed_token_count is not None else max(1, int(original_tokens * 0.8))
            tokens_saved = max(0, original_tokens - compressed_tokens)
            compression_ratio = round((original_tokens / max(1, compressed_tokens)) if compressed_tokens else 0.0, 3)
            latency = latency_ms if latency_ms is not None else 0.0
            quality = quality_score if quality_score is not None else (1.0 if execution_status == "success" else 0.0)
            cost = estimated_cost if estimated_cost is not None else self._estimate_cost(provider, model, original_tokens, compressed_tokens)
            cost_saved = estimated_cost_saved if estimated_cost_saved is not None else round(max(0.0, cost * (1 - (compressed_tokens / max(1, original_tokens)))), 6)

            event = {
                "request_id": request_uuid,
                "timestamp": event_time,
                "repository": normalized_repository,
                "user_prompt": normalized_prompt,
                "selected_files": selected,
                "total_files": total,
                "original_token_count": original_tokens,
                "compressed_token_count": compressed_tokens,
                "tokens_saved": tokens_saved,
                "compression_ratio": compression_ratio,
                "latency_ms": round(latency, 3),
                "estimated_cost": round(cost, 6),
                "estimated_cost_saved": round(cost_saved, 6),
                "model": model or "unknown",
                "provider": provider or "unknown",
                "quality_score": round(quality, 3),
                "execution_status": execution_status,
            }
            return self.repository.insert_request(event)
        except Exception as exc:  # pragma: no cover - defensive logging
            return {
                "request_id": request_id or str(uuid.uuid4()),
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
                "repository": repository or os.getenv("REPO_NAME", "unknown"),
                "user_prompt": user_prompt or "",
                "selected_files": selected_files or [],
                "total_files": total_files or 0,
                "original_token_count": 0,
                "compressed_token_count": 0,
                "tokens_saved": 0,
                "compression_ratio": 0.0,
                "latency_ms": 0.0,
                "estimated_cost": 0.0,
                "estimated_cost_saved": 0.0,
                "model": model or "unknown",
                "provider": provider or "unknown",
                "quality_score": 0.0,
                "execution_status": execution_status,
                "error": str(exc),
            }

    def get_recent_requests(self, limit: int = 100, repository: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.repository.list_requests(limit=limit, repository=repository)

    def get_overview(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        return self.repository.get_overview(start_date=start_date, end_date=end_date)

    def get_today_usage(self) -> List[Dict[str, Any]]:
        return self.repository.get_usage_series(granularity="hour", start_date=self._start_of_day(), end_date=self._end_of_day())

    def get_weekly_usage(self) -> List[Dict[str, Any]]:
        return self.repository.get_usage_series(granularity="day", start_date=self._start_of_week(), end_date=self._end_of_day())

    def get_monthly_usage(self) -> List[Dict[str, Any]]:
        return self.repository.get_usage_series(granularity="month", start_date=self._start_of_month(), end_date=self._end_of_day())

    def get_repository_analytics(self) -> List[Dict[str, Any]]:
        return self.repository.get_repository_analytics()

    def get_top_repositories(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.repository.get_top_repositories(limit=limit)

    def get_averages(self) -> Dict[str, Any]:
        return self.repository.get_averages()

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        normalized = re.sub(r"\s+", " ", (text or "")).strip()
        return max(1, int(len(normalized) / 4))

    @staticmethod
    def _estimate_cost(provider: str, model: str, original_tokens: int, compressed_tokens: int) -> float:
        provider_key = (provider or "unknown").lower()
        rates = {
            "openrouter": 0.000003,
            "bedrock": 0.000002,
            "groq": 0.000001,
        }
        rate = rates.get(provider_key, 0.000002)
        output_tokens = max(1, int(max(original_tokens, compressed_tokens) / 3))
        return round((original_tokens * rate) + (output_tokens * rate * 0.6), 6)

    @staticmethod
    def _start_of_day() -> str:
        now = datetime.now(timezone.utc)
        return now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    @staticmethod
    def _end_of_day() -> str:
        now = datetime.now(timezone.utc)
        return now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

    @staticmethod
    def _start_of_week() -> str:
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=now.weekday())
        return start.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    @staticmethod
    def _start_of_month() -> str:
        now = datetime.now(timezone.utc)
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


analytics_service = AnalyticsService()
