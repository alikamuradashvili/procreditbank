from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from support.scenario import Bank, BankMethodUnavailable


class BankVerificationPage(BasePage):
    OPTIONS = (By.CSS_SELECTOR, 'input[name="bank"]')
    CONTINUE = (By.CSS_SELECTOR, 'button[type="submit"]')
    OTP = (By.NAME, 'otpCode')
    BOG_MESSAGE = (By.XPATH, "//*[normalize-space()='კოდი გაგზავნილია საქართველოს ბანკში რეგისტრირებულ ნომერზე' and not(*)]")
    PRIVATE_ADDRESS = (By.NAME, 'legalAddress')

    def assert_loaded(self):
        self.assert_route('ident.procreditbank.ge', '/loan-application/identification')
        self.visible(self.OPTIONS)
        self.visible(self.CONTINUE)
        return self

    def select_bank(self, bank):
        self.assert_loaded()
        if bank in (Bank.BOG, Bank.TBC, Bank.IDENTOMAT):
            locator = (By.CSS_SELECTOR, f'input[name="bank"][value="{bank.value}"]')
            element = self.visible(locator)
        else:
            # ProCredit was not present in the observed list. Do not substitute
            # Identomat (video identification) or invent a radio value.
            matches = {}
            labels = self.driver.find_elements(By.TAG_NAME, 'label')
            for label in labels:
                text = label.text.casefold()
                if not label.is_displayed() or not any(
                    name in text for name in ('პროკრედიტ', 'procredit', 'pro credit')
                ):
                    continue
                target_id = label.get_attribute('for')
                inputs = (self.driver.find_elements(By.ID, target_id) if target_id
                          else label.find_elements(By.CSS_SELECTOR, 'input[name="bank"]'))
                for candidate in inputs:
                    if candidate.get_attribute('name') == 'bank':
                        matches[candidate.id] = candidate
            if not matches:
                available = [e.get_attribute('value') for e in self.driver.find_elements(*self.OPTIONS)]
                raise BankMethodUnavailable(
                    f'ProCredit verification option was not found. Available bank radio values: {available}. '
                    'Identomat is a separate verification method and is not substituted for ProCredit.')
            if len(matches) > 1:
                raise AssertionError('Multiple distinct ProCredit verification options matched the labels.')
            element = next(iter(matches.values()))
        if not element.is_selected():
            self.click_element(element)
        self.wait.until(lambda _: element.is_selected(), 'Requested bank was not selected.')
        selected = [e for e in self.driver.find_elements(*self.OPTIONS) if e.is_selected()]
        assert len(selected) == 1 and selected[0] == element, 'Selected bank does not match the requested bank.'
        self.assert_enabled(self.CONTINUE, 'Bank choice Continue')
        return self

    def confirm_bog(self, sms):
        selected = self.driver.find_element(By.CSS_SELECTOR, 'input[name="bank"][value="bog"]')
        if not selected.is_selected():
            raise AssertionError('BOG must be selected before requesting its OTP.')
        sms.arm()
        self.click(self.CONTINUE)
        self.visible(self.BOG_MESSAGE)
        self.assert_hidden(self.OPTIONS, 'Bank selection controls')
        field = self.wait.until(EC.element_to_be_clickable(self.OTP))
        code = sms.wait_for_code(length=4)
        field.clear()
        field.send_keys(code)
        if field.get_attribute('value') != code:
            raise AssertionError('Bank OTP entry failed.')
        self.assert_enabled(self.CONTINUE, 'BOG OTP confirmation')
        self.click(self.CONTINUE)
        # The bank response can take longer than the generic element timeout.
        self.visible(self.PRIVATE_ADDRESS)
        self.assert_route('ident.procreditbank.ge', '/loan-application/private-information')
        self.assert_hidden(self.OTP, 'Bank OTP input')
        return self
