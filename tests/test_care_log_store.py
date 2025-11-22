from datetime import datetime, timedelta, date
from pathlib import Path

from parent_concierge.tools import care_log_store


def test_add_and_get_logs_for_day(tmp_path):
    # Redirect the log file to a temp location for this test
    test_file: Path = tmp_path / "care_logs.json"
    care_log_store.CARE_LOG_FILE = test_file

    today = date.today()
    yesterday = today - timedelta(days=1)

    # Build ISO strings
    today_str = today.isoformat()  # e.g. "2025-11-19"

    event_today_ts = datetime(today.year, today.month, today.day, 7, 10).isoformat()
    event_yesterday_ts = datetime(
        yesterday.year, yesterday.month, yesterday.day, 22, 0
    ).isoformat()

    # Add events using the tool-style API
    res1 = care_log_store.add_log(
        event_type="feed",
        timestamp=event_today_ts,
        volume_ml=90,
        duration_minutes=None,
        notes="Bottle feed",
    )
    res2 = care_log_store.add_log(
        event_type="nap",
        timestamp=event_yesterday_ts,
        volume_ml=None,
        duration_minutes=45,
        notes="Evening nap",
    )

    assert res1.get("status") == "success"
    assert res2.get("status") == "success"
    assert test_file.exists()

    # Now fetch only today's logs
    logs_today = care_log_store.get_logs_for_day(today_str)

    assert isinstance(logs_today, list)
    assert len(logs_today) == 1

    only_event = logs_today[0]
    assert only_event["event_type"] == "feed"
    assert only_event["volume_ml"] == 90
    assert only_event["notes"] == "Bottle feed"
