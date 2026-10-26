from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class PersonalInformationPage(BasePage):
    ADDRESS = (By.NAME, 'legalAddress')
    DIFFERENT_ADDRESS = (By.NAME, 'isActualAddressDifferent')
    NOT_PEP = (By.CSS_SELECTOR, 'input[name="isPep"][value="2"]')
    CONTINUE = (By.CSS_SELECTOR, 'button[type="submit"]')

    def fill_details(self, *, same_address, is_pep):
        # Other branches expose extra fields that have not yet been inspected.
        if not same_address or is_pep:
            raise NotImplementedError('Different-address and PEP-detail fields need inspection first.')
        self.assert_route('ident.procreditbank.ge', '/loan-application/private-information')
        address = self.visible(self.ADDRESS)
        if not address.get_attribute('value'):
            raise AssertionError('The verified legal address was not populated.')
        if self.visible(self.DIFFERENT_ADDRESS).is_selected():
            self.click(self.DIFFERENT_ADDRESS)
        self.wait.until(EC.element_located_selection_state_to_be(self.DIFFERENT_ADDRESS, False))
        if not self.visible(self.NOT_PEP).is_selected():
            self.click(self.NOT_PEP)
        self.wait.until(EC.element_located_selection_state_to_be(self.NOT_PEP, True))
        self.assert_selected(self.DIFFERENT_ADDRESS, False, 'Same legal and actual address')
        self.assert_selected(self.NOT_PEP, True, 'Not politically exposed')
        self.assert_enabled(self.CONTINUE, 'Personal information Continue')
        return self

    def continue_to_consents(self):
        self.click(self.CONTINUE)
        self.wait.until(lambda driver: urlparse(driver.current_url).path.rstrip('/')
                        == '/loan-application/about-services')
        self.assert_route('ident.procreditbank.ge', '/loan-application/about-services')
        self.visible((By.NAME, 'consentDataVerification'))
        self.assert_hidden(self.ADDRESS, 'Personal information form')
        return self
