from core.rules_engine import load_rules
from core.models import SettlementRule, PaymentTier


def get_settlement_rules() -> list[SettlementRule]:
    settlement_rules, _ = load_rules()
    return settlement_rules


def get_payment_tiers() -> list[PaymentTier]:
    _, payment_tiers = load_rules()
    return payment_tiers