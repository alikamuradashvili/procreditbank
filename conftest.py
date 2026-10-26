import os

import pytest
from selenium import webdriver

from support.config import Settings, loan_data_from_env
from support.loan_application_flow import LoanApplicationFlow


def pytest_addoption(parser):
    parser.addoption('--live', action='store_true', help='Enable real bank browser interaction.')
    parser.addoption('--complete-application', action='store_true',
                     help='Enable the BOG case including all configured consents and final submission.')


@pytest.fixture(scope='session')
def settings():
    return Settings.from_env()


@pytest.fixture
def loan_data(settings):
    return loan_data_from_env()


@pytest.fixture
def applicant(settings):
    mobile = os.getenv('MOBILE_NUMBER', '')
    if not (len(mobile) == 9 and mobile.isascii() and mobile.isdigit() and mobile.startswith('5')):
        raise pytest.UsageError('Set MOBILE_NUMBER to a 9-digit Georgian mobile number.')
    return {'mobile': mobile}


@pytest.fixture(autouse=True)
def live_gate(request):
    if request.node.get_closest_marker('live'):
        if not request.config.getoption('--live'):
            pytest.skip('Use --live to run bank UI cases.')


@pytest.fixture
def driver(settings, loan_data, applicant):
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    if settings.headless:
        options.add_argument('--headless=new')
    browser = webdriver.Chrome(options=options)
    try:
        if not settings.headless:
            browser.maximize_window()
        browser.set_page_load_timeout(60)
        browser.implicitly_wait(0)
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def application_flow(driver, settings):
    return LoanApplicationFlow(driver, settings)
