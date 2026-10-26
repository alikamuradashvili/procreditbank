from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from pages.base_page import BasePage


def test_value_mismatch_has_safe_error_message():
    element = Mock()
    element.get_attribute.return_value = 'actual-sensitive-value'
    driver = Mock()
    driver.find_element.return_value = element
    with pytest.raises(AssertionError) as error:
        BasePage(driver, timeout=0).assert_value(('name', 'otpCode'), 'expected-secret', 'OTP')
    assert str(error.value) == 'OTP: entered value does not match.'


@pytest.mark.parametrize('actual', [False, True])
def test_selection_assertion_checks_requested_state(actual):
    element = Mock()
    element.is_selected.return_value = actual
    driver = Mock()
    driver.find_element.return_value = element
    page = BasePage(driver, timeout=0)
    page.assert_selected(('name', 'consent'), actual, 'Consent')
    with pytest.raises(AssertionError, match='unexpected selection'):
        page.assert_selected(('name', 'consent'), not actual, 'Consent')


@pytest.mark.parametrize('url', [
    'https://unexpected.example/loan-application/about-services',
    'https://ident.procreditbank.ge/loan-application/identification',
])
def test_route_assertion_rejects_wrong_host_or_stage(url):
    driver = SimpleNamespace(current_url=url)
    with pytest.raises(AssertionError, match='Expected page'):
        BasePage(driver, timeout=0).assert_route(
            'ident.procreditbank.ge', '/loan-application/about-services')


def test_route_assertion_accepts_trailing_slash_and_query():
    driver = SimpleNamespace(current_url='https://ident.procreditbank.ge/loan-application/about-services/?lang=ge')
    page = BasePage(driver, timeout=0)
    assert page.assert_route('ident.procreditbank.ge', '/loan-application/about-services') is page


def test_loan_application_accepts_observed_host_without_www(monkeypatch):
    from pages.loan_application_page import LoanApplicationPage
    driver = SimpleNamespace(current_url='https://procreditbank.ge/ge/consumer-loan-application')
    page = LoanApplicationPage(driver, timeout=0)
    monkeypatch.setattr(page, 'visible', lambda locator: object())
    assert page.assert_loaded() is page


def test_route_failure_reports_actual_path_without_tokens():
    driver = SimpleNamespace(current_url='https://wrong.example/failed?token=private#secret')
    with pytest.raises(AssertionError) as error:
        BasePage(driver, timeout=0).assert_route('procreditbank.ge', '/ge/consumer-loan-application')
    assert 'actual: wrong.example/failed' in str(error.value)
    assert 'private' not in str(error.value)
    assert 'secret' not in str(error.value)
