from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


ROME_TIMEZONE = ZoneInfo("Europe/Rome")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_rome() -> datetime:
    return datetime.now(ROME_TIMEZONE)


def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Il datetime da convertire in UTC deve avere timezone esplicita.")

    return value.astimezone(timezone.utc)


def rome_day_bounds_utc(reference_time: datetime | None = None) -> tuple[datetime, datetime]:
    local_reference = (reference_time or now_utc()).astimezone(ROME_TIMEZONE)
    start_local = datetime.combine(local_reference.date(), time.min, tzinfo=ROME_TIMEZONE)
    end_local = start_local + timedelta(days=1)
    return to_utc(start_local), to_utc(end_local)


def rome_shift_window_utc(target_date: date, start_hour: int, end_hour: int) -> tuple[datetime, datetime]:
    start_local = datetime.combine(target_date, time(hour=start_hour), tzinfo=ROME_TIMEZONE)
    end_local = datetime.combine(target_date, time(hour=end_hour), tzinfo=ROME_TIMEZONE)
    return to_utc(start_local), to_utc(end_local)
