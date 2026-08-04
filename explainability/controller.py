from typing import List, Optional

from fastapi import APIRouter, Query

from explainability.benchmark_service import benchmark_service
from explainability.service import explainability_service

router = APIRouter(prefix="/api/explainability", tags=["explainability"])


@router.post("/report")
def create_explainability_report(
    repository: str,
    user_prompt: str,
    kept_files: List[str],
    removed_files: List[str],
    retrieved_blocks: Optional[List[dict]] = None,
    model: str = "unknown",
    provider: str = "unknown",
):
    return {
        "ok": True,
        "data": explainability_service.build_explanation(
            repository=repository,
            user_prompt=user_prompt,
            kept_files=kept_files,
            removed_files=removed_files,
            retrieved_blocks=retrieved_blocks or [],
            model=model,
            provider=provider,
        ),
    }


@router.post("/benchmark")
def run_benchmark(
    prompt: str,
    repository: str,
    pipelines: Optional[List[str]] = Query(default=None),
    model: str = "claude",
    provider: str = "openrouter",
):
    return {
        "ok": True,
        "data": benchmark_service.run_benchmark(
            prompt=prompt,
            repository=repository,
            pipelines=pipelines,
            model=model,
            provider=provider,
        ),
    }


@router.get("/benchmark/history")
def benchmark_history():
    return {"ok": True, "data": benchmark_service.list_history()}


@router.get("/benchmark/compare")
def compare_benchmark(benchmark_id: Optional[str] = None):
    return {"ok": True, "data": benchmark_service.compare(benchmark_id=benchmark_id)}
