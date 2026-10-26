import pytest

from support.scenario import Bank, Consents, EndPoint, Scenario


def fill_loan_application(request, *, bank, end_at,
                          marketing=False, future_offers=False,
                          revenue_check=True, credit_bureau=True,
                          remittance_income=True,
                          same_address=True, is_pep=False):
    """One shared scenario, configured by each named test's arguments."""
    scenario = Scenario(
        bank=bank, end_at=end_at, marketing=marketing,
        consents=Consents(future_offers=future_offers, revenue_check=revenue_check,
                          credit_bureau=credit_bureau,
                          remittance_income=remittance_income))
    if end_at == EndPoint.COMPLETED:
        if not request.config.getoption('--complete-application'):
            pytest.skip('Use --complete-application to enable full BOG submission.')
        if not same_address or is_pep:
            raise pytest.UsageError('Additional address/PEP fields need inspection first.')
    flow = request.getfixturevalue('application_flow')
    loan = request.getfixturevalue('loan_data')
    applicant = request.getfixturevalue('applicant')
    result = flow.fill_application(
        loan, applicant['mobile'], scenario,
        same_address=same_address, is_pep=is_pep)
    assert result == end_at


@pytest.mark.live
class TestConsumerLoanApplication:

    def test_01_loan_application_otp_bog_complete(self, request):
        fill_loan_application(
            request, bank=Bank.BOG, end_at=EndPoint.COMPLETED,
            marketing=True, future_offers=True,
            same_address=True, is_pep=False)

    def test_02_loan_application_otp_tbc_selection(self, request):
        fill_loan_application(
            request, bank=Bank.TBC, end_at=EndPoint.BANK_SELECTION)

    def test_03_loan_application_otp_identomat_selection(self, request):
        fill_loan_application(
            request, bank=Bank.IDENTOMAT, end_at=EndPoint.BANK_SELECTION)
