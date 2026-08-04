import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from explainability.benchmark_service import benchmark_service
from explainability.service import explainability_service


def test_explainability_report_contains_kept_and_removed_files():
    report = explainability_service.build_explanation(
        repository="demo-repo",
        user_prompt="Explain auth flow",
        kept_files=["auth.py", "db.py"],
        removed_files=["README.md", "tests/test_auth.py"],
        retrieved_blocks=[{"file": "auth.py", "score": 0.91}],
        model="claude",
        provider="paritok",
    )

    assert report["summary"]["kept_count"] == 2
    assert report["summary"]["removed_count"] == 2
    assert report["kept_files"][0]["retained"] is True
    assert report["removed_files"][0]["retained"] is False


def test_benchmark_service_records_pipeline_metrics():
    result = benchmark_service.run_benchmark(
        prompt="Explain auth flow",
        repository="demo-repo",
        model="claude",
        provider="paritok",
    )

    assert len(result["pipelines"]) == 2
    assert result["pipelines"][0]["execution_success"] is True
    assert result["pipelines"][1]["quality_score"] >= 0.9
