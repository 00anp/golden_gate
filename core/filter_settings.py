import json
import os
from core.models import FilterSettings


BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "filter_settings.json")

DEFAULT_LOW_BALANCE_THRESHOLD = 100.0


def _to_dict(settings: FilterSettings) -> dict:
    return {
        "low_balance_threshold": settings.low_balance_threshold,
    }


def _from_dict(data: dict) -> FilterSettings:
    return FilterSettings(
        low_balance_threshold=float(data.get("low_balance_threshold", DEFAULT_LOW_BALANCE_THRESHOLD)),
    )


def load_filter_settings() -> FilterSettings:
    """Loads filter settings from JSON. Falls back to defaults if the file
    is missing, empty, or corrupted."""
    if not os.path.exists(SETTINGS_PATH) or os.path.getsize(SETTINGS_PATH) == 0:
        return FilterSettings(low_balance_threshold=DEFAULT_LOW_BALANCE_THRESHOLD)

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return _from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError):
        return FilterSettings(low_balance_threshold=DEFAULT_LOW_BALANCE_THRESHOLD)


def save_filter_settings(settings: FilterSettings) -> None:
    """Persists filter settings to JSON, creating the data folder if needed."""
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(_to_dict(settings), f, indent=2, ensure_ascii=False)