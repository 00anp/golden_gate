import json
import os
from datetime import datetime

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HISTORY_PATH  = os.path.join(BASE_DIR, "data", "history.json")


def save_history_entry(
    files_created:    int,
    companies_found:  list[str],
    duration_seconds: float,
    rules_applied: dict[str, int],
) -> None:

    entries: list[dict] = _load_raw()

    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files_created": files_created,
        "companies_found": companies_found,
        "duration_seconds": round(duration_seconds, 0),
        "rules_applied": rules_applied,
    }

    entries.insert(0, new_entry)

    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def load_history() -> list[dict]:
    return _load_raw()


def _load_raw() -> list[dict]:
    if not os.path.exists(HISTORY_PATH):
        return []
    if os.path.getsize(HISTORY_PATH) == 0:
        return []
    try:
        with open(HISTORY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []