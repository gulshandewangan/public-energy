from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.energy_metric import EnergyMetric
from app.schemas.energy_metric import EnergyMetricListResponse, EnergyMetricResponse
from app.services.scraper_service import ScraperService


class MetricService:
    def __init__(self, session: Session, scraper_service: ScraperService | None = None) -> None:
        self.session = session
        self.scraper_service = scraper_service or ScraperService()

    def list_metrics(self) -> EnergyMetricListResponse:
        statement = select(EnergyMetric).order_by(EnergyMetric.captured_at.desc())
        metrics = self.session.scalars(statement).all()
        return EnergyMetricListResponse(
            items=[EnergyMetricResponse.model_validate(metric) for metric in metrics],
            total=len(metrics),
        )

    def refresh_metrics(self) -> EnergyMetricListResponse:
        scraped_items = self.scraper_service.fetch_latest_metrics()

        for item in scraped_items:
            metric = EnergyMetric(**item)
            self.session.add(metric)

        self.session.commit()
        return self.list_metrics()


def get_metric_service(session: Session = Depends(get_db_session)) -> MetricService:
    return MetricService(session=session)

