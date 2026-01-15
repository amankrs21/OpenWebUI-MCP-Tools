from __future__ import annotations

from functools import lru_cache
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mcp_port: int = 8765
    mcp_host: str = "0.0.0.0"

    default_weather_units: str = "metric"
    weather_api_key: str = "your_api_key_here"
    weather_api_url: str = "https://api.openweathermap.org/data/2.5/weather"

    default_timezone: str = "UTC"


@lru_cache
def get_settings() -> Settings:
    return Settings()

config = get_settings()
