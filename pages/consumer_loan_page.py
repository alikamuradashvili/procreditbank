from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from pages.loan_application_page import LoanApplicationPage


class ConsumerLoanPage(BasePage):
    HEADING = (By.XPATH, '//h3[normalize-space()="სამომხმარებლო სესხი"]')
    APPLICATION = (By.CSS_SELECTOR, 'a[href$="/ge/consumer-loan-application"]')

    def assert_loaded(self):
        self.assert_route('www.procreditbank.ge', '/ge/samomkhmareblo-seskhi')
        self.visible(self.HEADING)
        self.assert_enabled(self.APPLICATION, 'Open loan application')
        return self

    def open_application(self):
        previous = set(self.driver.window_handles)
        self.click(self.APPLICATION)
        self.wait.until(EC.new_window_is_opened(previous))
        new_handles = set(self.driver.window_handles) - previous
        assert len(new_handles) == 1, 'Expected exactly one application tab.'
        self.driver.switch_to.window(new_handles.pop())
        self.wait.until(EC.url_contains('/ge/consumer-loan-application'))
        page = LoanApplicationPage(self.driver, self.timeout)
        page.assert_loaded()
        return page
