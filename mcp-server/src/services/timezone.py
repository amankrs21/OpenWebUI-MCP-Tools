from __future__ import annotations

from typing import Any, Dict
from zoneinfo import ZoneInfo
from dataclasses import dataclass
from datetime import datetime, timezone

# local imports
from src.config import config


@dataclass
class TimeService:

    def get_time(self, tz_name: str | None = None) -> Dict[str, Any]:
        tz_name = tz_name.upper() if tz_name else config.default_timezone
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            return {
                "status": "error",
                "message": f"Unknown timezone '{tz_name}'.",
            }

        now = datetime.now(tz=tz)
        utc_now = now.astimezone(timezone.utc)
        return {
            "status": "ok",
            "timezone": tz_name,
            "datetime_iso": now.isoformat(),
            "date": now.date().isoformat(),
            "time": now.strftime("%H:%M:%S"),
            "utc_offset": now.strftime("%z"),
            "unix": int(now.timestamp()),
            "utc_datetime_iso": utc_now.isoformat(),
        }
