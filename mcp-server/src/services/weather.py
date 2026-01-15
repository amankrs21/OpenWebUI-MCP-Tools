from __future__ import annotations


import urllib3
import requests
from typing import Any, Dict
from dataclasses import dataclass, field

# local imports
from src.config import config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class WeatherService:

    def _build_params(self, city: str) -> Dict[str, Any]:
        return {
            "q": city,
            "appid": config.weather_api_key,
            "units": config.default_weather_units,
        }

    def _format_weather(self, payload: Dict[str, Any]) -> str:
        main = payload.get("main", {})
        weather = (payload.get("weather") or [{}])[0]
        wind = payload.get("wind", {})
        description = weather.get("description", "No description")
        city = payload.get("name", "Unknown location")
        temp = main.get("temp")
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")
        speed = wind.get("speed")

        pieces = [f"Weather for {city}: {description}."]
        if temp is not None:
            pieces.append(f"Temperature {temp}°C (feels like {feels_like}°C).")
        if humidity is not None:
            pieces.append(f"Humidity {humidity}%.")
        if speed is not None:
            pieces.append(f"Wind {speed} m/s.")
        return " ".join(pieces)

    def get_weather(self, city: str) -> Dict[str, Any]:
        if not city:
            return {"status": "error", "message": "Please provide a city name."}

        if not config.weather_api_key:
            return {
                "status": "error",
                "message": (
                    "OPENWEATHERMAP_API_KEY missing. Set it in your environment "
                    "to enable weather queries."
                ),
            }

        try:
            response = requests.get(
                config.weather_api_url,
                params=self._build_params(city),
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("cod") == 404:
                return {"status": "error", "message": f"City '{city}' not found."}
        except requests.exceptions.SSLError as exc:  # type: ignore[attr-defined]
            return {
                "status": "error",
                "message": (
                    "Weather API SSL error. If you trust the endpoint, set "
                    "WEATHER_VERIFY_SSL=false or provide WEATHER_CA_BUNDLE. Details: "
                    f"{exc}"
                ),
            }
        except requests.HTTPError as exc:
            return {
                "status": "error",
                "message": f"Weather API error: {exc.response.status_code if exc.response else exc}",
            }
        except requests.RequestException as exc:
            return {"status": "error", "message": f"Weather API unreachable: {exc}"}

        return {
            "status": "ok",
            "summary": self._format_weather(payload),
            "raw": payload,
        }
