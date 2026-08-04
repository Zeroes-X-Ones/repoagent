from typing import Optional

from fastapi import APIRouter, Query

from analytics.service import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/requests")
def list_requests(
    repository: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    return {"ok": True, "data": analytics_service.get_recent_requests(limit=limit, repository=repository)}


@router.get("/overview")
def overview():
    return {"ok": True, "data": analytics_service.get_overview()}


@router.get("/usage/today")
def usage_today():
    return {"ok": True, "data": analytics_service.get_today_usage()}


@router.get("/usage/weekly")
def usage_weekly():
    return {"ok": True, "data": analytics_service.get_weekly_usage()}


@router.get("/usage/monthly")
def usage_monthly():
    return {"ok": True, "data": analytics_service.get_monthly_usage()}


@router.get("/repositories")
def repository_analytics():
    return {"ok": True, "data": analytics_service.get_repository_analytics()}


@router.get("/top-repositories")
def top_repositories(limit: int = Query(default=10, ge=1, le=50)):
    return {"ok": True, "data": analytics_service.get_top_repositories(limit=limit)}


@router.get("/averages")
def averages():
    return {"ok": True, "data": analytics_service.get_averages()}
