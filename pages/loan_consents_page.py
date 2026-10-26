from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from pages.loan_application_success_page import LoanApplicationSuccessPage


class LoanConsentsPage(BasePage):
    FIELDS = {
        'future_offers': (By.NAME, 'consentDataFutureOffers'),
        'revenue_check': (By.NAME, 'consentDataVerificationLepl'),
        'credit_bureau': (By.NAME, 'consentDataVerification'),
        'remittance_income': (By.NAME, 'consentDataIncomeRemittance'),
    }
    CONTINUE = (By.CSS_SELECTOR, 'button[type="submit"]')

    def set_consents(self, choices):
        url = urlparse(self.driver.current_url)
        if url.hostname != 'ident.procreditbank.ge' or url.path.rstrip('/') != '/loan-application/about-services':
            raise AssertionError('Expected the loan consent form.')
        for name, locator in self.FIELDS.items():
            desired = getattr(choices, name)
            if self.visible(locator).is_selected() != desired:
                self.click(locator)
            self.wait.until(EC.element_located_selection_state_to_be(locator, desired))
        # Check the complete state again to catch controls that reset each other.
        for name, locator in self.FIELDS.items():
            self.assert_selected(locator, getattr(choices, name), f'Loan consent: {name}')
        self.assert_enabled(self.CONTINUE, 'Loan consents Continue')
        return self

    def continue_to_success(self):
        self.click(self.CONTINUE)
        return LoanApplicationSuccessPage(self.driver, self.timeout)
