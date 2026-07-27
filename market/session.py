from __future__ import annotations
import pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime, time
from config.settings import SETTINGS

def to_new_york(ts) -> pd.Timestamp:
    value = pd.Timestamp(ts)
    if value.tzinfo is None:
        value = value.tz_localize(ZoneInfo(SETTINGS.market_timezone))
    else:
        value = value.tz_convert(ZoneInfo(SETTINGS.market_timezone))
    return value

def opening_shield_active(last_timestamp, now: datetime | None=None) -> bool:
    last = to_new_york(last_timestamp)
    current = now.astimezone(ZoneInfo(SETTINGS.market_timezone)) if now else datetime.now(ZoneInfo(SETTINGS.market_timezone))
    if last.date() != current.date():
        return False
    start = time(9, 30)
    end_minutes = 9 * 60 + 30 + SETTINGS.opening_shield_minutes
    last_minutes = last.hour * 60 + last.minute
    return start <= last.time() and last_minutes < end_minutes
