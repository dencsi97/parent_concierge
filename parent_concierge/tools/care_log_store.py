import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date as date_cls

CARE_LOG_FILE = Path("data/care_logs.json")


def _ensure_file_exists() -> None:
    """Create the JSON file if it doesn't exist."""
    if not CARE_LOG_FILE.exists():
        CARE_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CARE_LOG_FILE.write_text("[]", encoding="utf-8")


def add_log(
    event_type: str,
    timestamp: str,
    volume_ml: Optional[int] = None,
    duration_minutes: Optional[int] = None,
    notes: Optional[str] = None,
) -> Dict[str, str]:
    """
    Append a care event to the log file.

    Args:
        event_type: One of "feed", "nap", "diaper" (not enforced here).
        timestamp: ISO datetime string, e.g. "2025-11-19T07:10:00".
        volume_ml: Optional, for feeds.
        duration_minutes: Optional, for naps.
        notes: Optional free-text notes.

    Returns:
        { "status": "success" }
    """
    _ensure_file_exists()
    raw = json.loads(CARE_LOG_FILE.read_text(encoding="utf-8"))

    if not isinstance(raw, list):
        # In case file is corrupted / manually edited
        raw = []

    event: Dict[str, Any] = {
        "event_type": event_type,
        "timestamp": timestamp,
        "volume_ml": volume_ml,
        "duration_minutes": duration_minutes,
        "notes": notes,
    }

    raw.append(event)

    CARE_LOG_FILE.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {"status": "success"}


def get_logs_for_day(day: str) -> List[Dict[str, Any]]:
    """
    Return all care events whose timestamp.date() == the given day.

    Args:
        day: ISO date string, e.g. "2025-11-19".

    Returns:
        List of dicts, each with keys:
        - event_type
        - timestamp
        - volume_ml
        - duration_minutes
        - notes
    """
    _ensure_file_exists()
    raw = json.loads(CARE_LOG_FILE.read_text(encoding="utf-8"))

    try:
        target_date = date_cls.fromisoformat(day)
    except ValueError:
        # If date is bad, just return no events
        return []

    events: List[Dict[str, Any]] = []

    for item in raw:
        ts_str = item.get("timestamp")
        if not ts_str:
            continue

        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            # Skip bad timestamps
            continue

        if ts.date() == target_date:
            events.append(item)

    return events
