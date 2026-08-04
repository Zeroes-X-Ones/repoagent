import os
import sqlite3
from typing import Optional


class AnalyticsDatabase:
    """SQLite-backed persistence layer for analytics events.

    The repository layer is intentionally isolated so a future database backend can
    be swapped in without changing the service/controller contracts.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv(
            "ANALYTICS_DB_PATH",
            os.path.join(os.getcwd(), "analytics.sqlite3"),
        )
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS analytics_events (
                    request_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    user_prompt TEXT NOT NULL,
                    selected_files TEXT NOT NULL,
                    total_files INTEGER NOT NULL DEFAULT 0,
                    original_token_count INTEGER NOT NULL DEFAULT 0,
                    compressed_token_count INTEGER NOT NULL DEFAULT 0,
                    tokens_saved INTEGER NOT NULL DEFAULT 0,
                    compression_ratio REAL NOT NULL DEFAULT 0.0,
                    latency_ms REAL NOT NULL DEFAULT 0.0,
                    estimated_cost REAL NOT NULL DEFAULT 0.0,
                    estimated_cost_saved REAL NOT NULL DEFAULT 0.0,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    quality_score REAL NOT NULL DEFAULT 0.0,
                    execution_status TEXT NOT NULL DEFAULT 'success',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp
                    ON analytics_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_analytics_events_repository
                    ON analytics_events(repository);
                CREATE INDEX IF NOT EXISTS idx_analytics_events_provider
                    ON analytics_events(provider);
                """
            )
