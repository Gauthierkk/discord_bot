"""
Input validation utilities
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple

from config import MAX_DAYS_LOOKBACK, MAX_HOURS_LOOKBACK


def normalize_time_unit(unit: str) -> str:
    """
    Normalize time unit to lowercase and plural form

    Args:
        unit: Time unit string (e.g., 'Hours', 'day', 'DAYS')

    Returns:
        Normalized unit string ('hours' or 'days')
    """
    if not unit:
        return "days"

    normalized = unit.lower().strip()

    # Handle singular forms
    if normalized == "hour":
        return "hours"
    elif normalized == "day":
        return "days"

    return normalized


def validate_timeframe(timeframe: int, unit: str) -> Tuple[bool, str]:
    """
    Validate timeframe input for commands

    Args:
        timeframe: Number of hours or days
        unit: 'hours' or 'days' (case-insensitive, accepts singular/plural)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Normalize the unit
    unit = normalize_time_unit(unit)

    if unit == "days":
        if timeframe < 1 or timeframe > MAX_DAYS_LOOKBACK:
            return False, f"Timeframe must be between 1 and {MAX_DAYS_LOOKBACK} days!"
    elif unit == "hours":
        if timeframe < 1 or timeframe > MAX_HOURS_LOOKBACK:
            return (
                False,
                f"Timeframe must be between 1 and {MAX_HOURS_LOOKBACK} hours ({MAX_DAYS_LOOKBACK} days)!",
            )
    else:
        return False, "Invalid time unit! Must be 'hours' or 'days'."

    return True, ""


def calculate_time_window(timeframe: int, unit: str) -> Tuple[datetime, str]:
    """
    Calculate the start time and description for a time window

    Args:
        timeframe: Number of hours or days
        unit: 'hours' or 'days' (case-insensitive, accepts singular/plural)

    Returns:
        Tuple of (start_datetime, description)
    """
    # Normalize the unit
    unit = normalize_time_unit(unit)

    now = datetime.now(timezone.utc)

    if unit == "days":
        time_start = now - timedelta(days=timeframe)
        time_desc = f"past {timeframe} day{'s' if timeframe > 1 else ''}"
    else:  # hours
        time_start = now - timedelta(hours=timeframe)
        time_desc = f"past {timeframe} hour{'s' if timeframe > 1 else ''}"

    return time_start, time_desc
