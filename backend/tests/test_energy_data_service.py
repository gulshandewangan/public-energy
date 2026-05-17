import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.energy_record import EnergyDataRecord
from app.models.energy_snapshot import EnergySnapshot
from app.services.energy_data_service import EnergyDataService
from app.services.energy_scraper_service import EnergyScraperService, ScraperError


class StubScraper:
    def __init__(self, result=None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error

    def fetch_latest_energy_data(self):
        if self.error is not None:
            raise self.error
        return self.result


class StubDailyTrendService:
    def __init__(self) -> None:
        self.records = []

    def upsert_daily_snapshot(self, energy_data):
        self.records.append(energy_data)

    def list_daily_trends(self):
        return []


class EnergyDataServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.session = self.SessionLocal()
        self.daily_trend_service = StubDailyTrendService()

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_parses_state_ui_from_combined_frequency_row(self) -> None:
        current_ist = datetime.now(timezone.utc).astimezone(
            timezone(timedelta(hours=5, minutes=30))
        )
        sample = EnergyScraperService().parse_html_to_energy_data(
            f"""
            <html>
              <body>
                <span id="Label6">{current_ist.strftime("%d/%m/%Y %H:%M")}</span>
                <div>FREQUENCY : 50.08 STATE UI : 172</div>
                <span id="Label1">50.08</span>
                <span id="Label5">17019</span>
                <span id="lbl_thermal">3881</span>
                <span id="lbl_thrmipp">835</span>
                <span id="lbl_hydro">1547</span>
                <span id="lbl_wind">262</span>
                <span id="lbl_solar">3614</span>
                <div>PAVAGADA KSPDCL: 879</div>
                <div>BESCOM: 7870</div>
                <div>HESCOM :3073 GESCOM : 1345</div>
                <div>CESC :1889 MESCOM :1521</div>
              </body>
            </html>
            """
        )

        self.assertEqual(sample.frequency, 50.08)
        self.assertEqual(sample.state_ui, 172.0)
        self.assertEqual(sample.pavagada_kspdcl, 879.0)
        self.assertEqual(sample.bescom, 7870.0)
        self.assertEqual(sample.hescom, 3073.0)
        self.assertEqual(sample.gescom, 1345.0)
        self.assertEqual(sample.cesc, 1889.0)
        self.assertEqual(sample.mescom, 1521.0)

    def test_enriches_live_sample_with_derived_analysis_and_quality(self) -> None:
        current_ist = datetime.now(timezone.utc).astimezone(
            timezone(timedelta(hours=5, minutes=30))
        )
        sample = EnergyScraperService().parse_html_to_energy_data(
            f"""
            <html>
              <body>
                <span id="Label6">{current_ist.strftime("%d/%m/%Y %H:%M")}</span>
                <span id="Label1">49.98</span>
                <div>STATE UI : 300</div>
                <span id="Label5">10000</span>
                <span id="lbl_thermal">4200</span>
                <span id="lbl_thrmipp">300</span>
                <span id="lbl_hydro">1800</span>
                <span id="lbl_wind">900</span>
                <span id="lbl_solar">1600</span>
                <div>PAVAGADA KSPDCL: 879</div>
                <div>BESCOM: 7870</div>
                <div>HESCOM :3073 GESCOM : 1345</div>
                <div>CESC :1889 MESCOM :1521</div>
              </body>
            </html>
            """
        )
        service = EnergyDataService(
            session=self.session,
            scraper_service=StubScraper(result=sample),
            daily_trend_service=self.daily_trend_service,
        )

        result = service.get_latest_energy_data()

        self.assertEqual(result.quality.source_mode, "live")
        self.assertEqual(result.quality.confidence_label, "high")
        self.assertEqual(result.state_ui, 300.0)
        self.assertEqual(result.pavagada_kspdcl, 879.0)
        self.assertEqual(result.bescom, 7870.0)
        self.assertEqual(result.hescom, 3073.0)
        self.assertEqual(result.gescom, 1345.0)
        self.assertEqual(result.cesc, 1889.0)
        self.assertEqual(result.mescom, 1521.0)
        self.assertEqual(result.thermal, 4200.0)
        self.assertEqual(result.thermal_ipp, 300.0)
        self.assertEqual(result.analysis.total_generation, 8800.0)
        self.assertEqual(result.analysis.renewable_generation, 4300.0)
        self.assertEqual(result.analysis.demand_gap_mw, -1200.0)
        self.assertEqual(result.analysis.balance_state, "deficit")
        self.assertAlmostEqual(result.analysis.renewable_share_pct, 48.86, places=2)
        self.assertEqual(len(self.daily_trend_service.records), 1)

    def test_uses_cached_snapshot_when_live_scrape_fails(self) -> None:
        captured_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        self.session.add(
            EnergySnapshot(
                frequency=49.94,
                demand=9000.0,
                thermal=4200.0,
                thermal_ipp=350.0,
                hydro=1700.0,
                wind=1200.0,
                solar=1800.0,
                captured_at=captured_at,
                state_ui=145.0,
                pavagada_kspdcl=820.0,
                bescom=6100.0,
                hescom=2400.0,
                gescom=1150.0,
                cesc=1500.0,
                mescom=1300.0,
            )
        )
        self.session.commit()

        service = EnergyDataService(
            session=self.session,
            scraper_service=StubScraper(error=ScraperError("source unavailable")),
            daily_trend_service=self.daily_trend_service,
        )

        result = service.get_latest_energy_data()

        self.assertFalse(result.is_live)
        self.assertEqual(result.data_source, "last_stored_fallback")
        self.assertEqual(result.quality.source_mode, "cached")
        self.assertEqual(result.quality.confidence_label, "moderate")
        self.assertEqual(result.state_ui, 145.0)
        self.assertEqual(result.bescom, 6100.0)
        self.assertEqual(result.mescom, 1300.0)
        self.assertEqual(result.thermal_ipp, 350.0)
        self.assertIsNotNone(result.quality.source_age_seconds)
        self.assertEqual(result.analysis.balance_state, "surplus")
        self.assertEqual(len(self.daily_trend_service.records), 0)

    def test_stores_a_history_record_for_each_returned_sample(self) -> None:
        sample = EnergyScraperService().parse_html_to_energy_data(
            """
            <html>
              <body>
                <span id="Label6">24/04/2026 18:30</span>
                <span id="Label1">50.00</span>
                <span id="Label5">8000</span>
                <span id="lbl_thermal">3000</span>
                <span id="lbl_thrmipp">500</span>
                <span id="lbl_hydro">1500</span>
                <span id="lbl_wind">1000</span>
                <span id="lbl_solar">2200</span>
                <div>PAVAGADA KSPDCL: 700</div>
                <div>BESCOM: 5000</div>
                <div>HESCOM :2000 GESCOM : 1100</div>
                <div>CESC :1400 MESCOM :1200</div>
              </body>
            </html>
            """
        )
        service = EnergyDataService(
            session=self.session,
            scraper_service=StubScraper(result=sample),
            daily_trend_service=self.daily_trend_service,
        )

        result = service.get_latest_energy_data()
        stored_records = self.session.query(EnergyDataRecord).all()

        self.assertEqual(len(stored_records), 1)
        self.assertEqual(stored_records[0].state_ui, result.state_ui)
        self.assertEqual(stored_records[0].demand, result.demand)
        self.assertEqual(stored_records[0].thermal_ipp, result.thermal_ipp)
        self.assertEqual(stored_records[0].bescom, result.bescom)
        self.assertEqual(stored_records[0].solar, result.solar)


if __name__ == "__main__":
    unittest.main()
