from fastapi import APIRouter, Depends

from app.schemas.energy_metric import EnergyMetricListResponse
from app.services.metric_service import MetricService, get_metric_service

router = APIRouter()


@router.get("", response_model=EnergyMetricListResponse)
def list_metrics(
    metric_service: MetricService = Depends(get_metric_service),
) -> EnergyMetricListResponse:
    return metric_service.list_metrics()


@router.post("/refresh", response_model=EnergyMetricListResponse)
def refresh_metrics(
    metric_service: MetricService = Depends(get_metric_service),
) -> EnergyMetricListResponse:
    return metric_service.refresh_metrics()

