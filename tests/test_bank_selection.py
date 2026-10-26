from unittest.mock import Mock

import pytest
from selenium.webdriver.common.by import By

from pages.bank_verification_page import BankVerificationPage
from support.scenario import Bank, BankMethodUnavailable


def test_missing_procredit_is_failure_with_available_methods(monkeypatch):
    options = []
    for value in ('bog', 'tbc', 'Identomat'):
        option = Mock()
        option.get_attribute.return_value = value
        options.append(option)
    driver = Mock()
    driver.find_elements.side_effect = lambda by, value: [] if by == By.TAG_NAME else options
    page = BankVerificationPage(driver, timeout=0)
    monkeypatch.setattr(page, 'assert_loaded', lambda: page)
    with pytest.raises(BankMethodUnavailable, match='Available bank radio values') as error:
        page.select_bank(Bank.PROCREDIT)
    assert isinstance(error.value, AssertionError)
    driver.execute_script.assert_not_called()


def test_duplicate_labels_for_same_radio_are_not_ambiguous(monkeypatch):
    radio = Mock()
    radio.id = 'one-radio'
    radio.get_attribute.return_value = 'bank'
    radio.is_selected.return_value = True
    labels = []
    for text in ('PROCREDIT', 'პროკრედიტ ბანკი'):
        label = Mock()
        label.text = text
        label.is_displayed.return_value = True
        label.get_attribute.return_value = 'procredit-option'
        labels.append(label)
    driver = Mock()
    driver.find_elements.side_effect = lambda by, value: labels if by == By.TAG_NAME else [radio]
    page = BankVerificationPage(driver, timeout=0)
    monkeypatch.setattr(page, 'assert_loaded', lambda: page)
    monkeypatch.setattr(page, 'assert_enabled', lambda *args: page)
    assert page.select_bank(Bank.PROCREDIT) is page
    radio.click.assert_not_called()
