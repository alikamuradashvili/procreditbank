from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException, StaleElementReferenceException, TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, timeout=25):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def visible(self, locator):
        return self.assert_condition(EC.visibility_of_element_located(locator),
                                     f'Expected visible element: {locator}')

    def assert_condition(self, condition, message):
        try:
            return self.wait.until(condition, message)
        except TimeoutException:
            raise AssertionError(message) from None

    def assert_route(self, host, path):
        try:
            self.assert_condition(lambda driver: (
                urlparse(driver.current_url).hostname == host
                and urlparse(driver.current_url).path.rstrip('/') == path.rstrip('/')
            ), f'Expected page: {host}{path}')
        except AssertionError:
            actual = urlparse(self.driver.current_url)
            # Exclude query strings and fragments, which may contain tokens.
            raise AssertionError(
                f'Expected page: {host}{path}; actual: {actual.hostname}{actual.path}'
            ) from None
        return self

    def assert_value(self, locator, expected, label):
        self.assert_condition(lambda driver: driver.find_element(*locator).get_attribute('value') == expected,
                              f'{label}: entered value does not match.')
        return self

    def assert_selected(self, locator, selected, label):
        self.assert_condition(EC.element_located_selection_state_to_be(locator, selected),
                              f'{label}: unexpected selection state.')
        return self

    def assert_enabled(self, locator, label):
        self.assert_condition(EC.element_to_be_clickable(locator), f'{label}: not ready for interaction.')
        return self

    def assert_hidden(self, locator, label):
        self.assert_condition(EC.invisibility_of_element_located(locator), f'{label}: still visible.')
        return self

    def _click_visible(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});", element)
            ready = self.driver.execute_script("""
                const e=arguments[0], r=e.getBoundingClientRect();
                const top=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
                return top && (top===e || e.contains(top));
            """, element)
            if not ready or not element.is_enabled():
                return False
            element.click()
            return True
        except (ElementClickInterceptedException, StaleElementReferenceException):
            return False

    def click_element(self, element):
        self.wait.until(lambda _: self._click_visible(element))

    def click(self, locator):
        self.wait.until(lambda _: self._click_first_visible(locator))

    def _click_first_visible(self, locator):
        elements = self.visible_elements(locator)
        return bool(elements) and self._click_visible(elements[0])

    def fill(self, locator, value):
        field = self.visible(locator)
        field.clear()
        field.send_keys(value)
        self.assert_value(locator, str(value), 'Input field')

    def visible_elements(self, locator):
        try:
            return [e for e in self.driver.find_elements(*locator) if e.is_displayed()]
        except StaleElementReferenceException:
            return []
