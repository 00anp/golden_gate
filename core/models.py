from dataclasses import dataclass, field



@dataclass
class SettlementRule:
    prefix: str
    balance_threshold: float
    z_high: float
    ak_high: float
    z_low: float
    ak_low: float
    review_column: int | None = None
    z_greater_than_threshold: bool = False
    z_lower_than_threshold: bool = False
    mark_am: bool = False
    mark_aq: bool = False
    copy_z_to_ak: bool = False
    value_to_review: str = ""
    description: str = ""


@dataclass
class PaymentTier:
    min_settlement: float
    max_settlement: float
    min_payment: float
    max_term_default: int
    max_term_lpl: int


@dataclass
class CompanyPassword:
    company: str
    password: str = ""
    requires_password: bool = False

@dataclass
class ProcessResult:
    success: bool
    total_rows: int = 0
    files_created: int = 0
    companies_found: list = field(default_factory=list)
    created_files: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    duration_seconds: float =  0.0