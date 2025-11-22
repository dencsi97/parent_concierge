from pathlib import Path

from parent_concierge.tools import baby_profile_store


def test_get_profile_initially_empty(tmp_path):
    # Redirect PROFILE_FILE to a temp file so we don't touch real data
    test_file: Path = tmp_path / "profiles.json"
    baby_profile_store.PROFILE_FILE = test_file

    # Initially, file should be auto-created and no profile should exist
    result = baby_profile_store.get_profile()

    assert "exists" in result
    assert "profile" in result
    assert result["exists"] is False
    assert result["profile"] is None

    # And the underlying file should now exist
    assert test_file.exists()


def test_save_and_get_profile(tmp_path):
    # Redirect PROFILE_FILE again for this test
    test_file: Path = tmp_path / "profiles.json"
    baby_profile_store.PROFILE_FILE = test_file

    parent_name = "Stephen"
    baby_name = "Leo"
    dob_str = "2024-08-01"
    feeding_type = "bottle"
    country = "UK"

    # Save the profile via the tool-style function
    save_result = baby_profile_store.save_profile(
        parent_name=parent_name,
        baby_name=baby_name,
        date_of_birth=dob_str,
        feeding_type=feeding_type,
        country=country,
    )

    assert isinstance(save_result, dict)
    assert save_result.get("status") == "success"
    assert test_file.exists()

    # Now fetch it back
    result = baby_profile_store.get_profile()

    assert result["exists"] is True
    profile = result["profile"]
    assert profile is not None

    assert profile["parent_name"] == parent_name
    assert profile["baby_name"] == baby_name
    assert profile["date_of_birth"] == dob_str
    assert profile["feeding_type"] == feeding_type
    assert profile["country"] == country
