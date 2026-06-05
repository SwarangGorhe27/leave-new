"""Shared query/body parsers for attendance APIs."""

from __future__ import annotations

from datetime import date, datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_datetime


def parse_query_date(value: str) -> date:
    """Parse YYYY-MM-DD."""
    return date.fromisoformat(value.strip()[:10])


def parse_query_datetime(value: str, *, end_of_day: bool = False) -> datetime:
    """
    Parse ISO date or datetime from query params.
    Supports trailing Z (UTC) which datetime.fromisoformat rejects on Python 3.10.
    """
    raw = (value or "").strip()
    if not raw:
        raise ValueError("Empty datetime value")

    if "T" in raw or " " in raw:
        normalized = raw.replace("Z", "+00:00")
        dt = parse_datetime(normalized)
        if dt is None:
            raise ValueError(f"Invalid datetime: {value}")
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt

    d = parse_query_date(raw)
    if end_of_day:
        dt = datetime.combine(d, time(23, 59, 59))
    else:
        dt = datetime.combine(d, time.min)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt
