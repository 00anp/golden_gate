from core.filter_settings import load_filter_settings, save_filter_settings
from core.models import FilterSettings


def get_filter_settings() -> FilterSettings:
    """Returns the persisted filter settings (or defaults if none saved)."""
    return load_filter_settings()


def update_filter_settings(settings: FilterSettings) -> None:
    """Persists updated filter settings to disk."""
    save_filter_settings(settings)