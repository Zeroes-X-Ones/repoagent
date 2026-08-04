import os
import tempfile

from analytics.database import AnalyticsDatabase
from analytics.repository import AnalyticsRepository
from analytics.service import AnalyticsService


def test_record_request_persists_and_aggregates():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "analytics.sqlite3")
        repository = AnalyticsRepository(AnalyticsDatabase(db_path))
        service = AnalyticsService(repository)

        event = service.record_request(
            repository="demo-repo",
            user_prompt="Explain this module",
            selected_files=["app.py", "utils/model_router.py"],
            total_files=2,
            model="gpt-4o-mini",
            provider="openrouter",
            quality_score=0.91,
            execution_status="success",
            latency_ms=215.4,
        )

        assert event["request_id"]
        assert event["repository"] == "demo-repo"
        assert event["execution_status"] == "success"

        overview = service.get_overview()
        assert overview["total_requests"] == 1
        assert overview["average_quality"] >= 0.9
        assert overview["average_latency_ms"] >= 215.4
