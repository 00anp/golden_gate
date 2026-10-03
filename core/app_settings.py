import json
import os
from core.models import AppSettings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "app_settings.json")

DEFAULT_APP_SETTINGS = AppSettings(default_password="Glass2025!")


def _to_dict(settings: AppSettings) -> dict:
    return {
        "default_password": settings.default_password,
    }


def _from_dict(data: dict) -> AppSettings:
    return AppSettings(
        default_password=data.get("default_password", "Glass2025!"),
    )


def load_app_settings() -> AppSettings:
    """Loads app settings from JSON. Falls back to defaults if the file
    is missing, empty, or corrupted."""
    if not os.path.exists(SETTINGS_PATH) or os.path.getsize(SETTINGS_PATH) == 0:
        return AppSettings(default_password="Glass2025!")

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return _from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError):
        return AppSettings(default_password="Glass2025!")


def save_app_settings(settings: AppSettings) -> None:
    """Persists app settings to JSON, creating the data folder if needed."""
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(_to_dict(settings), f, indent=2, ensure_ascii=False)