from datetime import datetime

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class EnergySnapshot(Base):
    __tablename__ = "energy_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    frequency: Mapped[float] = mapped_column(Float, nullable=False)
    state_ui: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    demand: Mapped[float] = mapped_column(Float, nullable=False)
    thermal: Mapped[float] = mapped_column(Float, nullable=False)
    thermal_ipp: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hydro: Mapped[float] = mapped_column(Float, nullable=False)
    wind: Mapped[float] = mapped_column(Float, nullable=False)
    solar: Mapped[float] = mapped_column(Float, nullable=False)
    pavagada_kspdcl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bescom: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hescom: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gescom: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cesc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    mescom: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
