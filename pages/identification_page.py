from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class IdentificationPage(BasePage):
    PERSONAL_ID = (By.NAME, 'personalId')
    MOBILE = (By.NAME, 'mobileNumber')
    PRIVACY = (By.NAME, 'acceptPrivacy')
    MARKETING = (By.XPATH, "//span[normalize-space()='მარკეტინგული მიზნებისათვის მონაცემების დამუშავებას']/../preceding-sibling::div")
    CONTINUE = (By.CSS_SELECTOR, 'button[type="submit"]')
    OTP = (By.NAME, 'otpCode')

    def switch_to_new_window(self, previous_handles):
        self.wait.until(EC.new_window_is_opened(previous_handles))
        new_handles = set(self.driver.window_handles) - set(previous_handles)
        assert len(new_handles) == 1, 'Expected one identification window.'
        self.driver.switch_to.window(new_handles.pop())
        self.wait.until(lambda d: urlparse(d.current_url).hostname == 'ident.procreditbank.ge')
        self.visible(self.PERSONAL_ID)
        self.assert_route('ident.procreditbank.ge', '/loan-application/identification')
        self.visible(self.MOBILE)
        self.visible(self.PRIVACY)
        self.visible(self.CONTINUE)
        return self

    def fill_details(self, personal_id, mobile):
        self.fill(self.PERSONAL_ID, personal_id)
        self.fill(self.MOBILE, mobile)
        self.assert_value(self.PERSONAL_ID, personal_id, 'Personal ID')
        self.assert_value(self.MOBILE, mobile, 'Mobile number')
        return self

    def accept_consents(self, *, explicitly_authorized=False, marketing=False):
        if not explicitly_authorized:
            raise RuntimeError('Explicit authorization is required for identification and marketing consents.')
        if not self.visible(self.PRIVACY).is_selected():
            self.click(self.PRIVACY)
        self.assert_selected(self.PRIVACY, True, 'Identity privacy consent')
        if not hasattr(self, '_marketing_unchecked_class'):
            self._marketing_unchecked_class = self.visible(self.MARKETING).get_attribute('class')
        # This custom toggle has no input/ARIA checked state. On a fresh form it
        # starts unchecked; verify the visual state class changes after one click.
        if getattr(self, '_marketing_selected', False) != marketing:
            toggle = self.visible(self.MARKETING)
            before = toggle.get_attribute('class')
            self.click(self.MARKETING)
            self.wait.until(lambda _: self.visible(self.MARKETING).get_attribute('class') != before)
            self._marketing_selected = marketing
        self.assert_condition(
            lambda _: (self.visible(self.MARKETING).get_attribute('class')
                       != self._marketing_unchecked_class) == marketing,
            'Marketing toggle does not match the requested visual state.')
        self.assert_enabled(self.CONTINUE, 'Identity details Continue')
        return self

    def request_and_fill_otp(self, sms):
        # Capture the message watermark immediately before requesting a new code.
        sms.arm()
        self.click(self.CONTINUE)
        self.wait.until(EC.element_to_be_clickable(self.OTP))
        self.assert_hidden(self.PERSONAL_ID, 'Identity details form')
        code = sms.wait_for_code(length=6)
        field = self.wait.until(EC.element_to_be_clickable(self.OTP))
        field.clear()
        field.send_keys(code)
        if field.get_attribute('value') != code:
            raise AssertionError('OTP entry failed.')
        self.assert_enabled(self.CONTINUE, 'Initial OTP confirmation')
        return self

    def confirm_otp(self):
        self.click(self.CONTINUE)
        self.visible((By.CSS_SELECTOR, 'input[name="bank"]'))
        self.assert_hidden(self.OTP, 'Initial OTP input')
        return self
