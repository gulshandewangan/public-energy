from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def initialize_database() -> None:
    from app.models.energy_metric import EnergyMetric  # noqa: F401
    from app.models.energy_record import EnergyDataRecord  # noqa: F401
    from app.models.energy_snapshot import EnergySnapshot  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_energy_table_columns()


def _ensure_energy_table_columns() -> None:
    inspector = inspect(engine)
    required_columns = {
        "energy_data_records": {
            "thermal_ipp",
            "state_ui",
            "pavagada_kspdcl",
            "bescom",
            "hescom",
            "gescom",
            "cesc",
            "mescom",
        },
        "energy_snapshots": {
            "thermal_ipp",
            "state_ui",
            "pavagada_kspdcl",
            "bescom",
            "hescom",
            "gescom",
            "cesc",
            "mescom",
        },
    }

    with engine.begin() as connection:
        for table_name, columns in required_columns.items():
            existing_columns = {
                column_info["name"] for column_info in inspector.get_columns(table_name)
            }
            for column_name in columns - existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"ADD COLUMN {column_name} FLOAT NOT NULL DEFAULT 0"
                    )
                )


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
