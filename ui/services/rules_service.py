from core.rules_engine import load_rules, save_rules
from core.models import SettlementRule, PaymentTier


def get_settlement_rules() -> list[SettlementRule]:
    settlement_rules, _ = load_rules()
    return settlement_rules


def get_payment_tiers() -> list[PaymentTier]:
    _, payment_tiers = load_rules()
    return payment_tiers


# Settlement rules CRUD
def add_settlement_rule(rule: SettlementRule) -> None:
    rules, tiers = load_rules()
    rules.append(rule)
    save_rules(rules, tiers)


def update_settlement_rule(updated_rule: SettlementRule) -> None:
    rules, tiers = load_rules()
    for i, rule in enumerate(rules):
        if rule.prefix == updated_rule.prefix:
            rules[i] = updated_rule
            break
    save_rules(rules, tiers)


def delete_settlement_rule(prefix: str) -> None:
    rules, tiers = load_rules()
    rules = [r for r in rules if r.prefix != prefix]
    save_rules(rules, tiers)


# Payment tiers CRUD
def add_payment_tier(tier: PaymentTier) -> None:
    rules, tiers = load_rules()
    tiers.append(tier)
    tiers.sort(key=lambda t: t.min_settlement)
    save_rules(rules, tiers)


def update_payment_tier(index: int, updated_tier: PaymentTier) -> None:
    rules, tiers = load_rules()
    if 0 <= index < len(tiers):
        tiers[index] = updated_tier
    tiers.sort(key=lambda t: t.min_settlement)
    save_rules(rules, tiers)


def delete_payment_tier(index: int) -> None:
    rules, tiers = load_rules()
    if 0 <= index < len(tiers):
        tiers.pop(index)
    save_rules(rules, tiers)