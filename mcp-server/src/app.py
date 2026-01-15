from __future__ import annotations

from mcp.server.fastmcp import FastMCP

# local imports
from src.config import config
from src.services.scrape import ScrapeService
from src.services.timezone import TimeService
from src.services.wiki import WikipediaService
from src.services.weather import WeatherService


mcp = FastMCP("openwebui-tools", host=config.mcp_host, port=config.mcp_port)


@mcp.tool()
def weather(city: str) -> dict:
    """Get current weather for a city using OpenWeatherMap."""
    return WeatherService().get_weather(city)

@mcp.tool()
def time_now(timezone: str | None = None) -> dict:
    """Get current date/time for a timezone (like UTC, CET...)."""
    return TimeService().get_time(timezone)

@mcp.tool()
def wikipedia_summary(query: str, sentences: int = 5, lang: str = "en") -> dict:
    """Get a short Wikipedia summary for fact checking."""
    return WikipediaService().summary(query=query, sentences=sentences, lang=lang)

@mcp.tool()
async def web_scrape(
    url: str,
    css: str | None = None,
    xpath: str | None = None,
    method: str = "quick",
    wait_for: str | None = None,
) -> dict | list[str]:
    """Scrape a URL. method: quick | robust | impersonate."""
    service = ScrapeService()
    method = method.lower().strip()

    if method == "quick":
        return await service.quick_scrape(url, css=css, xpath=xpath)
    if method == "robust":
        return await service.robust_scrape(url, wait_for=wait_for)
    if method == "impersonate":
        return service.impersonate_scrape(url)

    return {"status": "error", "message": f"Unknown method '{method}'."}

