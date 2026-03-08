import math
from openpyxl.utils import column_index_from_string

HEADERS:dict = {
    "A": "DSC",
    "B": "DSC_Column1",
    "C": "DSC_Column2",
    "F": "GMC Ref#",
    "G": "FirstName",
    "H": "LastName",
    "I": "SSN",
    "J": "OriginalCreditor",
    "K": "OriginalCreditorAccount#",
    "L": "Balance",
    "M": "Settlement",
    "N": "Min Payment",
    "O": "Max Term",
    "AK": "%",
    "AL": "Lump Sum Offer",
    "AM": "Pre-Litigation",
    "AN": "PreviousCreditor",
    "AO": "OpenDate",
    "AP": "2nd Acct#/CBR#",
    "AQ": "Pre-Charge Off",
}

EXPORT_COLUMNS:list = ["A", "B", "C", "F", "G", "H", "I", "J", "K", "L",
                  "M", "N", "O", "AL", "AM", "AN", "AO", "AP", "AQ"]


def safe_float(value) -> float:
    try:
        if value is None:
            return 0.0
        else:
            return float(value)
    except (ValueError, TypeError):
        return 0.0


def safe_str(value) -> str:
    if value is None:
        return ""
    else:
        return value.strip().upper()


def ceiling(value:float) -> int:
    return math.ceil(value)


def col_letter_to_index(letter: str) -> int:
    return column_index_from_string(letter)

