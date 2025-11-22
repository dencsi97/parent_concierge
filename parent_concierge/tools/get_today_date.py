from datetime import date

def get_today_date() -> str:
    """
    Return today's date as an ISO string.

    This tool provides a reliable, deterministic way for agents to know
    the current day (e.g. "2025-11-21").

    Returns:
        str: Today's date in ISO format, YYYY-MM-DD.
              Example: "2025-11-21"
    """
    return date.today().isoformat()
