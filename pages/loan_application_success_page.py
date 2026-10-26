from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class LoanApplicationSuccessPage(BasePage):
    TITLE = (By.XPATH, "//span[normalize-space()='დასრულებულია წარმატებით!']")
    COMPLETION = (By.XPATH, "//div[normalize-space()='იდენტიფიკაციის და განაცხადის შევსების პროცესი დასრულებულია.' and not(*)]")
    CONTACT = (By.XPATH, "//div[normalize-space()='დაელოდე ბანკისგან დაკავშირებას.' and not(*)]")
    CONSENT = (By.NAME, 'consentDataVerification')
    SUBMIT = (By.CSS_SELECTOR, 'button[type="submit"]')

    def assert_loaded(self):
        self.wait.until(lambda driver: (
            urlparse(driver.current_url).hostname == 'ident.procreditbank.ge'
            and urlparse(driver.current_url).path.rstrip('/') == '/loan-application/about-services'
        ), 'Expected the completion route.')
        # Success is rendered on the SAME URL as the preceding form.
        for locator in (self.TITLE, self.COMPLETION, self.CONTACT):
            self.visible(locator)
        for locator in (self.CONSENT, self.SUBMIT):
            self.wait.until(EC.invisibility_of_element_located(locator),
                            'The application form is still visible.')
        return self
