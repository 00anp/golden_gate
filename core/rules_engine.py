import json
import os
from core.models import SettlementRule, PaymentTier


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, "data", "rules.json")

DEFAULT_SETTLEMENT_RULES: list[SettlementRule] = [
    SettlementRule("VIL",  5000, 0.45, 0.40, 0.50, 0.45, review_column=32, mark_am=True, value_to_review="PRELIT", description="VIL — threshold $5,000"),
    SettlementRule("CKS",  5000, 0.45, 0.40, 0.50, 0.45, review_column=32, mark_am=True, value_to_review="PRELIT", description="CKS — threshold $5,000"),
    SettlementRule("FFAM", 5000, 0.45, 0.40, 0.50, 0.45, z_greater_than_threshold=True, description="FFAM — only applies if Z > 0.45"),
    SettlementRule("OLU",  5000, 0.45, 0.40, 0.50, 0.45, description="OLU — threshold $5,000"),
    SettlementRule("OLI",  5000, 0.45, 0.40, 0.50, 0.45, description="OLI — threshold $5,000"),
    SettlementRule("CAG",  5000, 0.45, 0.40, 0.50, 0.45, description="CAG — threshold $5,000"),
    SettlementRule("LPL",  0,    0.45, 0.45, 0.45, 0.45, mark_aq=True, description="LPL — fixed rate, mark AQ"),
    SettlementRule("GAM",  1250, 0.45, 0.40, 0.50, 0.45, z_lower_than_threshold=True, description="GAM — threshold $1,250"),
    SettlementRule("SMF",  0,    0.50, 0.45, 0.50, 0.45, z_lower_than_threshold=True, description="SMF — fixed rate Z=0.50"),
    SettlementRule("SCS",  1250, 0.45, 0.40, 0.50, 0.45, description="SCS — threshold $1,250"),
    SettlementRule("RSG",  0,    0.60, 0.55, 0.60, 0.55, mark_am=True, description="RSG — mark AM, Z=0.60"),
    SettlementRule("NDH",  0,    0,    0,    0,    0,    copy_z_to_ak=True, description="NDH — copy Z to AK"),
    SettlementRule("GSG",  0,    0,    0,    0,    0,    copy_z_to_ak=True, description="GSG — copy Z to AK"),
    SettlementRule("CAV",  0,    0,    0,    0,    0,    review_column=19, mark_am=True, value_to_review="7GMC01", copy_z_to_ak=True, description="CAV — mark AM if 7GMC01, else copy Z to AK"),
    SettlementRule("CAQ",  0,    0,    0,    0,    0,    copy_z_to_ak=True, description="CAQ — copy Z to AK"),
    SettlementRule("CSF",  0,    0,    0,    0,    0,    copy_z_to_ak=True, description="CSF — copy Z to AK"),
]

DEFAULT_PAYMENT_TIERS: list[PaymentTier] = [
    PaymentTier(0,        999.99,   50,  6,  12),
    PaymentTier(1000,     2500,     50,  12, 12),
    PaymentTier(2500.01,  5000,     50,  18, 24),
    PaymentTier(5000.01,  7500,     75,  24, 24),
    PaymentTier(7500.01,  10000,    100, 30, 24),
    PaymentTier(10000.01, 15000,    125, 36, 24),
    PaymentTier(15000.01, 25000,    200, 36, 24),
    PaymentTier(25000.01, float("inf"), 250, 36, 24),
]


def _rule_to_dict(rule: SettlementRule) -> dict:
    return {
        "prefix": rule.prefix,
        "balance_threshold": rule.balance_threshold,
        "z_high": rule.z_high,
        "ak_high": rule.ak_high,
        "z_low": rule.z_low,
        "ak_low": rule.ak_low,
        "mark_am": rule.mark_am,
        "mark_aq": rule.mark_aq,
        "copy_z_to_ak": rule.copy_z_to_ak,
        "description": rule.description,
    }


def _dict_to_rule(rule: dict) -> SettlementRule:
    return SettlementRule(
        prefix=rule["prefix"],
        balance_threshold=rule["balance_threshold"],
        z_high=rule["z_high"],
        ak_high=rule["ak_high"],
        z_low=rule["z_low"],
        ak_low=rule["ak_low"],
        mark_am=rule.get("mark_am", False),
        mark_aq=rule.get("mark_aq", False),
        copy_z_to_ak=rule.get("copy_z_to_ak", False),
        description=rule.get("description", ""),
    )

def _tier_to_dict(tier: PaymentTier) -> dict:
    return {
        "min_settlement": tier.min_settlement,
        "max_settlement": tier.max_settlement if tier.max_settlement != float("inf") else "inf",
        "min_payment": tier.min_payment,
        "max_term_default": tier.max_term_default,
        "max_term_lpl": tier.max_term_lpl,
    }

def _dict_to_tier(tier: dict) -> PaymentTier:
    max_settlement = float("inf") if tier["max_settlement"] == "inf" else tier["max_settlement"]
    return PaymentTier(
        min_settlement=tier["min_settlement"],
        max_settlement=max_settlement,
        min_payment=tier["min_payment"],
        max_term_default=tier["max_term_default"],
        max_term_lpl=tier["max_term_lpl"],
    )


def load_rules()->tuple[list[SettlementRule], list[PaymentTier]]:
    """Loads rules from JSON. If they don't exist, uses default and saves."""
    if not os.path.exists(RULES_PATH) or os.path.getsize(RULES_PATH) == 0:
        return (list(DEFAULT_SETTLEMENT_RULES), list(DEFAULT_PAYMENT_TIERS))

    try:
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            settlement_rules:list = [_dict_to_rule(rule) for rule in data.get("settlement_rules", [])]
            payment_tiers:list = [_dict_to_tier(tier) for tier in data.get("payment_tiers", [])]

            if not settlement_rules:
                settlement_rules = list(DEFAULT_SETTLEMENT_RULES)
            if not payment_tiers:
                payment_tiers = list(DEFAULT_PAYMENT_TIERS)
            
            return(settlement_rules, payment_tiers)
        
    except (json.JSONDecodeError, KeyError):
        
        return (list(DEFAULT_SETTLEMENT_RULES), list(DEFAULT_PAYMENT_TIERS))
    

def save_rules(settlement_rules:list, payment_tiers:list):
    """Saves the current rules in json format"""
    data:dict = {
        "settlement_rules": [_rule_to_dict(rule) for rule in settlement_rules],
        "payment_tiers":    [_tier_to_dict(tier) for tier in payment_tiers],
        }
    os.makedirs(os.path.dirname(RULES_PATH), exist_ok=True)
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_rule(settlement_rules:list, prefix:str) -> SettlementRule | None:
    """Returns rule based on prefix"""
    prefix_upper = prefix.upper()
    for rule in settlement_rules:
        if prefix_upper.startswith(rule.prefix):
            return rule
    return None


def get_payment_tier(payment_tier:list, settlement: float) -> PaymentTier | None:
    """Returns threshold based on settlement."""
    for tier in payment_tier:
        if tier.min_settlement <= settlement <= tier.max_settlement:
            return tier
    return None

    

    # ── Edición ────────────────────────────────────────

    # def update_rule(self, updated_rule: SettlementRule):
    #     """Reemplaza una regla existente por prefix. Si no existe, la agrega."""
    #     for i, rule in enumerate(self.settlement_rules):
    #         if rule.prefix == updated_rule.prefix:
    #             self.settlement_rules[i] = updated_rule
    #             return
    #     self.settlement_rules.append(updated_rule)

    # def delete_rule(self, prefix: str):
    #     """Elimina la regla con el prefix dado."""
    #     self.settlement_rules = [r for r in self.settlement_rules if r.prefix != prefix]

    # def update_tier(self, index: int, updated_tier: PaymentTier):
    #     """Actualiza un tramo de pago por índice."""
    #     if 0 <= index < len(self.payment_tiers):
    #         self.payment_tiers[index] = updated_tier