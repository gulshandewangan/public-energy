from datetime import datetime, timezone


class ScraperService:
    """Temporary scraper stub to be replaced with live public source integrations."""

    def fetch_latest_metrics(self) -> list[dict]:
        captured_at = datetime.now(timezone.utc)
        return [
            {
                "source_name": "Sample SLDC Feed",
                "metric_name": "Current Demand",
                "unit": "MW",
                "value": 12450.0,
                "region": "Karnataka",
                "captured_at": captured_at,
            },
            {
                "source_name": "Sample Renewable Feed",
                "metric_name": "Solar Generation",
                "unit": "MW",
                "value": 3175.0,
                "region": "Karnataka",
                "captured_at": captured_at,
            },
            {
                "source_name": "Sample Renewable Feed",
                "metric_name": "Wind Generation",
                "unit": "MW",
                "value": 1680.0,
                "region": "Karnataka",
                "captured_at": captured_at,
            },
        ]

