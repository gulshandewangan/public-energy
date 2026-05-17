from fastapi import APIRouter, Depends

from app.models.energy_data import DailyTrendResponse, EnergyData, HistoricalEnergyData
from app.services.energy_data_service import EnergyDataService, get_energy_data_service

router = APIRouter()


@router.get("/energy-data", response_model=EnergyData, tags=["energy-data"])
def get_energy_data(
    energy_data_service: EnergyDataService = Depends(get_energy_data_service),
) -> EnergyData:
    return energy_data_service.get_latest_energy_data()


@router.get("/historical-data", response_model=list[HistoricalEnergyData], tags=["historical-data"])
def get_historical_data(
    energy_data_service: EnergyDataService = Depends(get_energy_data_service),
) -> list[HistoricalEnergyData]:
    return energy_data_service.list_historical_data(limit=50)


@router.get("/daily-trends", response_model=DailyTrendResponse, tags=["daily-trends"])
def get_daily_trends(
    energy_data_service: EnergyDataService = Depends(get_energy_data_service),
) -> DailyTrendResponse:
    return DailyTrendResponse.model_validate(energy_data_service.get_daily_trends())
