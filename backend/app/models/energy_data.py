from datetime import datetime

from pydantic import BaseModel, Field


class EnergyAnalysis(BaseModel):
    total_generation: float = Field(
        ...,
        description="Sum of thermal, thermal IPP, hydro, wind, and solar generation in MW",
    )
    renewable_generation: float = Field(..., description="Sum of hydro, wind, and solar generation in MW")
    renewable_share_pct: float = Field(..., description="Renewable generation as a percentage of total generation")
    thermal_share_pct: float = Field(
        ...,
        description="Combined thermal and thermal IPP generation as a percentage of total generation",
    )
    demand_gap_mw: float = Field(..., description="Generation minus demand in MW")
    reserve_margin_pct: float = Field(..., description="Generation surplus or deficit as a percentage of demand")
    frequency_deviation_hz: float = Field(..., description="Absolute deviation from the nominal 50 Hz grid frequency")
    balance_state: str = Field(..., description="Qualitative assessment of the demand-supply balance")


class DataQualityAssessment(BaseModel):
    source_mode: str = Field(..., description="Categorization of whether the values are live, cached, or simulated")
    confidence_score: float = Field(..., description="Heuristic confidence score for interpreting the sample")
    confidence_label: str = Field(..., description="Human-readable confidence band derived from the score")
    freshness_seconds: float = Field(..., description="Age of the API sample in seconds")
    freshness_label: str = Field(..., description="Human-readable freshness bucket")
    source_age_seconds: float | None = Field(
        default=None,
        description="Age of the original source sample in seconds when a source timestamp is available",
    )
    coverage_ratio: float = Field(..., description="Generation divided by demand")


class DailyTrendPoint(BaseModel):
    date: str = Field(..., description="Daily bucket in ISO date format")
    demand: float = Field(..., description="Daily demand snapshot in MW")
    total_generation: float = Field(..., description="Total generation snapshot in MW")
    renewable_generation: float = Field(..., description="Renewable generation snapshot in MW")
    renewable_share_pct: float = Field(..., description="Renewable share of total generation")
    state_ui: float = Field(..., description="State UI in MW")
    bescom: float = Field(..., description="BESCOM in MW")


class DailyTrendInsight(BaseModel):
    title: str = Field(..., description="Short insight title")
    value: str = Field(..., description="Primary takeaway value")
    detail: str = Field(..., description="Short explanatory sentence")
    tone: str = Field(..., description="Visual tone for the insight card")


class DailyTrendResponse(BaseModel):
    records: list[DailyTrendPoint] = Field(..., description="Day-to-day trend records")
    insights: list[DailyTrendInsight] = Field(..., description="Day-to-day insight summaries")


class EnergyData(BaseModel):
    frequency: float = Field(..., description="Grid frequency in Hz")
    state_ui: float = Field(..., description="State UI in MW")
    demand: float = Field(..., description="Current demand in MW")
    thermal: float = Field(..., description="Thermal generation in MW")
    thermal_ipp: float = Field(..., description="Thermal IPP generation in MW")
    hydro: float = Field(..., description="Hydro generation in MW")
    wind: float = Field(..., description="Wind generation in MW")
    solar: float = Field(..., description="Solar generation in MW")
    pavagada_kspdcl: float = Field(..., description="Pavagada KSPDCL in MW")
    bescom: float = Field(..., description="BESCOM in MW")
    hescom: float = Field(..., description="HESCOM in MW")
    gescom: float = Field(..., description="GESCOM in MW")
    cesc: float = Field(..., description="CESC in MW")
    mescom: float = Field(..., description="MESCOM in MW")
    timestamp: datetime = Field(..., description="Time when this API response was produced")
    is_live: bool = Field(..., description="Whether the values came from a live scrape")
    data_source: str = Field(..., description="Origin of the returned values")
    source_timestamp: datetime | None = Field(
        default=None,
        description="Original timestamp of the source values when using cached fallback data",
    )
    analysis: EnergyAnalysis | None = Field(
        default=None,
        description="Derived analytical indicators computed from the current energy sample",
    )
    quality: DataQualityAssessment | None = Field(
        default=None,
        description="Data-quality metadata describing freshness and confidence",
    )


class HistoricalEnergyData(BaseModel):
    id: int = Field(..., description="Database record identifier")
    timestamp: datetime = Field(..., description="Time when the record was stored")
    frequency: float = Field(..., description="Grid frequency in Hz")
    state_ui: float = Field(..., description="State UI in MW")
    demand: float = Field(..., description="Current demand in MW")
    thermal: float = Field(..., description="Thermal generation in MW")
    thermal_ipp: float = Field(..., description="Thermal IPP generation in MW")
    hydro: float = Field(..., description="Hydro generation in MW")
    wind: float = Field(..., description="Wind generation in MW")
    solar: float = Field(..., description="Solar generation in MW")
    pavagada_kspdcl: float = Field(..., description="Pavagada KSPDCL in MW")
    bescom: float = Field(..., description="BESCOM in MW")
    hescom: float = Field(..., description="HESCOM in MW")
    gescom: float = Field(..., description="GESCOM in MW")
    cesc: float = Field(..., description="CESC in MW")
    mescom: float = Field(..., description="MESCOM in MW")
