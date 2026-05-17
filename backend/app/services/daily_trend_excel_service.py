import json
import subprocess
import sys
from datetime import timezone
from pathlib import Path

from app.core.config import settings
from app.models.energy_data import DailyTrendPoint, EnergyData


class DailyTrendExcelService:
    def __init__(self) -> None:
        self.workbook_path = Path(settings.daily_trend_workbook_path).resolve()
        self.helper_script_path = (
            Path(__file__).resolve().parents[2] / "scripts" / "daily_trend_excel_helper.py"
        )

    def upsert_daily_snapshot(self, energy_data: EnergyData) -> None:
        trend_date = (energy_data.source_timestamp or energy_data.timestamp).date().isoformat()
        total_generation = round(
            energy_data.thermal
            + energy_data.thermal_ipp
            + energy_data.hydro
            + energy_data.wind
            + energy_data.solar,
            2,
        )
        renewable_generation = round(
            energy_data.hydro + energy_data.wind + energy_data.solar,
            2,
        )
        renewable_share_pct = round(
            (renewable_generation / total_generation) * 100,
            2,
        ) if total_generation else 0.0

        payload = {
            "date": trend_date,
            "timestamp": energy_data.timestamp.astimezone(timezone.utc).isoformat(),
            "demand": energy_data.demand,
            "frequency": energy_data.frequency,
            "state_ui": energy_data.state_ui,
            "thermal": energy_data.thermal,
            "thermal_ipp": energy_data.thermal_ipp,
            "hydro": energy_data.hydro,
            "wind": energy_data.wind,
            "solar": energy_data.solar,
            "total_generation": total_generation,
            "renewable_generation": renewable_generation,
            "renewable_share_pct": renewable_share_pct,
            "pavagada_kspdcl": energy_data.pavagada_kspdcl,
            "bescom": energy_data.bescom,
            "hescom": energy_data.hescom,
            "gescom": energy_data.gescom,
            "cesc": energy_data.cesc,
            "mescom": energy_data.mescom,
        }
        self._run_helper("upsert", input_payload=payload)

    def list_daily_trends(self) -> list[DailyTrendPoint]:
        records = self._run_helper("read")
        return [
            DailyTrendPoint(
                date=str(record["date"]),
                demand=float(record.get("demand") or 0.0),
                total_generation=float(record.get("total_generation") or 0.0),
                renewable_generation=float(record.get("renewable_generation") or 0.0),
                renewable_share_pct=float(record.get("renewable_share_pct") or 0.0),
                state_ui=float(record.get("state_ui") or 0.0),
                bescom=float(record.get("bescom") or 0.0),
            )
            for record in records
        ]

    def _run_helper(self, command: str, input_payload: dict | None = None):
        input_text = json.dumps(input_payload) if input_payload is not None else None
        last_error = None

        for python_path in self._candidate_python_paths():
            try:
                completed = subprocess.run(
                    [python_path, str(self.helper_script_path), command, str(self.workbook_path)],
                    input=input_text,
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=20,
                )
                stdout = completed.stdout.strip()
                return json.loads(stdout) if stdout else []
            except Exception as exc:  # noqa: BLE001
                last_error = exc

        raise RuntimeError("Unable to execute Excel helper for daily trend storage") from last_error

    def _candidate_python_paths(self) -> list[str]:
        candidates = []
        configured = settings.spreadsheet_python_path.strip()
        if configured:
            candidates.append(configured)

        candidates.append(
            str(
                Path.home()
                / ".cache"
                / "codex-runtimes"
                / "codex-primary-runtime"
                / "dependencies"
                / "python"
                / "python.exe"
            )
        )
        candidates.append(sys.executable)

        unique_candidates = []
        for candidate in candidates:
            if candidate and candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates
