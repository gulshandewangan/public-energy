import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.models.energy_data import EnergyData


class ScraperError(Exception):
    pass


class EnergyScraperService:
    """Scrapes KPTCL/SLDC-style pages and maps them to the API contract."""

    FIELD_ALIASES = {
        "frequency": ["grid frequency", "frequency"],
        "state_ui": ["state ui"],
        "demand": ["state demand", "current demand", "total demand", "demand", "load"],
        "thermal": ["thermal generation", "thermal"],
        "hydro": ["hydel", "hydro generation", "hydro"],
        "wind": ["wind generation", "wind"],
        "solar": ["solar generation", "solar"],
        "pavagada_kspdcl": ["pavagada kspdcl"],
        "bescom": ["bescom"],
        "hescom": ["hescom"],
        "gescom": ["gescom"],
        "cesc": ["cesc"],
        "mescom": ["mescom"],
    }

    KPTCL_SELECTORS = {
        "timestamp": "#Label6",
        "frequency": "#Label1",
        "demand": "#Label5",
        "thermal": "#lbl_thermal",
        "thermal_ipp": "#lbl_thrmipp",
        "hydro": "#lbl_hydro",
        "wind": "#lbl_wind",
        "solar": "#lbl_solar",
    }

    IST = timezone(timedelta(hours=5, minutes=30))

    def __init__(self, source_url: str | None = None, timeout_seconds: int | None = None) -> None:
        self.source_url = source_url or settings.energy_source_url
        self.timeout_seconds = timeout_seconds or settings.energy_source_timeout_seconds

    def fetch_latest_energy_data(self) -> EnergyData:
        if not self.source_url:
            raise ScraperError("ENERGY_SOURCE_URL is not configured. Create backend/.env and set a real source URL.")

        try:
            response = requests.get(
                self.source_url,
                timeout=self.timeout_seconds,
                headers={"User-Agent": "PublicEnergyClimateTracker/0.1"},
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ScraperError(f"Failed to fetch source page: {exc}") from exc

        return self.parse_html_to_energy_data(response.text)

    def parse_html_to_energy_data(self, html: str) -> EnergyData:
        soup = BeautifulSoup(html, "html.parser")

        kptcl_data = self._extract_kptcl_homepage_data(soup)
        if kptcl_data is not None:
            return kptcl_data

        rows = self._extract_candidate_rows(soup)
        parsed_values = {
            field: self._extract_numeric_value(rows, aliases)
            for field, aliases in self.FIELD_ALIASES.items()
        }

        required_fields = ["frequency", "demand", "thermal", "hydro", "wind", "solar"]
        missing_fields = [field for field in required_fields if parsed_values[field] is None]
        if missing_fields:
            raise ScraperError(
                f"Unable to extract required fields from page: {', '.join(missing_fields)}"
            )

        now = datetime.now(timezone.utc)
        return EnergyData(
            frequency=parsed_values["frequency"],
            state_ui=parsed_values["state_ui"] or 0.0,
            demand=parsed_values["demand"],
            thermal=parsed_values["thermal"],
            thermal_ipp=0.0,
            hydro=parsed_values["hydro"],
            wind=parsed_values["wind"],
            solar=parsed_values["solar"],
            pavagada_kspdcl=parsed_values["pavagada_kspdcl"] or 0.0,
            bescom=parsed_values["bescom"] or 0.0,
            hescom=parsed_values["hescom"] or 0.0,
            gescom=parsed_values["gescom"] or 0.0,
            cesc=parsed_values["cesc"] or 0.0,
            mescom=parsed_values["mescom"] or 0.0,
            timestamp=now,
            is_live=True,
            data_source="live_scrape",
            source_timestamp=now,
        )

    def _extract_kptcl_homepage_data(self, soup: BeautifulSoup) -> EnergyData | None:
        selector_values = {}
        for key, selector in self.KPTCL_SELECTORS.items():
            element = soup.select_one(selector)
            selector_values[key] = element.get_text(strip=True) if element else None

        required_keys = ["frequency", "demand", "thermal", "hydro", "wind", "solar"]
        if not all(selector_values.get(key) for key in required_keys):
            return None

        now = datetime.now(timezone.utc)
        rows = self._extract_candidate_rows(soup)
        thermal = self._parse_number(selector_values["thermal"]) or 0.0
        thermal_ipp = self._parse_number(selector_values["thermal_ipp"] or "") or 0.0
        state_ui = self._extract_numeric_value(rows, self.FIELD_ALIASES["state_ui"]) or 0.0
        pavagada_kspdcl = self._extract_numeric_value(rows, self.FIELD_ALIASES["pavagada_kspdcl"]) or 0.0
        bescom = self._extract_numeric_value(rows, self.FIELD_ALIASES["bescom"]) or 0.0
        hescom = self._extract_numeric_value(rows, self.FIELD_ALIASES["hescom"]) or 0.0
        gescom = self._extract_numeric_value(rows, self.FIELD_ALIASES["gescom"]) or 0.0
        cesc = self._extract_numeric_value(rows, self.FIELD_ALIASES["cesc"]) or 0.0
        mescom = self._extract_numeric_value(rows, self.FIELD_ALIASES["mescom"]) or 0.0
        source_timestamp = self._parse_kptcl_timestamp(selector_values.get("timestamp"))

        return EnergyData(
            frequency=self._require_number("frequency", selector_values["frequency"]),
            state_ui=state_ui,
            demand=self._require_number("demand", selector_values["demand"]),
            thermal=thermal,
            thermal_ipp=thermal_ipp,
            hydro=self._require_number("hydro", selector_values["hydro"]),
            wind=self._require_number("wind", selector_values["wind"]),
            solar=self._require_number("solar", selector_values["solar"]),
            pavagada_kspdcl=pavagada_kspdcl,
            bescom=bescom,
            hescom=hescom,
            gescom=gescom,
            cesc=cesc,
            mescom=mescom,
            timestamp=now,
            is_live=True,
            data_source="kptcl_live_homepage",
            source_timestamp=source_timestamp or now,
        )

    def _parse_kptcl_timestamp(self, value: str | None) -> datetime | None:
        if not value:
            return None

        try:
            naive_dt = datetime.strptime(value, "%d/%m/%Y %H:%M")
            return naive_dt.replace(tzinfo=self.IST)
        except ValueError:
            return None

    def _require_number(self, field_name: str, value: str) -> float:
        parsed = self._parse_number(value)
        if parsed is None:
            raise ScraperError(f"Unable to parse numeric value for {field_name}")
        return parsed

    def _extract_candidate_rows(self, soup: BeautifulSoup) -> list[str]:
        rows: list[str] = []
        interesting_aliases = [alias for aliases in self.FIELD_ALIASES.values() for alias in aliases]

        for selector in ["tr", "li", "div", "span", "p", "td", "th"]:
            for element in soup.select(selector):
                text = " ".join(element.stripped_strings)
                lowered = text.lower()
                if text and any(alias in lowered for alias in interesting_aliases):
                    rows.append(text)

        if not rows:
            rows.append(" ".join(soup.stripped_strings))

        return rows

    def _extract_numeric_value(self, rows: list[str], aliases: list[str]) -> float | None:
        for row in rows:
            lowered_row = row.lower()
            for alias in aliases:
                if alias not in lowered_row:
                    continue

                value = self._parse_number_after_alias(row, alias)
                if value is not None:
                    return value

            value = self._parse_number(row)
            if value is not None and any(alias in lowered_row for alias in aliases):
                return value

        return None

    def _parse_number_after_alias(self, text: str, alias: str) -> float | None:
        match = re.search(
            rf"{re.escape(alias)}\s*[:\-]?\s*(-?\d[\d,]*\.?\d*)",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            return None

        return float(match.group(1).replace(",", ""))

    def _parse_number(self, text: str) -> float | None:
        match = re.search(r"(-?\d[\d,]*\.?\d*)", text)
        if not match:
            return None

        return float(match.group(1).replace(",", ""))
