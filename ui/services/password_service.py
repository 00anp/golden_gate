import json
import os
from core.models import CompanyPassword


BASE_DIR       = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASSWORDS_PATH = os.path.join(BASE_DIR, "data", "passwords.json")


def _to_dict(cp: CompanyPassword) -> dict:
    return {
        "company": cp.company,
        "password": cp.password,
        "requires_password": cp.requires_password,
        "delivery_method": cp.delivery_method,
    }


def _from_dict(data: dict) -> CompanyPassword:
    return CompanyPassword(
        company=data["company"],
        password=data.get("password", ""),
        requires_password=data.get("requires_password", True),
        delivery_method=data.get("delivery_method", "requires_password"),
    )


def load_passwords() -> list[CompanyPassword]:
    if not os.path.exists(PASSWORDS_PATH):
        return []
    if os.path.getsize(PASSWORDS_PATH) == 0:
        return []
    
    try:
        with open(PASSWORDS_PATH, "r", encoding="utf-8") as f:
            data: list[dict] = json.load(f)
            return [_from_dict(i) for i in data]
    except (json.JSONDecodeError, KeyError):
        return []


def save_passwords(passwords: list[CompanyPassword]) -> None:
    os.makedirs(os.path.dirname(PASSWORDS_PATH), exist_ok=True)

    with open(PASSWORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(
            [_to_dict(cp) for cp in passwords],
            f,
            indent= 2,
            ensure_ascii= False,
        )


def get_passwords_dict(passwords: list[CompanyPassword]) -> dict[str, CompanyPassword]:
    return {cp.company: cp for cp in passwords}