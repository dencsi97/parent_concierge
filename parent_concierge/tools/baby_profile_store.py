import json
from pathlib import Path
from typing import Dict, Any

PROFILE_FILE = Path("data/profiles.json")


def _ensure_file_exists() -> None:
    """Create the JSON file if it doesn't exist."""
    if not PROFILE_FILE.exists():
        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROFILE_FILE.write_text("{}", encoding="utf-8")


def get_profile() -> Dict[str, Any]:
    """
    Tool-friendly getter.

    Returns:
        {
          "exists": bool,
          "profile": {
            "parent_name": str,
            "baby_name": str,
            "date_of_birth": str (ISO),
            "feeding_type": str,
            "country": str
          } | None
        }
    """
    _ensure_file_exists()
    raw = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))

    if "profile" not in raw:
        return {"exists": False, "profile": None}

    return {
        "exists": True,
        "profile": raw["profile"],
    }


def save_profile(
    parent_name: str,
    baby_name: str,
    date_of_birth: str,
    feeding_type: str,
    country: str,
) -> Dict[str, str]:
    """
    Tool-friendly setter.

    Args:
        parent_name: Parent's name/User's name.
        baby_name: Baby's name.
        date_of_birth: ISO date string, e.g. "2024-08-01".
        feeding_type: "breast", "bottle", or "mixed".
        country: Country code/name.

    Returns:
        { "status": "success" }
    """
    _ensure_file_exists()

    profile_dict = {
        "parent_name": parent_name,
        "baby_name": baby_name,
        "date_of_birth": date_of_birth,
        "feeding_type": feeding_type,
        "country": country,
    }

    data = {"profile": profile_dict}

    PROFILE_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {"status": "success"}
