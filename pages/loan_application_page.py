from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoanApplicationPage(BasePage):
    CONTINUE = (By.CSS_SELECTOR, '#step1 button[onclick="nextStep(event)"]')
    FORM = (By.ID, 'multiStepForm')
    PERSONAL_ID = (By.ID, 'id')
    PURPOSE = (By.ID, 'selected-option')
    AMOUNT = (By.ID, 'money')
    TERM = (By.ID, 'period')
    CURRENCY_PICKER = (By.CSS_SELECTOR, '#currency-select > .selected-option')
    CURRENCY_VALUE = (By.ID, 'currency')
    OTP_INPUTS = (By.CSS_SELECTOR, '#otp-container .otp-input')
    OTP_MODAL = (By.ID, 'pinModal')

    def assert_loaded(self):
        self.assert_route('procreditbank.ge', '/ge/consumer-loan-application')
        self.visible(self.FORM)
        self.visible(self.PERSONAL_ID)
        self.visible(self.CONTINUE)
        return self

    def fill_loan_details(self, data):
        self.fill(self.PERSONAL_ID, data.personal_id)
        self.click(self.PURPOSE)
        self.click((By.CSS_SELECTOR, f'#dropdown-options .option[data-value="{data.purpose}"]'))
        expected_purpose = {'1': 'სამომხმარებლო', '2': 'იპოთეკური', '4': 'ავტო'}[data.purpose]
        self.assert_condition(lambda _: self.visible(self.PURPOSE).text.strip() == expected_purpose,
                              'Loan purpose was not selected.')
        self.fill(self.AMOUNT, data.amount)
        self.click(self.CURRENCY_PICKER)
        self.click((By.CSS_SELECTOR, f'#currency-select .option[data-value="{data.currency}"]'))
        self.assert_value(self.CURRENCY_VALUE, data.currency, 'Loan currency')
        self.fill(self.TERM, data.term_months)
        return self

    def assert_loan_details(self, data):
        # Assertion messages deliberately exclude personal data.
        for locator, expected in ((self.PERSONAL_ID, data.personal_id),
                                  (self.AMOUNT, data.amount), (self.TERM, data.term_months)):
            assert self.visible(locator).get_attribute('value') == expected, 'Field value mismatch.'
        assert self.driver.find_element(*self.CURRENCY_VALUE).get_attribute('value') == data.currency
        purpose = self.visible(self.PURPOSE).text.strip()
        assert purpose == {'1': 'სამომხმარებლო', '2': 'იპოთეკური', '4': 'ავტო'}[data.purpose]

    def continue_to_identification(self):
        """Advance loan details; identity checks and legal consents remain user-operated."""
        self.click(self.CONTINUE)
        def transitioned(_):
            errors = self.visible_elements((By.ID, 'apiErrorModal'))
            if errors:
                raise AssertionError('Bank rejected the request; inspect the error in the browser.')
            fetch_errors = self.visible_elements((By.ID, 'fetchError'))
            if any(e.text.strip() for e in fetch_errors):
                raise AssertionError('Bank request failed; inspect the error in the browser.')
            return not self.visible_elements(self.FORM)
        self.wait.until(transitioned)
        return self

    def wait_for_otp(self, timeout):
        from selenium.webdriver.support.ui import WebDriverWait

        return WebDriverWait(self.driver, timeout).until(
            lambda _: self.visible_elements(self.OTP_INPUTS))

    def fill_otp(self, code):
        fields = self.visible_elements(self.OTP_INPUTS)
        if not fields or len(code) != len(fields) or not code.isascii() or not code.isdigit():
            raise ValueError('SMS code must contain one digit per visible OTP field.')
        for field, digit in zip(fields, code, strict=True):
            field.clear()
            field.send_keys(digit)
        assert ''.join(f.get_attribute('value') for f in fields) == code, 'OTP entry failed.'
