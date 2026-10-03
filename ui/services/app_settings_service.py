from core.app_settings import load_app_settings, save_app_settings
from core.models import AppSettings


def get_app_settings() -> AppSettings:
    """Returns the persisted app settings (or defaults if none saved)."""
    return load_app_settings()


def update_app_settings(settings: AppSettings) -> None:
    """Persists updated app settings to disk."""
    save_app_settings(settings)