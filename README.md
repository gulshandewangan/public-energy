# Public Energy and Climate Tracker

Public Energy and Climate Tracker is a FastAPI + React dashboard for monitoring public power-system data with clearer analytical discipline. Instead of only displaying raw values, the app now computes derived indicators for renewable share, reserve margin, supply-demand gap, frequency deviation, source freshness, and confidence.

## What Makes This Version More Rigorous

- Separates observed values from derived analytical indicators.
- Exposes data-quality metadata so viewers can see whether a sample is live, cached, or simulated.
- Makes key assumptions explicit in the UI and documentation.
- Persists historical samples for short-run trend inspection.
- Includes backend regression tests for live parsing, fallback behavior, and analytical calculations.

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React, Vite, Tailwind CSS, Recharts
- Data collection: HTML scraping pipeline with fallback logic

## Project Structure

```text
Public Energy and Climate Tracker/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   |-- routers/
|   |   |-- services/
|   |   `-- main.py
|   |-- tests/
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- hooks/
|   |   |-- pages/
|   |   `-- styles/
|   `-- package.json
`-- README.md
```

## Key Analytical Definitions

- Total generation = thermal + hydro + wind + solar
- Renewable generation = hydro + wind + solar
- Renewable share = renewable generation / total generation
- Demand gap = total generation - demand
- Reserve margin = demand gap / demand
- Frequency deviation = absolute difference from 50 Hz
- Coverage ratio = total generation / demand

## Data-Quality Logic

- `live`: data came from the active scraper path
- `cached`: live scrape failed, so the API returned the latest stored snapshot
- `simulated`: neither live data nor stored history was available

The confidence score shown in the dashboard is heuristic. It starts from a stronger score for live data and is reduced for fallback data, stale source timestamps, or unusually large reserve-margin gaps. This is intended as a transparency aid, not a formal statistical uncertainty model.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Verification

### Backend tests

```bash
cd backend
.venv\Scripts\python.exe -m unittest discover -s tests
```

### Frontend build

```bash
cd frontend
npm run build
```

## Main Endpoints

- `GET /energy-data`
- `GET /historical-data`
- `GET /api/v1/health`
- `GET /api/v1/metrics`
- `POST /api/v1/metrics/refresh`

## Current Limitations

- The confidence score is rule-based, not statistically estimated.
- Historical analysis is short-window and depends on polling cadence.
- Source coverage is limited by the configured public page structure.
- When no real source is configured, the system necessarily falls back to cached or simulated values.

## Suggested Next Research Upgrades

1. Add a documented source catalog with citation links and scrape assumptions.
2. Introduce scheduled collection for longer historical baselines.
3. Add anomaly detection for sudden demand or frequency excursions.
4. Compare multiple public sources to cross-validate the same interval.
