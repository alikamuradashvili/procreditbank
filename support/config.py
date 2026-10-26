import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv


@dataclass(frozen=True)
class LoanData:
    personal_id: str
    amount: str
    term_months: str
    purpose: str
    currency: str

    def __post_init__(self):
        if not (self.personal_id.isascii() and self.personal_id.isdigit()
                and len(self.personal_id) == 11):
            raise ValueError('PERSONAL_ID must contain exactly 11 ASCII digits.')
        if not self.amount.isascii() or not self.amount.isdigit() or int(self.amount) <= 0:
            raise ValueError('LOAN_AMOUNT must be a positive integer.')
        if not self.term_months.isdigit() or not 3 <= int(self.term_months) <= 120:
            raise ValueError('LOAN_TERM_MONTHS must be between 3 and 120.')
        if self.purpose not in {'1', '2', '4'}:
            raise ValueError('LOAN_PURPOSE must be 1 (consumer), 2 (mortgage), or 4 (auto).')
        if self.currency not in {'GEL', 'USD', 'EUR'}:
            raise ValueError('Unsupported currency.')


@dataclass(frozen=True)
class Settings:
    base_url: str
    wait_timeout: int
    manual_timeout: int
    headless: bool

    @classmethod
    def from_env(cls):
        load_dotenv()
        base_url = os.getenv('BASE_URL', 'https://www.procreditbank.ge/')
        if urlparse(base_url).scheme not in {'http', 'https'}:
            raise ValueError('BASE_URL must be an HTTP(S) URL.')
        return cls(base_url, int(os.getenv('WAIT_TIMEOUT', '25')),
                   int(os.getenv('MANUAL_TIMEOUT', '300')),
                   os.getenv('HEADLESS', 'false').lower() == 'true')


def loan_data_from_env():
    return LoanData(os.getenv('PERSONAL_ID', ''), os.getenv('LOAN_AMOUNT', '50000'),
                    os.getenv('LOAN_TERM_MONTHS', '48'), os.getenv('LOAN_PURPOSE', '1'),
                    os.getenv('LOAN_CURRENCY', 'GEL'))
