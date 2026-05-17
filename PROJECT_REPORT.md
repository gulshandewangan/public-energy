# Project Report

## Public Energy and Climate Tracker

Prepared on: 2026-05-07

## 1. Executive Summary

Public Energy and Climate Tracker is a full-stack web application designed to collect, process, preserve, and present public electricity-system data in a more structured and transparent way. The project focuses on live grid information published through the Karnataka power-system portal and transforms those raw values into an interactive dashboard with clearer interpretation, historical storage, day-to-day comparison, and explanatory insight panels.

The system combines a FastAPI backend, a React frontend, a SQLite persistence layer, and an Excel-backed daily archive. It supports live scraping from the KPTCL/SLDC website, fallback behavior when the source is unavailable, short-term trend inspection, daily comparison charts, and clearly separated display cards for generation, interchange, and ESCOM/distribution values.

## 2. Problem Statement

Public power dashboards often expose raw values without sufficient context. Users can see figures such as demand, frequency, or thermal generation, but it is difficult to:

- distinguish observed values from interpreted metrics
- compare current data with previous days
- preserve historical data for reporting
- understand freshness and source reliability
- inspect distribution-wise values in one place

This project addresses those gaps by building a dashboard that is more analytical than decorative.

## 3. Project Objectives

The main objectives of the project were:

- collect live public electricity data from the KPTCL/SLDC website
- present the data in a structured and readable dashboard
- separate `Thermal` and `Thermal IPP` values correctly
- expose additional live fields such as `State UI`, `Pavagada KSPDCL`, `BESCOM`, `HESCOM`, `GESCOM`, `CESC`, and `MESCOM`
- preserve short-run history in SQLite for charting
- preserve day-level history in Excel for daily trend comparison
- generate analytical summaries such as renewable share, reserve margin, and demand gap
- provide a resilient fallback path when the live source is unavailable

## 4. Scope of the Project

The current scope includes:

- live scraping of the configured public source URL
- API-based delivery of processed energy data
- modern dashboard visualizations for current, historical, and daily comparison views
- short-term persistence in SQLite
- day-level archival in Excel
- backend test coverage for parser behavior and service logic

The current scope does not include:

- multi-source validation across several power portals
- long-term scheduled ingestion infrastructure
- user authentication or role-based access
- predictive analytics or anomaly detection models

## 5. Technology Stack

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- Requests
- BeautifulSoup4
- Pydantic

### Frontend

- React
- Vite
- Tailwind CSS
- Recharts
- Axios

### Data Storage

- SQLite database for sampled records and fallback history
- Excel workbook for daily trend storage and day-to-day reporting

## 6. System Architecture

The project follows a client-server architecture.

### Backend responsibilities

- scrape and parse live data from the public source
- clean and normalize extracted values
- expose API endpoints
- compute derived analytical indicators
- store recent records in SQLite
- store daily snapshots in an Excel workbook
- return fallback data when live scraping fails

### Frontend responsibilities

- fetch API data from the backend
- render live stat cards
- render short-run charts and day-to-day charts
- display derived insights and explanatory notes
- show system status and source freshness information

## 7. Key Modules

### 7.1 Scraper Module

The scraper is implemented in [energy_scraper_service.py](C:/projects/Public%20Energy%20%26%20Climate%20Tracker/backend/app/services/energy_scraper_service.py).  
It extracts:

- frequency
- state UI
- demand
- thermal
- thermal IPP
- hydro
- wind
- solar
- Pavagada KSPDCL
- BESCOM
- HESCOM
- GESCOM
- CESC
- MESCOM

It supports both selector-based extraction for the KPTCL homepage and alias-based text extraction for combined rows such as:

- `FREQUENCY : 50.08 STATE UI : 172`
- `HESCOM :3073 GESCOM : 1345`
- `CESC :1889 MESCOM :1521`

### 7.2 Data Service Layer

The business logic is implemented in [energy_data_service.py](C:/projects/Public%20Energy%20%26%20Climate%20Tracker/backend/app/services/energy_data_service.py).

It is responsible for:

- fetching the latest live sample
- applying fallback logic when scraping fails
- computing derived indicators
- storing records in SQLite
- storing daily live snapshots in Excel
- preparing historical and daily trend responses for the frontend

### 7.3 Daily Excel Archive

An Excel-backed daily archive is implemented through:

- [daily_trend_excel_service.py](C:/projects/Public%20Energy%20%26%20Climate%20Tracker/backend/app/services/daily_trend_excel_service.py)
- [daily_trend_excel_helper.py](C:/projects/Public%20Energy%20%26%20Climate%20Tracker/backend/scripts/daily_trend_excel_helper.py)

This archive stores one row per day and updates that row with the latest live sample for that day. It supports day-to-day trend comparison without mixing test data or fallback values into the archive.

### 7.4 Frontend Dashboard

The main dashboard page is implemented in [DashboardPage.jsx](C:/projects/Public%20Energy%20%26%20Climate%20Tracker/frontend/src/pages/DashboardPage.jsx) using reusable components.

Important frontend features include:

- live metric cards
- demand-over-time chart
- energy mix chart
- source comparison chart
- short-term trend list
- analytical layer
- daily archive trend chart
- daily insights panel
- methodology and source-freshness notes

## 8. Functional Features Implemented

The project currently supports the following features:

### Live energy display

- live frequency
- live state UI
- live demand
- live thermal
- live thermal IPP
- live hydro
- live wind
- live solar

### Distribution and allocation display

- Pavagada KSPDCL
- BESCOM
- HESCOM
- GESCOM
- CESC
- MESCOM

### Historical monitoring

- storage of recent records in SQLite
- display of recent short-run chart trends
- daily archive stored in Excel
- day-to-day comparison chart across archived days

### Derived analytics

- total generation
- renewable generation
- renewable share
- demand gap
- reserve margin
- frequency deviation
- coverage ratio
- balance state

### Reliability features

- source mode detection (`live`, `cached`, `simulated`)
- source freshness display
- fallback to latest stored snapshot
- simulated fallback when no stored data is available

## 9. API Endpoints

The project exposes the following relevant endpoints:

- `GET /energy-data`
- `GET /historical-data`
- `GET /daily-trends`
- `GET /api/v1/health`
- `GET /api/v1/metrics`
- `POST /api/v1/metrics/refresh`

## 10. Data Flow

The data flow of the project is as follows:

1. The backend requests the configured public source page.
2. The scraper extracts live values from the page.
3. The service computes derived metrics from the extracted values.
4. The latest sample is stored in SQLite.
5. If the sample is truly live, a daily snapshot is written into the Excel archive.
6. The backend exposes the processed result through REST endpoints.
7. The frontend fetches current, historical, and daily-trend data.
8. The dashboard renders current values, analytical summaries, and chart-based comparisons.

## 11. Testing and Verification

The backend contains regression tests in [test_energy_data_service.py](C:/projects/Public%20Energy%20%26%20Climate%20Tracker/backend/tests/test_energy_data_service.py).

The tested scenarios include:

- parsing combined `Frequency` and `State UI` rows
- parsing live thermal and thermal IPP fields correctly
- fallback behavior when live scraping fails
- storing historical records properly

The frontend build was also verified through the Vite production build process.

## 12. Challenges Faced

Several implementation challenges were addressed during development:

- public source pages use mixed layouts and combined labels
- some important values share the same row, requiring alias-aware parsing
- `Thermal` and `Thermal IPP` had to be separated instead of merged
- confidence-related UI elements had to be removed cleanly without breaking the underlying quality logic
- daily chart data initially became misleading when test data polluted the archive
- Excel support required a helper flow using the bundled spreadsheet runtime

## 13. Improvements Made During Development

The project was refined through multiple corrections and enhancements:

- separated `Thermal` and `Thermal IPP` values correctly
- added `State UI` as a proper live metric
- added Pavagada and ESCOM-wise live values
- removed confidence score visibility from the dashboard UI
- added an Excel-backed daily trend archive
- added a daily comparison chart with insight cards
- prevented non-live fallback data from contaminating the daily archive
- isolated test behavior from the real daily trend workbook

## 14. Current Limitations

The current version still has some limitations:

- daily trend quality depends on regular day-by-day live collection
- only one public source is currently used
- the parser is still sensitive to major source-page structural changes
- the Excel archive is designed for lightweight project reporting, not enterprise-scale warehousing
- the dashboard emphasizes comparison and interpretation, but not forecasting

## 15. Future Enhancements

The project can be extended in several useful directions:

- scheduled automatic daily collection with a task runner or cron job
- multi-day filters such as 7-day, 30-day, and monthly trend views
- exportable PDF or DOCX reports
- anomaly detection for sudden demand or frequency changes
- comparison against additional state or national public data sources
- stronger source citation and metadata tracking
- advanced charts for ESCOM-wise daily allocation trends

## 16. Conclusion

Public Energy and Climate Tracker demonstrates how a public-data dashboard can move beyond simple display into a more disciplined measurement tool. By combining live scraping, structured APIs, historical persistence, Excel-backed day archives, and readable analytical views, the project provides a practical platform for monitoring public electricity data with greater transparency.

The project succeeds in converting raw values into a more useful reporting system while remaining lightweight, testable, and extensible. It is well suited for academic demonstration, project submission, and future expansion into a broader public-energy analytics platform.
