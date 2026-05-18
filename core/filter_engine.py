import datetime
from core.helpers import safe_float, safe_str
from core.rules_engine import get_rule, load_rules

# Column index constants
COL_BALANCE  = 12   # L — gmc_current0
COL_STATUS   = 13   # M — gmc_status
COL_CUSTOMER = 17   # Q — gmc_customer
COL_LASTPAID = 20   # T — gmc_lastpaid
COL_NSFDATE  = 24   # X — gmc_NSFDate

RECENT_PAYMENT_DAYS   = 31
LOW_BALANCE_THRESHOLD = 100


def get_pdc_pcc_rows(ws) -> list[int]:
    """Returns row numbers where col M value is PDC or PCC."""
    flagged = []
    for i in range(2, ws.max_row + 1):
        status = safe_str(ws.cell(i, COL_STATUS).value)
        if status in {"PDC", "PCC"}:
            flagged.append(i)
    return flagged


def get_prm_ppa_recent_rows(ws) -> list[int]:
    """Returns rows where col M is PRM or PPA AND gmc_lastpaid (col T)
    is within 31 days of gmc_NSFDate (col X).
    If NSFDate is empty, use today as reference."""
    flagged = []
    for i in range(2, ws.max_row + 1):
        status = safe_str(ws.cell(i, COL_STATUS).value)
        if status not in {"PRM", "PPA"}:
            continue

        lastpaid = ws.cell(i, COL_LASTPAID).value
        nsfdate  = ws.cell(i, COL_NSFDATE).value

        if lastpaid is None or not isinstance(lastpaid, (datetime.date, datetime.datetime)):
            continue

        if isinstance(nsfdate, datetime.datetime):
            reference = nsfdate.date()
        elif isinstance(nsfdate, datetime.date):
            reference = nsfdate
        else:
            reference = datetime.date.today()

        lastpaid_date = lastpaid.date() if isinstance(lastpaid, datetime.datetime) else lastpaid
        delta = (reference - lastpaid_date).days

        if delta <= RECENT_PAYMENT_DAYS:
            flagged.append(i)
    return flagged


def get_low_balance_rows(ws) -> list[int]:
    """Returns rows where col L balance < 100."""
    flagged = []
    for i in range(2, ws.max_row + 1):
        balance = safe_float(ws.cell(i, COL_BALANCE).value)
        if balance < LOW_BALANCE_THRESHOLD:
            flagged.append(i)
    return flagged


def get_all_flagged_rows(ws) -> dict:
    """Aggregates all 3 criteria into a single dict.
    Keys map to their respective row lists.
    Rows can appear in more than one category."""
    return {
        "pdc_pcc":     get_pdc_pcc_rows(ws),
        "prm_ppa":     get_prm_ppa_recent_rows(ws),
        "low_balance": get_low_balance_rows(ws),
    }


def get_row_preview(ws, row_index: int) -> dict:
    """Returns a small dict with display values for a single row.
    Used by the UI to render each flagged row in a table."""
    return {
        "row":      row_index,
        "company":  safe_str(ws.cell(row_index, 1).value),
        "status":   safe_str(ws.cell(row_index, COL_STATUS).value),
        "balance":  safe_float(ws.cell(row_index, COL_BALANCE).value),
        "customer": safe_str(ws.cell(row_index, COL_CUSTOMER).value),
        "lastpaid": ws.cell(row_index, COL_LASTPAID).value,
        "nsfdate":  ws.cell(row_index, COL_NSFDATE).value,
    }


def get_prefix_analysis(ws, settlement_rules) -> list[dict]:
    """Reads col Q, counts occurrences per unique raw value,
    checks if a matching rule exists for each prefix.
    Returns list sorted: no-rule first, then by count desc."""
    counts: dict[str, int] = {}
    for i in range(2, ws.max_row + 1):
        value = safe_str(ws.cell(i, COL_CUSTOMER).value)
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1

    result = []
    for prefix_raw, count in counts.items():
        rule = get_rule(settlement_rules, prefix_raw)
        result.append({
            "prefix":      prefix_raw,
            "count":       count,
            "has_rule":    rule is not None,
            "rule_prefix": rule.prefix if rule else "",
        })

    # Sort: no-rule entries first, then descending count
    result.sort(key=lambda x: (x["has_rule"], -x["count"]))
    return result