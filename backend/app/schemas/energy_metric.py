from datetime import datetime

from pydantic import BaseModel


class EnergyMetricBase(BaseModel):
    source_name: str
    metric_name: str
    unit: str
    value: float
    region: str


class EnergyMetricResponse(EnergyMetricBase):
    id: int
    captured_at: datetime

    model_config = {"from_attributes": True}


class EnergyMetricListResponse(BaseModel):
    items: list[EnergyMetricResponse]
    total: int

