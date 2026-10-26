from dataclasses import dataclass
from enum import Enum


class Bank(str, Enum):
    BOG = 'bog'
    TBC = 'tbc'
    PROCREDIT = 'procredit'


class EndPoint(str, Enum):
    BANK_SELECTION = 'bank_selection'
    COMPLETED = 'completed'


@dataclass(frozen=True)
class Consents:
    future_offers: bool = False
    revenue_check: bool = True
    credit_bureau: bool = True
    remittance_income: bool = True


@dataclass(frozen=True)
class Scenario:
    bank: Bank
    end_at: EndPoint
    marketing: bool = False
    consents: Consents = Consents()

    def __post_init__(self):
        if self.end_at == EndPoint.COMPLETED and self.bank != Bank.BOG:
            raise ValueError('Only the BOG completion flow has been inspected.')


class BankMethodUnavailable(RuntimeError):
    """Requested bank is not exposed by the verification-method page."""
