import logging
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.energy_data import EnergyData, HistoricalEnergyData
from app.models.energy_record import EnergyDataRecord
from app.models.energy_snapshot import EnergySnapshot
from app.services.daily_trend_excel_service import DailyTrendExcelService
from app.services.energy_scraper_service import EnergyScraperService, ScraperError

logger = logging.getLogger(__name__)


class EnergyDataService:
    def __init__(
        self,
        session: Session,
        scraper_service: EnergyScraperService | None = None,
        daily_trend_service: DailyTrendExcelService | None = None,
    ) -> None:
        self.session = session
        self.scraper_service = scraper_service or EnergyScraperService()
        self.daily_trend_service = daily_trend_service or DailyTrendExcelService()

    def get_latest_energy_data(self) -> EnergyData:
        try:
            energy_data = self.scraper_service.fetch_latest_energy_data()
        except ScraperError as exc:
            logger.warning("Live energy scrape failed: %s", exc)
            last_snapshot = self._get_last_snapshot()
            if last_snapshot is not None:
                energy_data = self._snapshot_to_energy_data(last_snapshot)
            else:
                energy_data = self._build_simulated_data()

        energy_data = self._enrich_energy_data(energy_data)
        self._store_record(energy_data)
        self._store_daily_trend(energy_data)
        return energy_data

    def list_historical_data(self, limit: int = 50) -> list[HistoricalEnergyData]:
        statement = (
            select(EnergyDataRecord)
            .order_by(EnergyDataRecord.timestamp.desc(), EnergyDataRecord.id.desc())
            .limit(limit)
        )
        records = self.session.scalars(statement).all()
        return [
            HistoricalEnergyData(
                id=record.id,
                timestamp=record.timestamp,
                frequency=record.frequency,
                state_ui=record.state_ui,
                demand=record.demand,
                thermal=record.thermal,
                thermal_ipp=record.thermal_ipp,
                hydro=record.hydro,
                wind=record.wind,
                solar=record.solar,
                pavagada_kspdcl=record.pavagada_kspdcl,
                bescom=record.bescom,
                hescom=record.hescom,
                gescom=record.gescom,
                cesc=record.cesc,
                mescom=record.mescom,
            )
            for record in records
        ]

    def get_daily_trends(self):
        try:
            records = self.daily_trend_service.list_daily_trends()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Daily Excel trend read failed: %s", exc)
            records = []
        return {
            "records": records,
            "insights": self._build_daily_trend_insights(records),
        }

    def _store_record(self, energy_data: EnergyData) -> None:
        record = EnergyDataRecord(
            timestamp=energy_data.timestamp,
            frequency=energy_data.frequency,
            state_ui=energy_data.state_ui,
            demand=energy_data.demand,
            thermal=energy_data.thermal,
            thermal_ipp=energy_data.thermal_ipp,
            hydro=energy_data.hydro,
            wind=energy_data.wind,
            solar=energy_data.solar,
            pavagada_kspdcl=energy_data.pavagada_kspdcl,
            bescom=energy_data.bescom,
            hescom=energy_data.hescom,
            gescom=energy_data.gescom,
            cesc=energy_data.cesc,
            mescom=energy_data.mescom,
        )
        self.session.add(record)
        self.session.commit()

    def _store_daily_trend(self, energy_data: EnergyData) -> None:
        if not energy_data.is_live:
            return

        try:
            self.daily_trend_service.upsert_daily_snapshot(energy_data)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Daily Excel trend storage failed: %s", exc)

    def _get_last_snapshot(self) -> EnergySnapshot | None:
        statement = select(EnergyDataRecord).order_by(
            EnergyDataRecord.timestamp.desc(), EnergyDataRecord.id.desc()
        )
        last_record = self.session.scalars(statement).first()
        if last_record is not None:
            return EnergySnapshot(
                frequency=last_record.frequency,
                state_ui=last_record.state_ui,
                demand=last_record.demand,
                thermal=last_record.thermal,
                thermal_ipp=last_record.thermal_ipp,
                hydro=last_record.hydro,
                wind=last_record.wind,
                solar=last_record.solar,
                pavagada_kspdcl=last_record.pavagada_kspdcl,
                bescom=last_record.bescom,
                hescom=last_record.hescom,
                gescom=last_record.gescom,
                cesc=last_record.cesc,
                mescom=last_record.mescom,
                captured_at=last_record.timestamp,
            )

        legacy_statement = select(EnergySnapshot).order_by(EnergySnapshot.captured_at.desc())
        return self.session.scalars(legacy_statement).first()

    def _snapshot_to_energy_data(self, snapshot: EnergySnapshot) -> EnergyData:
        return EnergyData(
            frequency=snapshot.frequency,
            state_ui=snapshot.state_ui,
            demand=snapshot.demand,
            thermal=snapshot.thermal,
            thermal_ipp=snapshot.thermal_ipp,
            hydro=snapshot.hydro,
            wind=snapshot.wind,
            solar=snapshot.solar,
            pavagada_kspdcl=snapshot.pavagada_kspdcl,
            bescom=snapshot.bescom,
            hescom=snapshot.hescom,
            gescom=snapshot.gescom,
            cesc=snapshot.cesc,
            mescom=snapshot.mescom,
            timestamp=datetime.now(timezone.utc),
            is_live=False,
            data_source="last_stored_fallback",
            source_timestamp=snapshot.captured_at,
        )

    def _build_simulated_data(self) -> EnergyData:
        return EnergyData(
            frequency=49.96,
            state_ui=210.0,
            demand=12450.0,
            thermal=4220.0,
            thermal_ipp=1200.0,
            hydro=2840.0,
            wind=1680.0,
            solar=2510.0,
            pavagada_kspdcl=930.0,
            bescom=5810.0,
            hescom=2290.0,
            gescom=1090.0,
            cesc=1440.0,
            mescom=1210.0,
            timestamp=datetime.now(timezone.utc),
            is_live=False,
            data_source="simulated_fallback",
            source_timestamp=None,
        )

    def _enrich_energy_data(self, energy_data: EnergyData) -> EnergyData:
        total_generation = round(
            energy_data.thermal
            + energy_data.thermal_ipp
            + energy_data.hydro
            + energy_data.wind
            + energy_data.solar,
            2,
        )
        renewable_generation = round(
            energy_data.hydro + energy_data.wind + energy_data.solar, 2
        )
        demand_gap_mw = round(total_generation - energy_data.demand, 2)
        reserve_margin_pct = round(
            (demand_gap_mw / energy_data.demand) * 100, 2
        ) if energy_data.demand else 0.0
        renewable_share_pct = round(
            (renewable_generation / total_generation) * 100, 2
        ) if total_generation else 0.0
        thermal_share_pct = round(
            ((energy_data.thermal + energy_data.thermal_ipp) / total_generation) * 100, 2
        ) if total_generation else 0.0
        frequency_deviation_hz = round(abs(energy_data.frequency - 50.0), 3)
        coverage_ratio = round(
            (total_generation / energy_data.demand), 3
        ) if energy_data.demand else 0.0

        now = energy_data.timestamp.astimezone(timezone.utc)
        freshness_seconds = max(
            0.0,
            round((datetime.now(timezone.utc) - now).total_seconds(), 2),
        )
        source_age_seconds = None
        if energy_data.source_timestamp is not None:
            source_age_seconds = max(
                0.0,
                round(
                    (
                        datetime.now(timezone.utc)
                        - energy_data.source_timestamp.astimezone(timezone.utc)
                    ).total_seconds(),
                    2,
                ),
            )

        confidence_score = self._calculate_confidence_score(
            energy_data=energy_data,
            reserve_margin_pct=reserve_margin_pct,
            source_age_seconds=source_age_seconds,
        )

        payload = energy_data.model_dump()
        payload["analysis"] = {
            "total_generation": total_generation,
            "renewable_generation": renewable_generation,
            "renewable_share_pct": renewable_share_pct,
            "thermal_share_pct": thermal_share_pct,
            "demand_gap_mw": demand_gap_mw,
            "reserve_margin_pct": reserve_margin_pct,
            "frequency_deviation_hz": frequency_deviation_hz,
            "balance_state": self._classify_balance_state(reserve_margin_pct),
        }
        payload["quality"] = {
            "source_mode": self._classify_source_mode(energy_data),
            "confidence_score": confidence_score,
            "confidence_label": self._label_confidence(confidence_score),
            "freshness_seconds": freshness_seconds,
            "freshness_label": self._label_freshness(
                source_age_seconds if source_age_seconds is not None else freshness_seconds
            ),
            "source_age_seconds": source_age_seconds,
            "coverage_ratio": coverage_ratio,
        }
        return EnergyData.model_validate(payload)

    def _classify_balance_state(self, reserve_margin_pct: float) -> str:
        if reserve_margin_pct >= 2:
            return "surplus"
        if reserve_margin_pct <= -2:
            return "deficit"
        return "tight"

    def _classify_source_mode(self, energy_data: EnergyData) -> str:
        if energy_data.is_live:
            return "live"
        if energy_data.data_source == "last_stored_fallback":
            return "cached"
        return "simulated"

    def _label_freshness(self, age_seconds: float) -> str:
        if age_seconds <= 60:
            return "fresh"
        if age_seconds <= 15 * 60:
            return "recent"
        if age_seconds <= 60 * 60:
            return "aging"
        return "stale"

    def _label_confidence(self, confidence_score: float) -> str:
        if confidence_score >= 0.85:
            return "high"
        if confidence_score >= 0.6:
            return "moderate"
        return "exploratory"

    def _calculate_confidence_score(
        self,
        energy_data: EnergyData,
        reserve_margin_pct: float,
        source_age_seconds: float | None,
    ) -> float:
        source_mode = self._classify_source_mode(energy_data)
        base_score = {
            "live": 0.95,
            "cached": 0.72,
            "simulated": 0.4,
        }[source_mode]

        if source_age_seconds is not None and source_age_seconds > 15 * 60:
            base_score -= 0.12
        if abs(reserve_margin_pct) > 15:
            base_score -= 0.08

        return round(min(0.99, max(0.2, base_score)), 2)

    def _build_daily_trend_insights(self, records):
        if not records:
            return [
                {
                    "title": "No daily archive yet",
                    "value": "Waiting",
                    "detail": "The Excel-backed day-to-day archive will appear after live samples are stored.",
                    "tone": "amber",
                }
            ]

        if len(records) == 1:
            record = records[0]
            return [
                {
                    "title": "Archive seeded",
                    "value": record.date,
                    "detail": "One daily row is available. A direct day-to-day comparison will appear after the next day is archived.",
                    "tone": "sky",
                }
            ]

        latest = records[-1]
        previous = records[-2]
        demand_delta = round(latest.demand - previous.demand, 2)
        renewable_delta = round(latest.renewable_share_pct - previous.renewable_share_pct, 2)
        strongest_day = max(records, key=lambda record: record.total_generation)

        return [
            {
                "title": "Demand shift vs previous day",
                "value": f"{demand_delta:+,.0f} MW",
                "detail": f"{latest.date} compared with {previous.date}.",
                "tone": "amber" if demand_delta >= 0 else "sky",
            },
            {
                "title": "Renewable share movement",
                "value": f"{renewable_delta:+.1f} pts",
                "detail": f"Latest day closed at {latest.renewable_share_pct:.1f}% renewable share.",
                "tone": "emerald" if renewable_delta >= 0 else "orange",
            },
            {
                "title": "Strongest generation day",
                "value": strongest_day.date,
                "detail": f"{strongest_day.total_generation:,.0f} MW total generation in the Excel archive.",
                "tone": "violet",
            },
        ]


def get_energy_data_service(session: Session = Depends(get_db_session)) -> EnergyDataService:
    return EnergyDataService(session=session)
