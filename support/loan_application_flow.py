from pages.home_page import HomePage
from pages.identification_page import IdentificationPage
from pages.bank_verification_page import BankVerificationPage
from pages.personal_information_page import PersonalInformationPage
from pages.loan_consents_page import LoanConsentsPage
from support.android_sms import AndroidSmsOtp
from support.scenario import EndPoint


class LoanApplicationFlow:
    """One reusable entry point; page objects own UI actions and assertions."""

    def __init__(self, driver, settings):
        self.driver = driver
        self.settings = settings

    def fill_application(self, loan, mobile, scenario, *, same_address=True, is_pep=False):
        if scenario.end_at == EndPoint.COMPLETED and (not same_address or is_pep):
            raise NotImplementedError('This personal-information branch has not been inspected.')
        application = (HomePage(self.driver, self.settings.wait_timeout)
                       .open(self.settings.base_url).open_consumer_loan().open_application())
        application.fill_loan_details(loan)
        application.assert_loan_details(loan)
        previous_handles = set(self.driver.window_handles)
        application.continue_to_identification()
        identification = IdentificationPage(self.driver, self.settings.wait_timeout)
        identification.switch_to_new_window(previous_handles)
        identification.fill_details(loan.personal_id, mobile)
        identification.accept_consents(explicitly_authorized=True, marketing=scenario.marketing)
        identification.request_and_fill_otp(AndroidSmsOtp(timeout=45))
        identification.confirm_otp()

        bank_page = BankVerificationPage(self.driver, max(60, self.settings.wait_timeout))
        bank_page.select_bank(scenario.bank)
        if scenario.end_at == EndPoint.BANK_SELECTION:
            return EndPoint.BANK_SELECTION

        bank_sms = AndroidSmsOtp(
            timeout=45, marker='კომპანია Keepz.me LLC ითხოვს შენს ინფორმაციას',
            sender='', code_label='ერთჯერადი კოდი')
        bank_page.confirm_bog(bank_sms)
        (PersonalInformationPage(self.driver, self.settings.wait_timeout)
         .fill_details(same_address=same_address, is_pep=is_pep).continue_to_consents())
        (LoanConsentsPage(self.driver, max(60, self.settings.wait_timeout))
         .set_consents(scenario.consents).continue_to_success().assert_loaded())
        return EndPoint.COMPLETED
